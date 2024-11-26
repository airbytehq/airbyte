#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`585`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep585Exception
from beartype.typing import (
    Any,
    Set,
)
from beartype._cave._cavefast import HintGenericSubscriptedType
from beartype._data.hint.datahinttyping import TypeException
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype._util.utilobject import Iota
from beartype._data.hint.datahinttyping import TupleTypes

# ....................{ HINTS                              }....................
HINT_PEP585_TUPLE_EMPTY = (
    tuple[()] if IS_PYTHON_AT_LEAST_3_9 else Iota())  # type: ignore[misc]
'''
:pep:`585`-compliant empty fixed-length tuple type hint if the active Python
interpreter supports at least Python 3.9 and thus :pep:`585` *or* a unique
placeholder object otherwise to guarantee failure when comparing arbitrary
objects against this object via equality tests.
'''

# ....................{ VALIDATORS                         }....................
def die_unless_hint_pep585_generic(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep585Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a :pep:`585`-compliant
    **generic** (i.e., class superficially subclassing at least one subscripted
    :pep:`585`-compliant pseudo-superclass).

    Parameters
    ----------
    hint : object
        Object to be validated.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`exception_cls`
        If this object is *not* a :pep:`585`-compliant generic.
    '''

    # If this object is *NOT* a PEP 585-compliant generic, raise an exception.
    if not is_hint_pep585_generic(hint):
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not PEP 585 generic.')
    # Else, this object is a PEP 585-compliant generic.

# ....................{ TESTERS                            }....................
# If the active Python interpreter targets at least Python >= 3.9 and thus
# supports PEP 585, correctly declare this function.
if IS_PYTHON_AT_LEAST_3_9:
    def is_hint_pep585_builtin(hint: object) -> bool:

        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
            is_hint_pep484585_generic)

        # Return true only if this hint...
        return (
            # Is either a PEP 484- or -585-compliant subscripted generic or
            # PEP 585-compliant builtin *AND*...
            isinstance(hint, HintGenericSubscriptedType) and
            # Is *NOT* a PEP 484- or -585-compliant subscripted generic.
            not is_hint_pep484585_generic(hint)
        )


    @callable_cached
    def is_hint_pep585_generic(hint: object) -> bool:  # pyright: ignore[reportGeneralTypeIssues]

        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
            get_hint_pep484585_generic_type_or_none)

        # If this hint is *NOT* a type, reduce this hint to the object
        # originating this hint if any. See the comparable
        # is_hint_pep484_generic() tester for further details.
        hint = get_hint_pep484585_generic_type_or_none(hint)

        # Tuple of all pseudo-superclasses originally subclassed by the passed
        # hint if this hint is a generic *OR* false otherwise.
        hint_bases_erased = getattr(hint, '__orig_bases__', False)

        # If this hint subclasses *NO* pseudo-superclasses, this hint *CANNOT*
        # be a generic. In this case, immediately return false.
        if not hint_bases_erased:
            return False
        # Else, this hint subclasses one or more pseudo-superclasses.

        # For each such pseudo-superclass...
        #
        # Unsurprisingly, PEP 585-compliant generics have absolutely *NO*
        # commonality with PEP 484-compliant generics. While the latter are
        # trivially detectable as subclassing "typing.Generic" after type
        # erasure, the former are *NOT*. The only means of deterministically
        # deciding whether or not a hint is a PEP 585-compliant generic is if:
        # * That class defines both the __class_getitem__() dunder method *AND*
        #   the "__orig_bases__" instance variable. Note that this condition in
        #   and of itself is insufficient to decide PEP 585-compliance as a
        #   generic. Why? Because these dunder attributes have been
        #   standardized under various PEPs and may thus be implemented by
        #   *ANY* arbitrary classes.
        # * The "__orig_bases__" instance variable is a non-empty tuple.
        # * One or more objects listed in that tuple are PEP 585-compliant
        #   objects.
        #
        # Note we could technically also test that this hint defines the
        # __class_getitem__() dunder method. Since this condition suffices to
        # ensure that this hint is a PEP 585-compliant generic, however, there
        # exists little benefit to doing so.
        for hint_base_erased in hint_bases_erased:  # type: ignore[union-attr]
            # If this pseudo-superclass is itself a PEP 585-compliant type
            # hint, return true.
            if is_hint_pep585_builtin(hint_base_erased):
                return True
            # Else, this pseudo-superclass is *NOT* PEP 585-compliant. In this
            # case, continue to the next pseudo-superclass.

        # Since *NO* such pseudo-superclasses are PEP 585-compliant, this hint
        # is *NOT* a PEP 585-compliant generic. In this case, return false.
        return False

# Else, the active Python interpreter targets at most Python < 3.9 and thus
# fails to support PEP 585. In this case, fallback to declaring this function
# to unconditionally return False.
else:
    def is_hint_pep585_builtin(hint: object) -> bool:
        return False

    def is_hint_pep585_generic(hint: object) -> bool:
        return False

# ....................{ TESTERS ~ doc                      }....................
# Docstring for this function regardless of implementation details.
is_hint_pep585_builtin.__doc__ = '''
    ``True`` only if the passed object is a C-based :pep:`585`-compliant
    **builtin type hint** (i.e., C-based type hint instantiated by subscripting
    either a concrete builtin container class like :class:`list` or
    :class:`tuple` *or* an abstract base class (ABC) declared by the
    :mod:`collections.abc` submodule like :class:`collections.abc.Iterable` or
    :class:`collections.abc.Sequence`).

    Note that this additionally includes all third-party type hints whose
    classes subclass the :class:`types.GenericAlias` superclass, including:

    * ``numpy.typing.NDArray[...]`` type hints.

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This test returns false for** :pep:`585`-compliant **generics,** which
    fail to satisfy the same API as all other :pep:`585`-compliant type hints.
    Why? Because :pep:`560`-type erasure erases this API on :pep:`585`-compliant
    generics immediately after those generics are declared, preventing their
    subsequent detection as :pep:`585`-compliant. Instead, :pep:`585`-compliant
    generics are only detectable by calling either:

    * The high-level PEP-agnostic
      :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep484585_generic`
      tester.
    * The low-level :pep:`585`-specific :func:`is_hint_pep585_generic` tester.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a :pep:`585`-compliant type hint.
    '''


is_hint_pep585_generic.__doc__ = '''
    ``True`` only if the passed object is a :pep:`585`-compliant **generic**
    (i.e., object that may *not* actually be a class originally subclassing at
    least one subscripted :pep:`585`-compliant pseudo-superclass).

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a :pep:`585`-compliant generic.
    '''

# ....................{ GETTERS                            }....................
def get_hint_pep585_generic_bases_unerased(
    # Mandatory parameters.
    hint: Any,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep585Exception,
    exception_prefix: str = '',
) -> tuple:
    '''
    Tuple of all unerased :pep:`585`-compliant **pseudo-superclasses** (i.e.,
    :mod:`typing` objects originally listed as superclasses prior to their
    implicit type erasure under :pep:`560`) of the passed :pep:`585`-compliant
    **generic** (i.e., class subclassing at least one non-class
    :pep:`585`-compliant object).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    ----------
    Tuple[object]
        Tuple of the one or more unerased pseudo-superclasses of this
        :pep:`585`-compliant generic.

    Raises
    ----------
    :exc:`exception_cls`
        If this hint is *not* a :pep:`585`-compliant generic.

    See Also
    ----------
    :func:`beartype._util.hint.pep.proposal.pep484585.utilpep484585generic.get_hint_pep484585_generic_bases_unerased`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
        get_hint_pep484585_generic_type_or_none)

    # If this hint is *NOT* a class, reduce this hint to the object originating
    # this hint if any. See the is_hint_pep484_generic() tester for details.
    hint = get_hint_pep484585_generic_type_or_none(hint)

    # If this hint is *NOT* a PEP 585-compliant generic, raise an exception.
    die_unless_hint_pep585_generic(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # Return the tuple of all unerased pseudo-superclasses of this generic.
    # While the "__orig_bases__" dunder instance variable is *NOT* guaranteed
    # to exist for PEP 484-compliant generic types, this variable is guaranteed
    # to exist for PEP 585-compliant generic types. Thanks for small favours.
    return hint.__orig_bases__


@callable_cached
def get_hint_pep585_generic_typevars(hint: object) -> TupleTypes:
    '''
    Tuple of all **unique type variables** (i.e., subscripted :class:`TypeVar`
    instances of the passed :pep:`585`-compliant generic listed by the caller
    at hint declaration time ignoring duplicates) if any *or* the empty tuple
    otherwise.

    This getter is memoized for efficiency.

    Motivation
    ----------
    The current implementation of :pep:`585` under at least Python 3.9 is
    fundamentally broken with respect to parametrized generics. While `PEP
    484`_-compliant generics properly propagate type variables from
    pseudo-superclasses to subclasses, :pep:`585` fails to do so. This function
    "fills in the gaps" by recovering these type variables from parametrized
    :pep:`585`-compliant generics by iteratively constructing a new tuple from
    the type variables parametrizing all pseudo-superclasses of this generic.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    Tuple[TypeVar, ...]
        Either:

        * If this :pep:`585`-compliant generic defines a ``__parameters__``
          dunder attribute, the value of that attribute.
        * Else, the empty tuple.

    Raises
    ----------
    :exc:`BeartypeDecorHintPep585Exception`
        If this hint is *not* a :pep:`585`-compliant generic.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_typevars

    # Tuple of all pseudo-superclasses of this PEP 585-compliant generic.
    hint_bases = get_hint_pep585_generic_bases_unerased(hint)

    # Set of all type variables parametrizing these pseudo-superclasses.
    #
    # Note the following inefficient iteration *CANNOT* be reduced to an
    # efficient set comprehension, as each get_hint_pep_typevars() call returns
    # a tuple of type variables rather than single type variable to be added to
    # this set.
    hint_typevars: Set[type] = set()

    # For each such pseudo-superclass, add all type variables parametrizing
    # this pseudo-superclass to this set.
    for hint_base in hint_bases:
        # print(f'hint_base_typevars: {hint_base} [{get_hint_pep_typevars(hint_base)}]')
        hint_typevars.update(get_hint_pep_typevars(hint_base))

    # Return this set coerced into a tuple.
    return tuple(hint_typevars)
