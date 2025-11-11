# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Python's built-in :mod:`functools` module builds several useful
utilities on top of Python's first-class function support.
``typeutils`` attempts to do the same for metaprogramming with types
and instances.
"""
import sys
from collections import deque

_issubclass = issubclass


def make_sentinel(name='_MISSING', var_name=None):
    """Creates and returns a new **instance** of a new class, suitable for
    usage as a "sentinel", a kind of singleton often used to indicate
    a value is missing when ``None`` is a valid input.

    Args:
        name (str): Name of the Sentinel
        var_name (str): Set this name to the name of the variable in
            its respective module enable pickleability. Note:
            pickleable sentinels should be global constants at the top
            level of their module.

    >>> make_sentinel(var_name='_MISSING')
    _MISSING

    The most common use cases here in boltons are as default values
    for optional function arguments, partly because of its
    less-confusing appearance in automatically generated
    documentation. Sentinels also function well as placeholders in queues
    and linked lists.

    .. note::

      By design, additional calls to ``make_sentinel`` with the same
      values will not produce equivalent objects.

      >>> make_sentinel('TEST') == make_sentinel('TEST')
      False
      >>> type(make_sentinel('TEST')) == type(make_sentinel('TEST'))
      False

    """
    class Sentinel:
        def __init__(self):
            self.name = name
            self.var_name = var_name

        def __repr__(self):
            if self.var_name:
                return self.var_name
            return f'{self.__class__.__name__}({self.name!r})'

        if var_name:
            def __reduce__(self):
                return self.var_name

        def __bool__(self):
            return False

        def __copy__(self):
            return self

        def __deepcopy__(self, _memo):
            return self

    if var_name:
        frame = sys._getframe(1)
        module = frame.f_globals.get('__name__')
        if not module or module not in sys.modules:
            raise ValueError('Pickleable sentinel objects (with var_name) can only'
                             ' be created from top-level module scopes')
        Sentinel.__module__ = module

    return Sentinel()


def issubclass(subclass, baseclass):
    """Just like the built-in :func:`issubclass`, this function checks
    whether *subclass* is inherited from *baseclass*. Unlike the
    built-in function, this ``issubclass`` will simply return
    ``False`` if either argument is not suitable (e.g., if *subclass*
    is not an instance of :class:`type`), instead of raising
    :exc:`TypeError`.

    Args:
        subclass (type): The target class to check.
        baseclass (type): The base class *subclass* will be checked against.

    >>> class MyObject(object): pass
    ...
    >>> issubclass(MyObject, object)  # always a fun fact
    True
    >>> issubclass('hi', 'friend')
    False
    """
    try:
        return _issubclass(subclass, baseclass)
    except TypeError:
        return False


def get_all_subclasses(cls):
    """Recursively finds and returns a :class:`list` of all types
    inherited from *cls*.

    >>> class A(object):
    ...     pass
    ...
    >>> class B(A):
    ...     pass
    ...
    >>> class C(B):
    ...     pass
    ...
    >>> class D(A):
    ...     pass
    ...
    >>> [t.__name__ for t in get_all_subclasses(A)]
    ['B', 'D', 'C']
    >>> [t.__name__ for t in get_all_subclasses(B)]
    ['C']

    """
    try:
        to_check = deque(cls.__subclasses__())
    except (AttributeError, TypeError):
        raise TypeError('expected type object, not %r' % cls)
    seen, ret = set(), []
    while to_check:
        cur = to_check.popleft()
        if cur in seen:
            continue
        ret.append(cur)
        seen.add(cur)
        to_check.extend(cur.__subclasses__())
    return ret


class classproperty:
    """Much like a :class:`property`, but the wrapped get function is a
    class method.  For simplicity, only read-only properties are
    implemented.
    """

    def __init__(self, fn):
        self.fn = fn

    def __get__(self, instance, cls):
        return self.fn(cls)
