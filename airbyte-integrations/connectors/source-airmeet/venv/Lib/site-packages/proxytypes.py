"""
Based on the implementation here by Phillip J. Eby:
https://pypi.python.org/pypi/ProxyTypes
"""

import operator
from functools import wraps

OPERATORS = [
    # Unary
    "pos",
    "neg",
    "abs",
    "invert",
    # Comparison
    "eq",
    "ne",
    "lt",
    "gt",
    "le",
    "ge",
    # Container
    "getitem",
    "setitem",
    "delitem",
    "contains",
    # In-place operators
    "iadd",
    "isub",
    "imul",
    "ifloordiv",
    "itruediv",
    "imod",
    "ipow",
    "ilshift",
    "irshift",
    "iand",
    "ior",
    "ixor",
]
REFLECTED_OPERATORS = [
    "add",
    "sub",
    "mul",
    "floordiv",
    "truediv",
    "mod",
    "pow",
    "and",
    "or",
    "xor",
    "lshift",
    "rshift",
]
# These functions all have magic methods named after them
MAGIC_FUNCS = [
    divmod,
    round,
    repr,
    str,
    hash,
    len,
    abs,
    complex,
    bool,
    int,
    float,
    iter,
    bytes,
]

_oga = object.__getattribute__
_osa = object.__setattr__


class ProxyMetaClass(type):
    def __new__(mcs, name, bases, dct):
        newcls = super(ProxyMetaClass, mcs).__new__(mcs, name, bases, dct)
        newcls.__notproxied__ = set(dct.pop("__notproxied__", ()))
        # Add all the non-proxied attributes from base classes
        for base in bases:
            if hasattr(base, "__notproxied__"):
                newcls.__notproxied__.update(base.__notproxied__)
        for key, val in dct.items():
            setattr(newcls, key, val)
        return newcls

    def __setattr__(cls, attr, value):
        # Don't do any magic on the methods of the base Proxy class or the
        # __new__ static method
        if cls.__bases__[0].__name__ == "_ProxyBase" or attr == "__new__":
            pass
        elif callable(value):
            if getattr(value, "__notproxied__", False):
                cls.__notproxied__.add(attr)
            # Don't wrap staticmethods or classmethods
            if not isinstance(value, (staticmethod, classmethod)):
                value = cls._no_proxy(value)
        elif isinstance(value, property):
            if getattr(value.fget, "__notproxied__", False):
                cls.__notproxied__.add(attr)
            # Remake properties, with the underlying functions wrapped
            fset = cls._no_proxy(value.fset) if value.fset else value.fset
            fdel = cls._no_proxy(value.fdel) if value.fdel else value.fdel
            value = property(cls._no_proxy(value.fget), fset, fdel)
        super(ProxyMetaClass, cls).__setattr__(attr, value)

    @staticmethod
    def _no_proxy(method):
        """
        Returns a wrapped version of `method`, such that proxying is turned off
        during the method call.

        """

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            notproxied = _oga(self, "__notproxied__")
            _osa(self, "__notproxied__", True)
            try:
                return method(self, *args, **kwargs)
            finally:
                _osa(self, "__notproxied__", notproxied)

        return wrapper


# Since python 2 and 3 metaclass syntax aren't compatible, create an instance
# of our metaclass which our Proxy class can inherit from
_ProxyBase = ProxyMetaClass("_ProxyBase", (), {})


class Proxy(_ProxyBase):
    """
    Proxy for any python object. Base class for other proxies.

    :attr:`__subject__` is the only non-proxied attribute, and contains the
        proxied object

    """

    __notproxied__ = ("__subject__",)

    def __init__(self, subject):
        self.__subject__ = subject

    @staticmethod
    def _should_proxy(self, attr):
        """
        Determines whether `attr` should be looked up on the proxied object, or
        the proxy itself.

        """
        if attr in type(self).__notproxied__:
            return False
        if _oga(self, "__notproxied__") is True:
            return False
        return True

    def __getattribute__(self, attr):
        if Proxy._should_proxy(self, attr):
            return getattr(self.__subject__, attr)
        return _oga(self, attr)

    def __setattr__(self, attr, val):
        if Proxy._should_proxy(self, attr):
            setattr(self.__subject__, attr, val)
        _osa(self, attr, val)

    def __delattr__(self, attr):
        if Proxy._should_proxy(self, attr):
            delattr(self.__subject__, attr)
        object.__delattr__(self, attr)

    def __call__(self, *args, **kw):
        return self.__subject__(*args, **kw)

    @classmethod
    def add_proxy_meth(cls, name, func, arg_pos=0):
        """
        Add a method `name` to the class, which returns the value of `func`,
        called with the proxied value inserted at `arg_pos`

        """

        @wraps(func)
        def proxied(self, *args, **kwargs):
            args = list(args)
            args.insert(arg_pos, self.__subject__)
            result = func(*args, **kwargs)
            return result

        setattr(cls, name, proxied)


for func in MAGIC_FUNCS:
    Proxy.add_proxy_meth("__%s__" % func.__name__, func)

for op in OPERATORS + REFLECTED_OPERATORS:
    magic_meth = "__%s__" % op
    Proxy.add_proxy_meth(magic_meth, getattr(operator, magic_meth))

# Reflected operators
for op in REFLECTED_OPERATORS:
    Proxy.add_proxy_meth("__r%s__" % op, getattr(operator, "__%s__" % op), arg_pos=1)

# One offs
# Only non-operator that needs a reflected version
Proxy.add_proxy_meth("__rdivmod__", divmod, arg_pos=1)
# pypy is missing __index__ in operator module
Proxy.add_proxy_meth("__index__", operator.index)
# For python 2.6
Proxy.__nonzero__ = Proxy.__bool__


class CallbackProxy(Proxy):
    """
    Proxy for a callback result. Callback is called on each use.

    """

    def __init__(self, callback):
        self.callback = callback

    @property
    def __subject__(self):
        return self.callback()


class LazyProxy(CallbackProxy):
    """
    Proxy for a callback result, that is cached on first use.

    """

    @property
    def __subject__(self):
        try:
            return self.cache
        except AttributeError:
            pass

        self.cache = super(LazyProxy, self).__subject__
        return self.cache

    @__subject__.setter
    def __subject__(self, value):
        self.cache = value


def notproxied(func):
    """
    Decorator to add methods to the __notproxied__ list

    """
    func.__notproxied__ = True
    return func
