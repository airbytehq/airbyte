import warnings

import dpath
from dpath import _DEFAULT_SENTINEL
from dpath.types import MergeType


def deprecated(func):
    message = \
        "The dpath.util package is being deprecated. All util functions have been moved to dpath package top level."

    def wrapper(*args, **kwargs):
        warnings.warn(message, DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)

    return wrapper


@deprecated
def new(obj, path, value, separator="/", creator=None):
    return dpath.new(obj, path, value, separator, creator)


@deprecated
def delete(obj, glob, separator="/", afilter=None):
    return dpath.delete(obj, glob, separator, afilter)


@deprecated
def set(obj, glob, value, separator="/", afilter=None):
    return dpath.set(obj, glob, value, separator, afilter)


@deprecated
def get(obj, glob, separator="/", default=_DEFAULT_SENTINEL):
    return dpath.get(obj, glob, separator, default)


@deprecated
def values(obj, glob, separator="/", afilter=None, dirs=True):
    return dpath.values(obj, glob, separator, afilter, dirs)


@deprecated
def search(obj, glob, yielded=False, separator="/", afilter=None, dirs=True):
    return dpath.search(obj, glob, yielded, separator, afilter, dirs)


@deprecated
def merge(dst, src, separator="/", afilter=None, flags=MergeType.ADDITIVE):
    return dpath.merge(dst, src, separator, afilter, flags)
