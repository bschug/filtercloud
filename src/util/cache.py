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
    """
    def __init__(self, name, *, dbname='cache.sqlite', timeout=None):
        """
        Multiple Cache instances can share the same database.
        They can also share the same table, i.e. they are different views on the same cache.
        Make sure to only use the same name if the timeout is also the same.

        :param name:    Name of the cache. Used as the SQLite table name.
        :param dbname:  SQLite db to use for storage.
        :param timeout: Maximum age of cached entries (timedelta)
        """
        assert timeout is not None
        self.name = name
        self.dbname = dbname
        self.timeout = timeout
        self._init_db()

    @contextmanager
    def _db_cursor(self):
        with closing(sqlite3.connect(self.dbname, detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)) as db:
            with closing(db.cursor()) as cursor:
                yield cursor
                #db.commit()

    def _init_db(self):
        with self._db_cursor() as cursor:
            cursor.execute('CREATE TABLE IF NOT EXISTS ' + self.name +
                           ' (key TEXT PRIMARY KEY NOT NULL, ' +
                           ' timestamp TIMESTAMP NOT NULL, ' +
                           ' content BLOB NOT NULL)')

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

        # Invoke function and store result in cache
        new_value = function(*args, **kwargs)
        self.store(key, new_value)
        return new_value

    def lookup_cached(self, key):
        """
        Lookup a value in the cache by key.
        If the value has never been added, or is outdated, returns None.
        """
        threshold = datetime.utcnow() - self.timeout

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
