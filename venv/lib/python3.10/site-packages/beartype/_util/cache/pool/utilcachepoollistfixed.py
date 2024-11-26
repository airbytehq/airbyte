#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Fixed list pool** (i.e., submodule whose thread-safe API caches previously
instantiated :class:`list` subclasses constrained to fixed lengths defined at
instantiation time of various lengths for space- and time-efficient reuse
by the :func:`beartype.beartype` decorator across decoration calls).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Consider submitting the "FixedList" type as a relevant StackOverflow
#answer here:
#    https://stackoverflow.com/questions/10617045/how-to-create-a-fix-size-list-in-python
#    https://stackoverflow.com/questions/51558015/implementing-efficient-fixed-size-fifo-in-python

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCachedFixedListException
from beartype.typing import NoReturn
from beartype._util.cache.pool.utilcachepool import KeyPool
from beartype._util.text.utiltextrepr import represent_object

# ....................{ CONSTANTS                          }....................
FIXED_LIST_SIZE_MEDIUM = 256
'''
Reasonably large length to constrain acquired and released fixed lists to.

This constant is intended to be passed to the :func:`acquire_fixed_list`
function, which then returns a fixed list of this length suitable for use in
contexts requiring a "reasonably large" list -- where "reasonably" and "large"
are both subjective but *should* cover 99.9999% of use cases in this codebase.
'''

