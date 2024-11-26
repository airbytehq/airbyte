#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) type variable
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`-compliant :attr:`typing.TypeVar` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsuper import TypeHint
from beartype.door._cls.pep.doorpep484604 import UnionTypeHint
# from beartype.roar import BeartypeDoorPepUnsupportedException
from beartype.typing import (
    TYPE_CHECKING,
    Any,
    Tuple,
    TypeVar,
)
from beartype._util.cache.utilcachecall import property_cached

# ....................{ SUBCLASSES                         }....................
class TypeVarTypeHint(UnionTypeHint):
    '''
    **Type variable wrapper** (i.e., high-level object encapsulating a low-level
    :pep:`484`-compliant :attr:`typing.TypeVar` type hint).
    '''

    # ..................{ STATIC                             }..................
    # Squelch false negatives from static type checkers.
    if TYPE_CHECKING:
        _hint: TypeVar

    # ..................{ PROPERTIES                         }..................
    @property
    def is_ignorable(self) -> bool:

        # This type variable is ignorable only if this type variable is either:
        # * Unconstrained by any bounds or constraints (and thus effectively
        #   bound only by the "typing.Any" catch-all).
        # * Bound by an ignorable bound: e.g.,
        #       TypeVar('T', bound=object)
        # * Constrained by one or more ignorable constraints. Since constraints
        #   effectively build a union over those constraints, even a single
        #   ignorable constraint suffices to render the entire type variable
        #   ignorable: e.g.,
        #       TypeVar('T', object)
        return self._is_args_ignorable

    # ..................{ PRIVATE ~ properties               }..................
    #FIXME: *HMM.* We should arguably just define the _make_args() factory
    #method instead. That implementation would become quite a bit simpler as
    #well as generalize to cover more use cases. By defining this method,
    #"self._args" and "self._args_wrapped_tuple" are now desynchronized. *sigh*

    @property  # type: ignore[misc]
    @property_cached
    def _args_wrapped_tuple(self) -> Tuple[TypeHint, ...]:

        #FIXME: Support covariance and contravariance, please. We don't
        #particularly care about either at the moment. Moreover, runtime type
        #checkers were *NEVER* expected to support either -- although we
        #eventually intend to do so. For now, raising a fatal exception here
        #would seem to be extreme overkill. Doing nothing is (probably) better
        #than doing something reckless and wild.
        # # Human-readable string describing the variance of this type variable if
        # # any *OR* "None" otherwise (i.e., if this type variable is invariant).
        # variance_str = None
        # if self._hint.__covariant__:
        #     variance_str = 'covariant'
        # elif self._hint.__contravariant__:
        #     variance_str = 'contravariant'
        #
        # # If this type variable is variant, raise an exception.
        # if variance_str:
        #     raise BeartypeDoorPepUnsupportedException(
        #         f'Type hint {repr(self._hint)} '
        #         f'variance "{variance_str}" currently unsupported.'
        #     )
        # # Else, this type variable is invariant.

        # TypeVars may only be bound or constrained, but not both. The
        # difference between the two has semantic meaning for static type
        # checkers but relatively little meaning for us. Ultimately, we're only
        # concerned with the set of compatible types present in either the bound
        # or the constraints. So, we treat a type variable as a union of its
        # constraints or bound. See also:
        #     https://docs.python.org/3/library/typing.html#typing.TypeVar

        # If this type variable is bounded, return the 1-tuple containing only
        # this wrapped bound.
        if self._hint.__bound__ is not None:
            return (TypeHint(self._hint.__bound__),)
        # Else, this type variable is unbounded.
        #
        # If this type variable is constrained, return the n-tuple containing
        # each of these wrapped constraints.
        elif self._hint.__constraints__:
            return tuple(TypeHint(t) for t in self._hint.__constraints__)
        # Else, this type variable is unconstrained.

        #FIXME: Consider globalizing this as a private constant for efficiency.
        # Return the 1-tuple containing only the "typing.Any" catch-all. Why?
        # Because an unconstrained and unbounded type variable is semantically
        # equivalent to a type variable bounded by "typing.Any".
        return (TypeHint(Any),)
