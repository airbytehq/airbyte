#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype cave-specific abstract base classes (ABCs).**
'''

# ....................{ TODO                               }....................
#FIXME: As with the parallel "beartype._cave.abc" submodule, refactor the
#contents of this private submodule into the newly proposed public
#"beartype.caver" submodule. To do so:
#
#* In the "beartype.caver" submodule:
#  * Define a new make_type() function copied from the
#    betse.util.type.classes.define_class() function (but renamed, obviously).
#  * Define a new make_type_defaultdict() function copied from the
#    betse.util.type.iterable.mapping.mapcls.DefaultDict() function, but with
#    signature resembling:
#    def make_type_defaultdict(
#        name: str,
#        missing_key_maker: CallableTypes,
#        items: (Iterable, type(None)),
#    ) -> type:
#    Internally, this function should call make_type() to do so.

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeCaveNoneTypeOrKeyException,
    BeartypeCaveNoneTypeOrMutabilityException,
)
from beartype._util.hint.nonpep.utilnonpeptest import (
    die_unless_hint_nonpep)
from typing import Any, Tuple, Union

# ....................{ CONSTANTS                          }....................
_NoneType: type = type(None)
'''
Type of the ``None`` singleton, duplicated from the :mod:`beartype.cave`
submodule to prevent cyclic import dependencies.
'''


_NoneTypes: Tuple[type, ...] = (_NoneType,)
'''
Tuple of only the type of the ``None`` singleton.
'''

# ....................{ HINTS                              }....................
_TypeTuple = Tuple[Union[type, str], ...]
'''
PEP-compliant type hint matching a **type tuple** (i.e., tuple containing only
types and forward references to deferred types specified as the fully-qualified
names of those types).
'''

# ....................{ CLASSES                            }....................
class _NoneTypeOrType(dict):
    '''
    :class:`NoneType` **tuple factory type** (i.e., :class:`dict` subclass,
    instances of which are dictionaries mapping from arbitrary types or tuples
    of types to the same types or tuples of types concatenated with the type of
    the ``None`` singleton).
    '''

    # ..................{ DUNDERS                            }..................
    def __setitem__(self, key: Any, value: Any) -> None:
        '''
        Dunder method explicitly called by the superclass on setting the passed
        key-value pair with``[``- and ``]``-delimited syntax.

        Specifically, this method prohibits external attempts to explicitly set
        key-value pairs on this factory by unconditionally raising an
        exception.

        Parameters
        ----------
        key : object
            Key to map this value to.
        value : object
            Value to be mapped to.

        Raises
        ----------
        BeartypeCaveNoneTypeOrMutabilityException
            Unconditionally.
        '''

        raise BeartypeCaveNoneTypeOrMutabilityException(
            f'{repr(self)} externally immutable (i.e., not settable).')


    def __missing__(self, hint: Union[type, str, _TypeTuple]) -> _TypeTuple:
        '''
        Dunder method explicitly called by the superclass
        :meth:`dict.__getitem__` method implicitly called on getting the passed
        missing key with ``[``- and ``]``-delimited syntax.

        Specifically, this method:

        * If a single type or string is passed:

          #. Creates a new 2-tuple containing only that object and the type of
             the ``None`` singleton.
          #. Maps the passed type to that 2-tuple.
          #. Returns that 2-tuple.

        * Else if a tuple of one or more types and/or strings is passed:

          #. Creates a new tuple appending the type of the ``None`` singleton
             to the passed tuple.
          #. Maps the passed type to the new tuple.
          #. Returns the new tuple.

        * Else, raises an exception.

        Parameters
        ----------
        hint : (type, str, _TypeTuple)
            Type, string, or tuple of one or more types and/or strings *not*
            currently cached by this factory.

        Returns
        ----------
        _TypeTuple
            Tuple of types appending the type of the ``None`` singleton to the
            passed type, string, or tuple of types and/or strings.

        Raises
        ----------
        BeartypeCaveNoneTypeOrKeyException
            If this key is neither:

            * A **string** (i.e., forward reference specified as either a
              fully-qualified or unqualified classname).
            * A **type** (i.e., class).
            * A **non-empty tuple** (i.e., semantic union of types) containing
              only strings and types.
        '''

        # If this missing key is *NOT* a PEP-noncompliant type hint, raise an
        # exception.
        die_unless_hint_nonpep(
            hint=hint,
            exception_prefix='"NoneTypeOr" key',
            exception_cls=BeartypeCaveNoneTypeOrKeyException,
        )

        # Tuple of types to be cached and returned by this call.
        hint_or_none: _TypeTuple = None  # type: ignore[assignment]

        # If this key is a type...
        if isinstance(hint, type):
            # If this type is "NoneType", reuse the existing "_NoneTypes" tuple
            # containing only this type.
            if hint is _NoneType:
                hint_or_none = _NoneTypes
            # Else, this type is *NOT* "NoneType". In this case, instantiate a
            # new tuple of types concatenating this type with "NoneType".
            else:
                hint_or_none = (hint, _NoneType)
        # Else if this key is a non-empty tuple...
        elif isinstance(hint, tuple):
            # If "NoneType" is already in this tuple, reuse this tuple as is.
            if _NoneType in hint:
                hint_or_none = hint
            # Else, "NoneType" is *NOT* already in this tuple. In this case,
            # instantiate a new tuple of types concatenating this tuple with
            # "NoneType".
            else:
                hint_or_none = hint + _NoneTypes
        # Else, this key is invalid. Thanks to the above call to the
        # die_unless_hint_nonpep() function, this should *NEVER* occur.
        # Nonetheless, raise a human-readable exception for sanity.
        else:
            raise BeartypeCaveNoneTypeOrKeyException(
                f'"NoneTypeOr" key {repr(hint)} unsupported.')

        # Return this new tuple.
        #
        # The superclass dict.__getitem__() dunder method then implicitly maps
        # the passed missing key to this new tuple of types by effectively:
        #     self[hint] = hint_or_none
        return hint_or_none

# ....................{ SINGLETONS                         }....................
NoneTypeOr: Any = _NoneTypeOrType()
'''
**:class:``NoneType`` tuple factory** (i.e., dictionary mapping from arbitrary
types or tuples of types to the same types or tuples of types concatenated with
the type of the ``None`` singleton).