# ....................{ CLASSES                            }....................
class FixedList(list):
    '''
    **Fixed list** (i.e., :class:`list` constrained to a fixed length defined
    at instantiation time).**

    A fixed list is effectively a mutable tuple. Whereas a tuple is immutable
    and thus prohibits changes to its contained items, a fixed list is mutable
    and thus *permits* changes to its contained items.

    Design
    ----------
    This list enforces this constraint by overriding *all* :class:`list` dunder
    and standard methods that would otherwise modify the length of this list
    (e.g., :meth:`list.__delitem__`, :meth:`list.append`) to instead
    unconditionally raise an :class:`_BeartypeUtilCachedFixedListException`
    exception.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = ()

    # ..................{ INITIALIZER                        }..................
    def __init__(self, size: int) -> None:
        '''
        Initialize this fixed list to the passed length and all items of this
        fixed list to ``None``.

        Parameters
        ----------
        size : IntType
            Length to constrain this fixed list to.

        Raises
        ----------
        _BeartypeUtilCachedFixedListException
            If this length is either not an integer *or* is but is
            **non-positive** (i.e., is less than or equal to 0).
        '''

        # If this length is *NOT* an integer, raise an exception.
        if not isinstance(size, int):
            raise _BeartypeUtilCachedFixedListException(
                f'Fixed list length {repr(size)} not integer.')
        # Else, this length is an integer.

        # If this length is non-positive, raise an exception.
        if size <= 0:
            raise _BeartypeUtilCachedFixedListException(
                f'Fixed list length {size} <= 0.')
        # Else, this length is positive.

        # Make it so with the standard Python idiom for preallocating list
        # space -- which, conveniently, is also the optimally efficient means
        # of doing so. See also the timings in this StackOverflow answer:
        #     https://stackoverflow.com/a/10617221/2809027
        super().__init__([None]*size)

    # ..................{ GOOD ~ non-dunders                 }..................
    # Permit non-dunder methods preserving list length but otherwise requiring
    # overriding.

    def copy(self) -> 'FixedList':

        # Nullified fixed list of the same length as this fixed list.
        list_copy = FixedList(len(self))

        # Slice over the nullified contents of this copy with those of this
        # fixed list.
        list_copy[:] = self

        # Return this copy.
        return list_copy

    # ..................{ BAD ~ dunders                      }..................
    # Prohibit dunder methods modifying list length by overriding these methods
    # to raise exceptions.

    def __delitem__(self, index) -> NoReturn:
        raise _BeartypeUtilCachedFixedListException(
            f'{self._label} index {repr(index)} not deletable.')


    def __iadd__(self, value) -> NoReturn:  # type: ignore[misc]
        raise _BeartypeUtilCachedFixedListException(
            f'{self._label} not addable by {represent_object(value)}.')


    def __imul__(self, value) -> NoReturn:  # type: ignore[misc]
        raise _BeartypeUtilCachedFixedListException(
            f'{self._label} not multipliable by {represent_object(value)}.')

    # ..................{ BAD ~ dunders : setitem            }..................
    #FIXME: Great idea, if efficiency didn't particularly matter. Since
    #efficiency is the entire raison d'etre of this class, however, this method
    #has been temporarily and probably permanently disabled. Extensive
    #profiling has shown this single method to substantially cost us elsewhere.
    #Moreover, this method is only relevant in the context of preventing
    #external callers who are *NOT* us from violating class constraints. No
    #external callers exist, though! We are it. Since we know better, we won't
    #violate class constraints by changing fixed list length with slicing.
    #Moreover, it's unlikely we ever even assign list slices anywhere. *sigh*

    # def __setitem__(self, index, value):
    #
    #     # If these parameters indicate an external attempt to change the length
    #     # of this fixed length with slicing, raise an exception.
    #     self._die_if_slice_len_ne_value_len(index, value)
    #
    #     # If this index is a tuple of 0-based indices and slice objects...
    #     if isinstance(index, Iterable):
    #         # For each index or slice in this tuple...
    #         for subindex in index:
    #             # If these parameters indicate an external attempt to change
    #             # the length of this fixed length with slicing, raise an
    #             # exception.
    #             self._die_if_slice_len_ne_value_len(subindex, value)
    #
    #     # Else, this list is either not being sliced or is but is being set to
    #     # an iterable of the same length as that slice. In either case, this
    #     # operation preserves the length of this list and is thus acceptable.
    #     return super().__setitem__(index, value)


    #FIXME: Disabled as currently only called by __setitem__(). *sigh*
    # def _die_if_slice_len_ne_value_len(self, index, value) -> None:
    #     '''
    #     Raise an exception only if the passed parameters when passed to the
    #     parent :meth:`__setitem__` dunder method signify an external attempt to
    #     change the length of this fixed length with slicing.
    #
    #     This function is intended to be called by the :meth:`__setitem__`
    #     dunder method to validate the passed parameters.
    #
    #     Parameters
    #     ----------
    #     index
    #         0-based index, slice object, or tuple of 0-based indices and slice
    #         objects to index this fixed list with.
    #     value
    #         Object to set this index(s) of this fixed list to.
    #
    #     Raises
    #     ----------
    #     _BeartypeUtilCachedFixedListException
    #         If this index is a **slice object** (i.e., :class:`slice` instance
    #         underlying slice syntax) and this value is either:
    #
    #         * **Unsized** (i.e., unsupported by the :func:`len` builtin).
    #         * Sized but has a length differing from that of this fixed list.
    #     '''
    #
    #     # If this index is *NOT* a slice, silently reduce to a noop.
    #     if not isinstance(index, slice):
    #         return
    #     # Else, this index is a slice.
    #     #
    #     # If this value is *NOT* a sized container, raise an exception.
    #     elif not isinstance(value, Sized):
    #         raise _BeartypeUtilCachedFixedListException(
    #             f'{self._label} slice {repr(index)} not settable to unsized '
    #             f'{represent_object(value)}.'
    #         )
    #     # Else, this value is a sized container.
    #
    #     # 0-based first and one-past-the-last indices sliced by this slice.
    #     start, stop_plus_one, _ = index.indices(len(self))
    #
    #     # Number of items of this fixed list sliced by this slice. By
    #     # definition, this is guaranteed to be a non-negative integer.
    #     slice_len = stop_plus_one - start
    #
    #     # Number of items of this sized container to set this slice to.
    #     value_len = len(value)
    #
    #     # If these two lengths differ, raise an exception.
    #     if slice_len != value_len:
    #         raise _BeartypeUtilCachedFixedListException(
    #             f'{self._label} slice {repr(index)} of length {slice_len} not '
    #             f'settable to {represent_object(value)} of differing '
    #             f'length {value_len}.'
    #         )

    # ..................{ BAD ~ non-dunders                  }..................
    # Prohibit non-dunder methods modifying list length by overriding these
    # methods to raise exceptions.

    def append(self, obj) -> NoReturn:
        raise _BeartypeUtilCachedFixedListException(
            f'{self._label} not appendable by {represent_object(obj)}.')


    def clear(self) -> NoReturn:
        raise _BeartypeUtilCachedFixedListException(
            f'{self._label} not clearable.')


    def extend(self, obj) -> NoReturn:
        raise _BeartypeUtilCachedFixedListException(
            f'{self._label} not extendable by {represent_object(obj)}.')


    def pop(self, *args) -> NoReturn:
        raise _BeartypeUtilCachedFixedListException(
            f'{self._label} not poppable.')


    def remove(self, *args) -> NoReturn:
        raise _BeartypeUtilCachedFixedListException(
            f'{self._label} not removable.')

    # ..................{ PRIVATE ~ property                 }..................
    # Read-only properties intentionally prohibiting mutation.

    @property
    def _label(self) -> str:
        '''
        Human-readable representation of this fixed list trimmed to a
        reasonable length.

        This string property is intended to be interpolated into exception
        messages and should probably *not* be called in contexts where
        efficiency is a valid concern.
        '''

        # One-liners for magnanimous pusillanimousness.
        return f'Fixed list {represent_object(self)}'

