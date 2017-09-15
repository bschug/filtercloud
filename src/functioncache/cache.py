import logging
from datetime import datetime, timedelta
from contextlib import closing, contextmanager
import inspect

import sqlite3


logger = logging.getLogger('functioncache.cache')
logger.setLevel(logging.WARNING)
logger.setLevel(logging.DEBUG)
if len(logger.handlers) == 0:
    logger.addHandler(logging.StreamHandler())


class Cache(object):
    """
    Cache that stores the results of function calls.
    Returns cached results if they are less than <timeout> old.
    Uses an sqlite database to store cached results.

    Limitations:
     * This cache uses the function's __qualname__ to build a key.
       If this is not unique for your function (e.g. same function name  defined in multiple modules),
       functions with colliding names may return the other function's cached values.
       Override the _function_key method to provide a different way of identifying functions,
       or call get_with_key to directly specify a key (which must include the arguments).
       
     * This cache is designed for functions with a finite set of possible arguments. It does not impose
       any limits on the size of the cache. Don't use this if arguments are provided by user input or
       some other source out of your control. A malicious user may make you run out of disk space.
       
     * If you just want to cache HTTP requests, use requests_cache instead. This class is meant for caching
       expensive calculations or data that was generated based on HTTP requests (e.g. if the request returns
       very large JSONS, but you only need a tiny part of it).
    """
    def __init__(self, name, *, dbname='cache.sqlite', timeout=None, use_outdated_cache_on_error=False, gc_on_init=True):
        """
        Multiple Cache instances can share the same database.
        They can also share the same table, i.e. they are different views on the same cache.
        Make sure to only use the same name if the timeout is also the same.

        :param name:    Name of the cache. Used as the SQLite table name.
        :param dbname:  SQLite db to use for storage.
        :param timeout: Maximum age of cached entries (timedelta)
        :param gc_on_init: Garbage-collect outdated entries when initializing the Cache instance.
        :param use_outdated_cache_on_error: If function call raises an exception, and there is an outdated value
                                            still in the cache, return that instead of raising the exception.
        """
        assert timeout is not None
        self.name = name
        self.dbname = dbname
        self.timeout = timeout
        self.use_outdated_cache_on_error = use_outdated_cache_on_error
        self._init_db()
        if gc_on_init:
            self.gc()

    def get(self, function, *args, **kwargs):
        """
        Returns the cached result of the function call if it's stored in the cache.
        Otherwise, executes the function with the given arguments, stores the result and returns it.
        Note that all arguments must have a unique string representation because the database key will be constructed
        from them.

        :param function:    Function to call if data is not in cache.
        :param args:        Args to pass to the function.
        :param kwargs:      Keyword args to pass to the function.
        :return:
        """
        # Build key from function name and arguments:
        key = self._make_key(function, args, kwargs)
        return self.get_with_key(key, function, *args, **kwargs)

    def get_with_key(self, key, function, *args, **kwargs):
        """
        Same as get, but with an explicit key instead of one derived from function name and arguments.
        """
        # Use cached data if available
        cached = self.lookup_cached(key)
        if cached is not None:
            logger.debug("Returning cached version of %s", key)
            return cached
        logger.debug("No cached version found for %s", key)

        try:
            # Invoke function and store result in cache
            new_value = function(*args, **kwargs)
            self.store(key, new_value)
            return new_value
        except:
            # Function call failed, use cached value even if outdated
            cached = self.lookup_cached(key, threshold=datetime(1970, 1, 1))
            if cached is not None and self.use_outdated_cache_on_error:
                logger.debug("%s call failed, returning outdated value from cache", key)
                return self._deserialize(cached)
            raise

    def lookup_cached(self, key, *, threshold=None):
        """
        Lookup a value in the cache by key.
        If the value has never been added, or is outdated, returns None.
        If this cache overrides the _serialize method, this will return the *serialized* representation of the cached
        value.
        """
        threshold = threshold or datetime.utcnow() - self.timeout

        with self._db_cursor() as cursor:
            cursor.execute('SELECT timestamp, content FROM ' + self.name + ' WHERE key = ?', (key,))
            for timestamp, content in cursor:
                if timestamp > threshold:
                    return content
                logger.debug("Ignoring cached value of %s because it was created on %s, which is before %s",
                             key, timestamp, threshold)
        return None

    def store(self, key, value):
        """
        Store a value in the cache.
        """
        assert type(key) is str
        value = self._serialize(value)
        assert type(value) is str
        logger.debug("Storing new value for %s: %s", key, value)
        with self._db_cursor() as cursor:
            cursor.execute('INSERT OR REPLACE INTO ' + self.name + '(key, timestamp, content) ' +
                           'VALUES (?, CURRENT_TIMESTAMP, ?) ',
                           (key, value))

    def gc(self):
        """
        Delete outdated entries from the database.
        """
        with self._db_cursor() as cursor:
            threshold = datetime.utcnow() - self.timeout
            cursor.execute('DELETE FROM ' + self.name + ' WHERE timestamp < ?', (threshold,))

    def clear(self):
        """
        Delete all entries from the cache.
        """
        logger.info("Clearing " + self.name + " cache")
        with self._db_cursor() as cursor:
            cursor.execute('DELETE FROM ' + self.name)

    @contextmanager
    def _db_cursor(self):
        # Connect with isolation_level=None for autocommit mode and close connection after each access to avoid 
        # locking the database. Otherwise, you can't access the same database from multiple cache instances.
        with closing(sqlite3.connect(self.dbname, detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)) as db:
            with closing(db.cursor()) as cursor:
                yield cursor

    def _init_db(self):
        with self._db_cursor() as cursor:
            cursor.execute('CREATE TABLE IF NOT EXISTS ' + self.name +
                           ' (key TEXT PRIMARY KEY NOT NULL, ' +
                           ' timestamp TIMESTAMP NOT NULL, ' +
                           ' content BLOB NOT NULL)')

    def _make_key(self, function, args, kwargs):
        """
        Construct a key from function name and arguments.
        Override this if __qualname__ isn't unique for the functions you're using.
        """
        # Class methods take the class instance as the first parameter, which would include the repr of the object
        # in the key, which in turn might include a memory address or similar ephemeral component, so we need to
        # exclude it.
        print("__self__: %s", hasattr(function, '__self__'))
        if hasattr(function, '__self__'):
            print('len(args): %s', len(args))
            if len(args) > 0:
                print('args[0] == self: %s', args[0] == function.__self__)

        if hasattr(function, '__self__') and len(args) > 0 and args[0] == function.__self__:
            args = args[1:]

        # We want None arguments to show up as None, but that would collide with the string "None".
        # That's why we also need to add quotes to strings.
        def serialize_arg(x):
            if x is None:
                return 'None'
            if type(x) is str:
                return '"' + x + '"'
            return str(x)

        # Build argument list like (a, b, c=d, e=f)
        all_args = [serialize_arg(x) for x in args] + ["{}={}".format(k, serialize_arg(v)) for k, v in kwargs.items()]
        return function.__qualname__ + '(' + ','.join(all_args) + ')'

    def _serialize(self, x):
        """
        Transform value to string before writing to cache.
        If you want to support anything other than string return values in cached functions, you need to override this.
        """
        return x

    def _deserialize(self, x):
        """
        Transform serialized value from cache back to its original type.
        If you want to support anything other than string return values in cached functions, you need to override this.
        """
        return x