This factory efficiently generates and caches tuples of types containing
:class:``NoneType`` from arbitrary user-specified types and tuples of types. To
do so, simply index this factory with any desired type *or* tuple of types; the
corresponding value will then be another tuple containing :class:``NoneType``
and that type *or* those types.

Motivation
----------
This factory is commonly used to type-hint **optional callable parameters**
(i.e., parameters defaulting to ``None`` when *not* explicitly passed by the
caller). Although such parameters may also be type-hinted with a tuple manually
containing :class:``NoneType``, doing so inefficiently recreates these tuples
for each optional callable parameter across the entire codebase.

This factory avoids such inefficient recreation. Instead, when indexed with any
arbitrary key:

* If that key has already been successfully accessed on this factory, this
  factory returns the existing value (i.e., tuple containing
  :class:``NoneType`` and that key if that key is a type *or* the items of that
  key if that key is a tuple) previously mapped and cached to that key.
* Else, if that key is:

  * A type, this factory:

    #. Creates a new tuple containing that type and :class:``NoneType``.
    #. Associates that key with that tuple.
    #. Returns that tuple.

  * A tuple of types, this factory:

    #. Creates a new tuple containing these types and :class:``NoneType``.
    #. Associates that key with that tuple.
    #. Returns that tuple.

  * Any other object, raises a human-readable
    :class:`beartype.roar.BeartypeCaveNoneTypeOrKeyException` exception.

This factory is analogous to the :pep:`484`_-compliant :class:`typing.Optional`
type despite otherwise *not* complying with :pep:`484`_.

Examples
----------
    # Function accepting an optional parameter with neither
    # "beartype.cave" nor "typing".
    >>> def to_autumn(season_of_mists: (str, type(None)) = None) -> str
    ...     return season_of_mists if season_of_mists is not None else (
    ...         'While barred clouds bloom the soft-dying day,')

    # Function accepting an optional parameter with "beartype.cave".
    >>> from beartype.cave import NoneTypeOr
    >>> def to_autumn(season_of_mists: NoneTypeOr[str] = None) -> str
    ...     return season_of_mists if season_of_mists is not None else (
    ...         'Then in a wailful choir the small gnats mourn')

    # Function accepting an optional parameter with "typing".
    >>> from typing import Optional
    >>> def to_autumn(season_of_mists: Optional[str] = None) -> str
    ...     return season_of_mists if season_of_mists is not None else (
    ...         'Or sinking as the light wind lives or dies;')
'''