# ....................{ PRIVATE ~ factories                }....................
_fixed_list_pool = KeyPool(item_maker=FixedList)
'''
Thread-safe **fixed list pool** (i.e., :class:`KeyPool` singleton caching
previously instantiated :class:`FixedList` instances of various lengths).

Caveats
----------
**Avoid accessing this private singleton externally.** Instead, call the public
:func:`acquire_fixed_list` and :func:`release_fixed_list` functions, which
efficiently validate both input *and* output to conform to sane expectations.
'''

# ....................{ (ACQUIRERS|RELEASERS)              }....................
def acquire_fixed_list(size: int) -> FixedList:
    '''
    Acquire an arbitrary **fixed list** (i.e., :class:`list` constrained to a
    fixed length defined at instantiation time) with the passed length.

    Caveats
    ----------
    **The contents of this list are arbitrary.** Callers should make *no*
    assumptions as to this list's initial items, but should instead
    reinitialize this list immediately after acquiring this list with standard
    list slice syntax: e.g.,

        >>> from beartype._util.cache.pool.utilcachepoollistfixed import (
        ...     acquire_fixed_list)
        >>> fixed_list = acquire_fixed_list(size=5)
        >>> fixed_list[:] = ('Dirty', 'Deads', 'Done', 'Dirt', 'Cheap',)

    Parameters
    ----------
    size : int
        Length to constrain the fixed list to be acquired to.

    Returns
    ----------
    FixedList
        Arbitrary fixed list with this length.

    Raises
    ----------
    _BeartypeUtilCachedFixedListException
        If this length is either not an integer *or* is but is
        **non-positive** (i.e., is less than or equal to 0).
    '''
    # Note that the FixedList.__init__() method already validates this "size"
    # parameter to be an integer.

    # Thread-safely acquire a fixed list of this length.
    fixed_list = _fixed_list_pool.acquire(size)
    assert isinstance(fixed_list, FixedList), (
        f'{repr(fixed_list)} not fixed list.')

    # Return this list.
    return fixed_list


def release_fixed_list(fixed_list: FixedList) -> None:
    '''
    Release the passed fixed list acquired by a prior call to the
    :func:`acquire_fixed_list` function.

    Caveats
    ----------
    **This list is not safely accessible after calling this function.** Callers
    should make *no* attempts to read, write, or otherwise access this list,
    but should instead nullify *all* variables referring to this list
    immediately after releasing this list (e.g., by setting these variables to
    the ``None`` singleton *or* by deleting these variables): e.g.,

        >>> from beartype._util.cache.pool.utilcachepoollistfixed import (
        ...     acquire_fixed_list, release_fixed_list)
        >>> fixed_list = acquire_fixed_list(size=7)
        >>> fixed_list[:] = ('If', 'You', 'Want', 'Blood', "You've", 'Got', 'It',)
        >>> release_fixed_list(fixed_list)
        # Either do this...
        >>> fixed_list = None
        # Or do this.
        >>> del fixed_list

    Parameters
    ----------
    fixed_list : FixedList
        Previously acquired fixed list to be released.
    '''
    assert isinstance(fixed_list, FixedList), (
        f'{repr(fixed_list)} not fixed list.')

    # Thread-safely release this fixed list.
    _fixed_list_pool.release(key=len(fixed_list), item=fixed_list)
