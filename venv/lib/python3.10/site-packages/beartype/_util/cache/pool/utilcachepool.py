#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **key pool type** (i.e., object caching class implemented as a
dictionary of lists of arbitrary objects to be cached, where objects cached to
the same list are typically of the same type).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Conditionally pass "is_debug=True" to the KeyPool.{acquire,release}()
#methods defined below when the "BeartypeConfig.is_debug" parameter is "True"
#for the current call to the @beartype decorator, please.

#FIXME: Optimize the KeyPool.{acquire,release}() methods defined below. Rather
#than unconditionally wrapping the bodies of each in a thread-safe
#"self._thread_lock" context manager, we might be able to leverage the GIL by
#only doing so "if threading.active_count():". Profile us up, please.

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCachedKeyPoolException
from beartype.typing import (
    Dict,
    Union,
)
from collections import defaultdict
from collections.abc import Callable, Hashable
from threading import Lock

# ....................{ CLASSES                            }....................
class KeyPool(object):
    '''
    Thread-safe **key pool** (i.e., object cache implemented as a dictionary of
    lists of arbitrary objects to be cached, where objects cached to the same
    list are typically of the same type).

    Key pools are thread-safe by design and thus safely usable as module-scoped
    globals accessed from module-scoped callables.

    Attributes
    ----------
    _key_to_pool : defaultdict
        Dictionary mapping from an **arbitrary key** (i.e., hashable object) to
        corresponding **pool** (i.e., list of zero or more arbitrary objects
        referred to as "pool items" cached under that key). For both efficiency
        and simplicity, this dictionary is defined as a :class:`defaultdict`
        implicitly initializing missing keys on initial access to the empty
        list.
    _pool_item_id_to_is_acquired : dict
        Dictionary mapping from the unique object identifier of a **pool item**
        (i.e., arbitrary object cached under a pool of the :attr:`_key_to_pool`
        ditionary) to a boolean that is either:

        * :data:`True` if that item is currently **acquired** (i.e., most
          recently returned by a call to the :meth:`acquire` method).
        * :data:`False` if that item is currently **released** (i.e., most
          recently passed to a call to the :meth:`release` method).
    _pool_item_maker : Callable
        Caller-defined factory callable internally called by the
        :meth:`acquire` method on attempting to acquire a non-existent object
        from an **empty pool. See :meth:`__init__` for further details.
    _thread_lock : Lock
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
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_key_to_pool',
        '_pool_item_id_to_is_acquired',
        '_pool_item_maker',
        '_thread_lock',
    )

    # ..................{ INITIALIZER                        }..................
    def __init__(
        self,
        item_maker: Union[type, Callable],
    ) -> None:
        '''
        Initialize this key pool with the passed factory callable.

        Parameters
        ----------
        item_maker : Union[type, Callable[[Hashable,], Any]]
            Caller-defined factory callable internally called by the
            :meth:`acquire` method on attempting to acquire a non-existent
            object from an **empty pool** (i.e., either a missing key *or* an
            empty list of an existing key of the underlying
            :attr:`_key_to_pool` dictionary). That method initializes the empty
            pool in question by calling this factory with the key associated
            with that pool and appending the object created and returned by
            this factory to that pool. This factory is thus expected to have a
            signature resembling:

            .. code-block:: python

               from collections.abc import Hashable
               def item_maker(key: Hashable) -> object: ...
        '''
        assert callable(item_maker), f'{repr(item_maker)} not callable.'

        # Classify these parameters as instance variables.
        self._pool_item_maker = item_maker

        # Initialize all remaining instance variables.
        #
        # Note that "defaultdict" instances *MUST* be initialized with
        # positional rather than keyword parameters. For unknown reasons,
        # initializing such an instance with a keyword parameter causes that
        # instance to silently behave like a standard dictionary instead: e.g.,
        #
        #     >>> dd = defaultdict(default_factory=list)
        #     >>> dd['ee']
        #     KeyError: 'ee'
        self._key_to_pool: Dict[Hashable, list] = defaultdict(list)
        self._pool_item_id_to_is_acquired: Dict[int, bool] = {}
        self._thread_lock = Lock()

    # ..................{ METHODS                            }..................
    def acquire(
        self,

        # Optional parameters.
        key: Hashable = None,
        is_debug: bool = False,
    ) -> object:
        '''
        Acquire an arbitrary object associated with the passed **arbitrary
        key** (i.e., hashable object).

        Specifically, this method tests whether there exists a non-empty list
        previously associated with this key. If so, this method pops the last
        item from that list and returns that item; else (i.e., if there either
        exists no such list or such a list exists but is empty), this method
        effectively (in order):

        #. If no such list exists, create a new empty list associated with
           this key.
        #. Create a new object to be returned by calling the user-defined
           :meth:`_pool_item_maker` factory callable.
        #. Append this object to this list.
        #. Add/Update acquisition state of the object to True
        #. Returns this object.

        Parameters
        ----------
        key : Optional[HashableType]
            Hashable object associated with the pool item to be acquired.
            Defaults to ``None``.
        is_debug : bool, optional
            ``True`` only if enabling inefficient debugging logic. Notably,
            enabling this option notes this item to have now been acquired.
            Defaults to ``False``.

        Returns
        ----------
        object
            Pool item associated with this hashable object.

        Raises
        ----------
        TypeError
            If this key is unhashable and thus *not* a key.
        '''

        # In a thread-safe manner...
        with self._thread_lock:
            #FIXME: This logic can *PROBABLY* be optimized into:
            #    if not is_debug:
            #        try:
            #            return self._key_to_pool[key].pop()
            #        except IndexError:
            #            return self._pool_item_maker(key)
            #    else:
            #        try:
            #            pool_item = self._key_to_pool[key].pop()
            #        except IndexError:
            #            pool_item = self._pool_item_maker(key)
            #
            #        # Record this item to have now been acquired.
            #        self._pool_item_id_to_is_acquired[id(pool_item)] = True
            #
            #        return pool_item
            #
            #That said, this introduces additional complexity that will require
            #unit testing. So, only do so if the above is actually profiled as
            #being faster. It almost certainly is, but let's be certain please.

            # List associated with this key.
            #
            # If this is the first access of this key, this "defaultdict"
            # implicitly creates a new list and associates this key with that
            # list; else, this is the list previously associated with this key.
            #
            # Note that this statement implicitly raises a "TypeError"
            # exception if this key is unhashable, which is certainly more
            # efficient than our explicitly validating this constraint.
            pool = self._key_to_pool[key]

            # Pool item associated with this key, defined as either...
            pool_item = (
                # The last item popped (i.e., removed) from this list...
                pool.pop()
                # If the list associated with this key is non-empty (i.e., this
                # method has been called less frequently than the corresponding
                # release() method for this key);
                if pool else
                # Else, the list associated with this key is empty (i.e., this
                # method has been called more frequently than the release()
                # method for this key). In this case, an arbitrary object
                # associated with this key.
                self._pool_item_maker(key)
            )

            # If debugging, record this item to have now been acquired.
            if is_debug:
                self._pool_item_id_to_is_acquired[id(pool_item)] = True

            # Return this item.
            return pool_item


    def release(
        self,

        # Mandatory parameters.
        item: object,

        # Optional parameters.
        key: Hashable = None,
        is_debug: bool = False,
    ) -> None:
        '''
        Release the passed object acquired by a prior call to the
        :meth:`acquire` method passed the same passed **arbitrary key** (i.e.,
        hashable object).

        Specifically, this method tests whether there exists a list
        previously associated with this key. If not, this method creates a new
        empty list associated with this key. In either case, this method then
        appends this object to this list.

        Parameters
        ----------
        item : object
            Arbitrary object previously associated with this key.
        key : Optional[HashableType]
            Hashable object previously associated with this pool item. Defaults
            to ``None``.
        is_debug : bool, optional
            ``True`` only if enabling inefficient debugging logic. Notably,
            enabling this option raises an exception if this item was *not*
            previously acquired. Defaults to ``False``.

        Raises
        ----------
        TypeError
            If this key is unhashable (i.e. *not* a key).
        _BeartypeUtilCachedKeyPoolException
            If debugging *and* this pool item was not acquired (i.e., returned
            by a prior call to the :meth:`acquire` method), in which case this
            item is ineligible for release.
        '''

        # In a thread-safe manner...
        with self._thread_lock:
            # If debugging...
            if is_debug:
                # Integer uniquely identifying this previously acquired pool
                # item.
                item_id = id(item)

                # If this item was *NOT* previously acquired, raise an
                # exception.
                if not self._pool_item_id_to_is_acquired.get(item_id, False):
                    raise _BeartypeUtilCachedKeyPoolException(
                        f'Unacquired key pool item {repr(item)} '
                        f'not releasable.'
                    )

                # Record this item to have now been released.
                self._pool_item_id_to_is_acquired[item_id] = False

            # Append this item to the pool associated with this key.
            self._key_to_pool[key].append(item)
