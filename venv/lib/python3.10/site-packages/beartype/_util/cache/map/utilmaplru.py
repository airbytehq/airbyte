#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Least Recently Used (LRU) cache** utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: The current "CacheLruStrong" implementation is overly low-level and
#thus fundamentally *THREAD-UNSAFE.* The core issue here is that the current
#approach encourages callers to perform thread-unsafe logic resembling:
#   if key not in lru_dict:  # <-- if a context switch happens here, bad stuff
#       lru_dict[key] = value
#
#For thread-safety, the entire "CacheLruStrong" class *MUST* be rethought along
#the manner of the comparable "utilmapbig.CacheUnboundedStrong" class. Notably:
#* "CacheLruStrong" class should *NOT* directly subclass "dict" but instead
#  simply contain a "_dict" instance.
#* Thread-unsafe dunder methods (particularly the "__setitem__" method) should
#  probably *NOT* be defined at all. Yeah, we know.
#* A new CacheLruStrong.cache_entry() method resembling the existing
#  CacheUnboundedStrong.cache_entry() method should be declared.
#* Indeed, we should (arguably) declare a new "CacheStrongABC" base class to
#  provide a common API here -- trivializing switching between different
#  caching strategies implemented by concrete subclasses.

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCacheLruException
from beartype.typing import Hashable
from threading import Lock

# ....................{ CLASSES                            }....................
class CacheLruStrong(dict):
    '''
    **Thread-safe strong Least Recently Used (LRU) cache** (i.e., mapping
    limited to some maximum capacity of strongly referenced arbitrary keys
    mapped onto strongly referenced arbitrary values, whose methods are
    guaranteed to behave thread-safely).

    Design
    ------
    Cache implementations typically employ weak references for safety.
    Employing strong references invites memory leaks by preventing objects
    *only* referenced by the cache (cache-only objects) from being
    garbage-collected. Nonetheless, this cache intentionally employs strong
    references to persist these cache-only objects across calls to callables
    decorated with :func:`beartype.beartype`. In theory, caching an object
    under a weak reference would result in immediate garbage-collection as,
    with no external strong referents, the object would get collected with all
    other short-lived objects in the first generation (i.e., generation 0).

    Note that:

    * The equivalent LRU cache employing weak references to keys and/or values
      may be trivially implemented by swapping this classes inheritance from
      the builtin :class:`dict` to either of the builtin
      :class:`weakref.WeakKeyDictionary` or
      :class:`weakref.WeakValueDictionary`.
    * The standard example of a cache-only object is a container iterator
      (e.g., :meth:`dict.items`).

    Attributes
    ----------
    _size : int
        **Cache capacity** (i.e., maximum number of key-value pairs persisted
        by this cache).
    _lock : Lock
        **Non-reentrant instance-specific thread lock** (i.e., low-level thread
        locking mechanism implemented as a highly efficient C extension,
        defined as an instance variable for non-reentrant reuse by the public
        API of this class). Although CPython, the canonical Python interpreter,
        *does* prohibit conventional multithreading via its Global Interpreter
        Lock (GIL), CPython still coercively preempts long-running threads at
        arbitrary execution points. Ergo, multithreading concerns are *not*
        safely ignorable -- even under CPython.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_size',
        '_lock',
    )

    # ..................{ DUNDERS                            }..................
    def __init__(self, size: int) -> None:
        '''
        Initialize this cache to an empty cache with a capacity of this size.

        Parameters
        ----------
        size : int
            **Cache capacity** (i.e., maximum number of key-value pairs held in
            this cache).

        Raises
        ------
        _BeartypeUtilCacheLruException:
            If the capacity is *not* an integer or its a **non-positive
            integer** (i.e. less than 1).
        '''

        super().__init__()

        if not isinstance(size, int):
            raise _BeartypeUtilCacheLruException(
                f'LRU cache capacity {repr(size)} not integer.')
        elif size < 1:
            raise _BeartypeUtilCacheLruException(
                f'LRU cache capacity {size} not positive.')

        self._size = size
        self._lock = Lock()


    def __getitem__(
        self,
        key: Hashable,

        # Superclass methods efficiently localized as default parameters.
        __contains=dict.__contains__,
        __getitem=dict.__getitem__,
        __delitem=dict.__delitem__,
        __pushitem=dict.__setitem__,
    ) -> object:
        '''
        Return an item previously cached under the passed key *or* raise an
        exception otherwise.

        This implementation is *practically* identical to
        :meth:`self.__contains__` except we return an arbitrary object rather
        than a boolean.

        Parameters
        ----------
        key : Hashable
            Arbitrary hashable key to retrieve the cached value of.

        Returns
        ----------
        object
            Arbitrary value cached under this key.

        Raises
        ----------
        TypeError
            If this key is not hashable.
        KeyError
            If this key isn't cached.
        '''

        with self._lock:
            # Reset this key if it exists.
            if __contains(self, key):
                val = __getitem(self, key)
                __delitem(self, key)
                __pushitem(self, key, val)
                return val

            raise KeyError(f'Key Error: {key}')


    def __setitem__(
        self,
        key: Hashable,
        value: object,

        # Superclass methods efficiently localized as default parameters.
        __contains=dict.__contains__,
        __delitem=dict.__delitem__,
        __pushitem=dict.__setitem__,
        __iter=dict.__iter__,
        __len=dict.__len__,
    ) -> None:
        '''
        Cache this key-value pair while preserving size constraints.

        Parameters
        ----------
        key : Hashable
            Arbitrary hashable key to cache this value to.
        value : object
            Arbitrary value to be cached under this key.

        Raises
        ----------
        TypeError
            If this key is not hashable.
        '''

        with self._lock:
            if __contains(self, key):
                __delitem(self, key)
            __pushitem(self, key, value)

            # Prune this cache.
            if __len(self) > self._size:
                __delitem(self, next(__iter(self)))


    def __contains__(
        self,
         key: Hashable,

         # Superclass methods efficiently localized as default parameters.
         __contains=dict.__contains__,
         __getitem=dict.__getitem__,
         __delitem=dict.__delitem__,
         __pushitem=dict.__setitem__,
     ) -> bool:
        '''
        Return a boolean indicating whether this key is cached.

        If this key is cached, this method implicitly refreshes this key by
        popping and pushing this key back onto the top of this cache.

        Parameters
        ----------
        key : Hashable
            Arbitrary hashable key to detect the existence of.

        Returns
        ----------
        bool
            ``True`` only if this key is cached.

        Raises
        ----------
        TypeError
            If this key is unhashable.
        '''

        with self._lock:
            if __contains(self, key):
                val = __getitem(self, key)
                __delitem(self, key)
                __pushitem(self, key, val)
                return True

            return False
