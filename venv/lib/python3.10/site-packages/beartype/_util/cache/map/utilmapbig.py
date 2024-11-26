#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **unbounded cache** utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Callable,
    Dict,
    Union,
)
from beartype._util.utilobject import SENTINEL
from collections.abc import Hashable
from contextlib import AbstractContextManager
from threading import Lock

# ....................{ CLASSES                            }....................
#FIXME: Submit back to StackOverflow, preferably under this question:
#    https://stackoverflow.com/questions/1312331/using-a-global-dictionary-with-threads-in-python
class CacheUnboundedStrong(object):
    '''
    **Thread-safe strongly unbounded cache** (i.e., mapping of unlimited size
    from strongly referenced arbitrary keys onto strongly referenced arbitrary
    values, whose methods are guaranteed to behave thread-safely).

    Design
    ------
    Cache implementations typically employ weak references for safety. Employing
    strong references invites memory leaks by preventing objects *only*
    referenced by the cache (cache-only objects) from being garbage-collected.
    Nonetheless, this cache intentionally employs strong references to persist
    these cache-only objects across calls to callables decorated with
    :func:`beartype.beartype`. In theory, caching an object under a weak
    reference would result in immediate garbage-collection; with *no* external
    strong referents, that object would be garbage-collected with all other
    short-lived objects in the first generation (i.e., generation 0).

    This cache intentionally does *not* adhere to standard mapping semantics by
    subclassing a standard mapping API (e.g., :class:`dict`,
    :class:`collections.abc.MutableMapping`). Standard mapping semantics are
    sufficiently low-level as to invite race conditions between competing
    threads concurrently contesting the same instance of this class. For
    example, consider the following standard non-atomic logic for caching a new
    key-value into this cache:

    .. code-block:: python

       if key not in cache:    # <-- If a context switch happens immediately
                               # <-- after entering this branch, bad stuff!
           cache[key] = value  # <-- We may overwrite another thread's work.

    Attributes
    ----------
    _key_to_value : dict[Hashable, object]
        Internal **backing store** (i.e., thread-unsafe dictionary of unlimited
        size mapping from strongly referenced arbitrary keys onto strongly
        referenced arbitrary values).
    _key_to_value_get : Callable
        The :meth:`self._key_to_value.get` method, classified for efficiency.
    _key_to_value_set : Callable
        The :meth:`self._key_to_value.__setitem__` dunder method, classified
        for efficiency.
    _lock : AbstractContextManager
        **Instance-specific thread lock** (i.e., low-level thread locking
        mechanism implemented as a highly efficient C extension, defined as an
        instance variable for non-reentrant reuse by the public API of this
        class). Although CPython, the canonical Python interpreter, *does*
        prohibit conventional multithreading via its Global Interpreter Lock
        (GIL), CPython still coercively preempts long-running threads at
        arbitrary execution points. Ergo, multithreading concerns are *not*
        safely ignorable -- even under CPython.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_key_to_value',
        '_key_to_value_get',
        '_key_to_value_set',
        '_lock',
    )

    # ..................{ INITIALIZER                        }..................
    def __init__(
        self,

        # Optional parameters.
        lock_type: Union[type, Callable[[], object]] = Lock,
    ) -> None:
        '''
        Initialize this cache to an empty cache.

        Parameters
        ----------
        lock_type : Union[type, Callable[[], object]]
            Type of thread-safe lock to internally use. Defaults to
            :class:`Lock` (i.e., the type of the standard non-reentrant lock)
            for efficiency.
        '''

        # Initialize all instance variables.
        self._key_to_value: Dict[Hashable, object] = {}
        self._key_to_value_get = self._key_to_value.get
        self._key_to_value_set = self._key_to_value.__setitem__
        self._lock: AbstractContextManager = lock_type()  # type: ignore[assignment]

    # ..................{ GETTERS                            }..................
    def cache_or_get_cached_value(
        self,

        # Mandatory parameters.
        key: Hashable,
        value: object,

        # Hidden parameters, localized for negligible efficiency.
        _SENTINEL=SENTINEL,
    ) -> object:
        '''
        **Statically** (i.e., non-dynamically, rather than "statically" in the
        different semantic sense of "static" methods) associate the passed key
        with the passed value if this cache has yet to cache this key (i.e., if
        this method has yet to be passed this key) and, in any case, return the
        value associated with this key.

        Parameters
        ----------
        key : Hashable
            **Key** (i.e., arbitrary hashable object) to return the associated
            value of.
        value : object
            **Value** (i.e., arbitrary object) to associate with this key if
            this key has yet to be associated with any value.

        Returns
        ----------
        object
            **Value** (i.e., arbitrary object) associated with this key.
        '''
        # assert isinstance(key, Hashable), f'{repr(key)} unhashable.'

        # Thread-safely (but non-reentrantly)...
        with self._lock:
            # Value previously cached under this key if any *OR* the sentinel
            # placeholder otherwise.
            value_old = self._key_to_value_get(key, _SENTINEL)

            # If this key has already been cached, return this value as is.
            if value_old is not _SENTINEL:
                return value_old
            # Else, this key has yet to be cached.

            # Cache this key with this value.
            self._key_to_value_set(key, value)

            # Return this value.
            return value


    #FIXME: Unit test us up.
    #FIXME: Generalize to accept a new mandatory "arg: object" parameter and
    #then pass rather than forcefully passing the passed key. \o/
    def cache_or_get_cached_func_return_passed_arg(
        self,

        # Mandatory parameters.
        key: Hashable,
        value_factory: Callable[[object], object],
        arg: object,

        # Hidden parameters, localized for negligible efficiency.
        _SENTINEL=SENTINEL,
    ) -> object:
        '''
        Dynamically associate the passed key with the value returned by the
        passed **value factory** (i.e., caller-defined function accepting this
        key and returning the value to be associated with this key) if this
        cache has yet to cache this key (i.e., if this method has yet to be
        passed this key) and, in any case, return the value associated with
        this key.

        Caveats
        ----------
        **This value factory must not recursively call this method.** For
        efficiency, this cache is internally locked through a non-reentrant
        rather than reentrant thread lock. If this value factory accidentally
        recursively calls this method, the active thread will be indefinitely
        locked. Welcome to the risky world of high-cost efficiency gains.

        Parameters
        ----------
        key : Hashable
            **Key** (i.e., arbitrary hashable object) to return the associated
            value of.
        value_factory : Callable[[object], object]
            **Value factory** (i.e., caller-defined function accepting the
            passed ``arg`` object and dynamically returning the value to be
            associated with this key).
        arg : object
            Arbitrary object to be passed as is to this value factory.

        Returns
        ----------
        object
            **Value** (i.e., arbitrary object) associated with this key.
        '''
        # assert isinstance(key, Hashable), f'{repr(key)} unhashable.'
        # assert callable(value_factory), f'{repr(value_factory)} uncallable.'

        # Thread-safely (but non-reentrantly)...
        with self._lock:
            # Value previously cached under this key if any *OR* the sentinel
            # placeholder otherwise.
            value_old = self._key_to_value_get(key, _SENTINEL)

            # If this key has already been cached, return this value as is.
            if value_old is not _SENTINEL:
                return value_old
            # Else, this key has yet to be cached.

            # Value created by this factory function, localized for negligible
            # efficiency to avoid the unnecessary subsequent dictionary lookup.
            value = value_factory(arg)

            # Cache this key with this value.
            self._key_to_value_set(key, value)

            # Return this value.
            return value

    # ..................{ CLEARERS                           }..................
    #FIXME: Unit test us up, please.
    def clear(self) -> None:
        '''
        Clear (i.e., empty) this cache.
        '''

        # Clear your head and be at peace, one-liner.
        self._key_to_value.clear()
