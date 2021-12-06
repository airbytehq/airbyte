__all__ = ("cached_property",)

try:
    from functools import cached_property
except ImportError:

    class cached_property:  # type: ignore[no-redef]
        """Decorator that turns an instance method into a cached property
        From https://speakerdeck.com/u/mitsuhiko/p/didntknow, slide #69
        """

        __NOT_SET = object()

        def __init__(self, func):
            self.func = func
            self.__name__ = func.__name__
            self.__doc__ = func.__doc__
            self.__module__ = func.__module__

        def __get__(self, obj, type=None):
            if obj is None:
                return self
            value = obj.__dict__.get(self.__name__, self.__NOT_SET)
            if value is self.__NOT_SET:
                value = self.func(obj)
                obj.__dict__[self.__name__] = value
            return value
