import json

from .cache import Cache


class JsonCache(Cache):
    def _serialize(self, x):
        return json.dumps(x)

    def _deserialize(self, x):
        return json.loads(x)

    def get_json(self, function, *args, **kwargs):
        """
        Return function call result as serialized JSON.
        If you would serialize the result anyway, this avoids the deserialization when read from cache.
        """
        key = self._make_key(function, args, kwargs)
        return self.get_json_with_key(key, function, *args, **kwargs)

    def get_json_with_key(self, key, function, *args, **kwargs):
        cached = self.lookup_cached(key)
        if cached is not None:
            return cached
        return self._serialize(self.get(function, *args, **kwargs))

