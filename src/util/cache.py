import logging
from datetime import datetime, timedelta
from contextlib import closing, contextmanager

import sqlite3


logger = logging.getLogger('util.cache')
logger.setLevel(logging.WARNING)


class Cache(object):
    """
    Cache that stores the results of function calls.
    Returns cached results if they are less than <timeout> old.
    Uses an sqlite database to store cached results.

    Caveats:
     * This cache uses the function's __qualname__ to build a key.
       If this is not unique for your function (e.g. same function name  defined in multiple modules),
       functions with colliding names may return the other function's cached values.
       Override the _function_key method to provide a different way of identifying functions,
       or call get_with_key to directly specify a key (which must include the arguments).
     * This cache is designed for functions with a finite set of possible arguments. It does not impose
       any limits on the size of the cache. Don't use this if arguments are provided by user input or
       some other source out of your control. A malicious user may make you run out of disk space.
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
        all_args = [str(x) for x in args] + ["{}={}".format(k, v) for k, v in kwargs.items()]
        key = function.__qualname__ + '(' + ','.join(all_args) + ')'
        return self.get_with_key(key, function, *args, **kwargs)

    def get_with_key(self, key, function, *args, **kwargs):
        """
        Same as get, but with an explicit key instead of one derived from function name and arguments.
        """
        # Use cached data if available
        cached = self.lookup_cached(key)
        if cached is not None:
            logger.debug("Returning cached version of %s", format(key))
            return cached
        logger.debug("No cached version found for %s", format(key))

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
                return cached
            raise

    def lookup_cached(self, key, *, threshold=None):
        """
        Lookup a value in the cache by key.
        If the value has never been added, or is outdated, returns None.
        """
        threshold = threshold or datetime.utcnow() - self.timeout

        with self._db_cursor() as cursor:
            cursor.execute('SELECT timestamp, content FROM ' + self.name + ' WHERE key = ?', (key,))
            for timestamp, content in cursor:
                if timestamp > threshold:
                    return content
                logger.debug("Ignoring cached value of %s because it was created on %s, which is before %s",
                             format(key), format(timestamp), format(threshold))
        return None

    def store(self, key, value):
        """
        Store a value in the cache.
        """
        logger.debug("Storing new value for %s: %s", format(key), format(value))
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

    def _function_key(self, function):
        """Override this if __qualname__ isn't unique for the functions you're using."""
        return function.__qualname__

