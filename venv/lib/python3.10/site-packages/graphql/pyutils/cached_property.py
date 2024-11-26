from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    standard_cached_property = None
else:
    try:
        from functools import cached_property as standard_cached_property
    except ImportError:  # Python < 3.8
        standard_cached_property = None

if standard_cached_property:
    cached_property = standard_cached_property
else:
    # Code taken from https://github.com/bottlepy/bottle

    class CachedProperty:
        """A cached property.

        A property that is only computed once per instance and then replaces itself with
        an ordinary attribute. Deleting the attribute resets the property.
        """

        def __init__(self, func: Callable) -> None:
            self.__doc__ = getattr(func, "__doc__")
            self.func = func

        def __get__(self, obj: object, cls: type) -> Any:
            if obj is None:
                return self
            value = obj.__dict__[self.func.__name__] = self.func(obj)
            return value

    cached_property = CachedProperty

__all__ = ["cached_property"]
