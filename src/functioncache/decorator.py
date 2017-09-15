

def cached(cache):
    """Function Decorator - Use given cache to cache function calls"""
    def decorator(function):
        def wrapped(*args, **kwargs):
            return cache.get(function, *args, **kwargs)
        # Decorated function should keep its __qualname__ so that _make_key still works
        wrapped.__qualname__ = function.__qualname__
        # If decorating a method, we need to set __self__, otherwise _make_key can't filter out the self argument
        if hasattr(function, '__self__'):
            wrapped.__self__ = function.__self__
        return wrapped
    return decorator
