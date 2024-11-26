#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **generic type hint
utilities** (i.e., callables generically applicable to both :pep:`484`-
and :pep:`585`-compliant generic classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype.typing import (
    Optional,
    Tuple,
)
from beartype._data.hint.datahinttyping import TypeException
from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cache.pool.utilcachepoollistfixed import (
    FIXED_LIST_SIZE_MEDIUM,
    acquire_fixed_list,
    release_fixed_list,
)
from beartype._util.hint.pep.proposal.pep484.utilpep484generic import (
    get_hint_pep484_generic_bases_unerased,
    is_hint_pep484_generic,
)
from beartype._util.hint.pep.proposal.utilpep585 import (
    get_hint_pep585_generic_bases_unerased,
    is_hint_pep585_generic,
)
from collections.abc import Iterable

# ....................{ TESTERS                            }....................
@callable_cached
def is_hint_pep484585_generic(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **generic** (i.e., object that may *not* actually be a
    class despite subclassing at least one PEP-compliant type hint that also
    may *not* actually be a class).

    Specifically, this tester returns :data:`True` only if this object is
    either:

    * A :pep:`585`-compliant generic as tested by the lower-level
      :func:`is_hint_pep585_generic` function.
    * A :pep:`484`-compliant generic as tested by the lower-level
      :func:`is_hint_pep484_generic` function.

    This tester is memoized for efficiency. Although the implementation
    trivially reduces to a one-liner, constant factors associated with that
    one-liner are non-negligible. Moreover, this tester is called frequently
    enough to warrant its reduction to an efficient lookup.

    Caveats
    ----------
    **Generics are not necessarily classes,** despite originally being declared
    as classes. Although *most* generics are classes, subscripting a generic
    class usually produces a generic non-class that *must* nonetheless be
    transparently treated as a generic class: e.g.,

    .. code-block:: python

       >>> from typing import Generic, TypeVar
       >>> S = TypeVar('S')
       >>> T = TypeVar('T')
       >>> class MuhGeneric(Generic[S, T]): pass
       >>> non_class_generic = MuhGeneric[S, T]
       >>> isinstance(non_class_generic, type)
       False

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if this object is a generic.

    See Also
    ----------
    :func:`beartype._util.hint.pep.utilpeptest.is_hint_pep_typevars`
        Commentary on the relation between generics and parametrized hints.
    '''

    # Return true only if this hint is...
    return (
        # A PEP 484-compliant generic. Note this test trivially reduces to
        # an O(1) operation and is thus tested first.
        is_hint_pep484_generic(hint) or
        # A PEP 585-compliant generic. Note this test is O(n) in n the
        # number of pseudo-superclasses originally subclassed by this
        # generic and is thus tested last.
        is_hint_pep585_generic(hint)
    )

# ....................{ GETTERS ~ bases                    }....................
def get_hint_pep484585_generic_bases_unerased(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> Tuple[object, ...]:
    '''
    Tuple of the one or more **unerased pseudo-superclasses** (i.e.,
    PEP-compliant objects originally listed as superclasses prior to their
    implicit type erasure under :pep:`560`) of the passed :pep:`484`- or
    :pep:`585`-compliant **generic** (i.e., class superficially subclassing at
    least one PEP-compliant type hint that is possibly *not* an actual class) if
    this object is a generic *or* raise an exception otherwise (i.e., if this
    object is either not a class *or* is a class subclassing no non-class
    PEP-compliant objects).

    This getter is guaranteed to return a non-empty tuple. By definition, a
    generic is a type subclassing one or more generic superclasses.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This function should always be called in lieu of attempting to directly
    access the low-level** ``__orig_bases__`` **dunder instance variable.**
    Most PEP-compliant type hints fail to declare that variable, guaranteeing
    :class:`AttributeError` exceptions from all general-purpose logic
    attempting to directly access that variable. Thus this function, which
    "fills in the gaps" by implementing this oversight.

    **This function returns tuples possibly containing a mixture of actual
    superclasses and pseudo-superclasses superficially masquerading as actual
    superclasses subscripted by one or more PEP-compliant child hints or type
    variables** (e.g., ``(typing.Iterable[T], typing.Sized[T])``). Indeed, most
    type hints used as superclasses produced by subscripting PEP-compliant type
    hint factories are *not* actually types but singleton objects devilishly
    masquerading as types. Most actual :mod:`typing` superclasses are private,
    fragile, and prone to alteration or even removal between Python versions.

    Motivation
    ----------
    :pep:`560` (i.e., "Core support for typing module and generic types)
    formalizes the ``__orig_bases__`` dunder attribute first informally
    introduced by the :mod:`typing` module's implementation of :pep:`484`.
    Naturally, :pep:`560` remains as unusable as :pep:`484` itself. Ideally,
    :pep:`560` would have generalized the core intention of preserving each
    original user-specified subclass tuple of superclasses as a full-blown
    ``__orig_mro__`` dunder attribute listing the original method resolution
    order (MRO) of that subclass had that tuple *not* been modified.

    Naturally, :pep:`560` did no such thing. The original MRO remains obfuscated
    and effectively inaccessible. While computing that MRO would technically be
    feasible, doing so would also be highly non-trivial, expensive, and fragile.
    Instead, this function retrieves *only* the tuple of :mod:`typing`-specific
    pseudo-superclasses that this object's class originally attempted (but
    failed) to subclass.

    You are probably now agitatedly cogitating to yourself in the darkness: "But
    @leycec: what do you mean :pep:`560`? Wasn't :pep:`560` released *after*
    :pep:`484`? Surely no public API defined by the Python stdlib would be so
    malicious as to silently alter the tuple of base classes listed by a
    user-defined subclass?"

    As we've established both above and elsewhere throughout the codebase,
    everything developed for :pep:`484` -- including :pep:`560`, which derives
    its entire raison d'etre from :pep:`484` -- are fundamentally insane. In
    this case, :pep:`484` is insane by subjecting parametrized :mod:`typing`
    types employed as base classes to "type erasure," because:

         ...it is common practice in languages with generics (e.g. Java,
         TypeScript).

    Since Java and TypeScript are both terrible languages, blindly
    recapitulating bad mistakes baked into such languages is an equally bad
    mistake. In this case, "type erasure" means that the :mod:`typing` module
    *intentionally* destroys runtime type information for nebulous and largely
    unjustifiable reasons (i.e., Big Daddy Java and TypeScript do it, so it
    must be unquestionably good).

    Specifically, the :mod:`typing` module intentionally munges :mod:`typing`
    types listed as base classes in user-defined subclasses as follows:

    * All base classes whose origin is a builtin container (e.g.,
      ``typing.List[T]``) are reduced to that container (e.g., :class:`list`).
    * All base classes derived from an abstract base class declared by the
      :mod:`collections.abc` subpackage (e.g., ``typing.Iterable[T]``) are
      reduced to that abstract base class (e.g., ``collections.abc.Iterable``).
    * All surviving base classes that are parametrized (e.g.,
      ``typing.Generic[S, T]``) are stripped of that parametrization (e.g.,
      :class:`typing.Generic`).

    Since there exists no counterpart to the :class:`typing.Generic` superclass,
    the :mod:`typing` module preserves that superclass in unparametrized form.
    Naturally, this is useless, as an unparametrized :class:`typing.Generic`
    superclass conveys no meaningful type information. All other superclasses
    are reduced to their non-:mod:`typing` counterparts: e.g.,

        .. code-block:: python

        >>> from typing import TypeVar, Generic, Iterable, List
        >>> T = TypeVar('T')
        >>> class UserDefinedGeneric(List[T], Iterable[T], Generic[T]): pass
        # This is type erasure.
        >>> UserDefinedGeneric.__mro__
        (list, collections.abc.Iterable, Generic)
        # This is type preservation -- except the original MRO is discarded.
        # So, it's not preservation; it's reduction! We take what we can get.
        >>> UserDefinedGeneric.__orig_bases__
        (typing.List[T], typing.Iterable[T], typing.Generic[T])
        # Guess which we prefer?

    So, we prefer the generally useful ``__orig_bases__`` dunder tuple over the
    generally useless ``__mro__`` dunder tuple. Note, however, that the latter
    *is* still occasionally useful and thus occasionally returned by this
    getter. For inexplicable reasons, **single-inherited protocols** (i.e.,
    classes directly subclassing *only* the :pep:`544`-compliant
    :attr:`typing.Protocol` abstract base class (ABC)) are *not* subject to type
    erasure and thus constitute a notable exception to this heuristic:

        .. code-block:: python

        >>> from typing import Protocol
        >>> class UserDefinedProtocol(Protocol): pass
        >>> UserDefinedProtocol.__mro__
        (__main__.UserDefinedProtocol, typing.Protocol, typing.Generic, object)
        >>> UserDefinedProtocol.__orig_bases__
        AttributeError: type object 'UserDefinedProtocol' has no attribute
        '__orig_bases__'

    Welcome to :mod:`typing` hell, where even :mod:`typing` types lie broken and
    misshapen on the killing floor of overzealous theory-crafting purists.

    Parameters
    ----------
    hint : object
        Generic type hint to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    ----------
    Tuple[object]
        Tuple of the one or more unerased pseudo-superclasses of this generic.

    Raises
    ----------
    exception_cls
        If this hint is either:

        * Neither a :pep:`484`- nor :pep:`585`-compliant generic.
        * A :pep:`484`- nor :pep:`585`-compliant generic subclassing *no*
          pseudo-superclasses.

    Examples
    ----------
        >>> import typing
        >>> from beartype._util.hint.pep.utilpepget import (
        ...     get_hint_pep484585_generic_bases_unerased)
        >>> T = typing.TypeVar('T')
        >>> class MuhIterable(typing.Iterable[T], typing.Container[T]): pass
        >>> get_hint_pep585_generic_bases_unerased(MuhIterable)
        (typing.Iterable[~T], typing.Container[~T])
        >>> MuhIterable.__mro__
        (MuhIterable,
         collections.abc.Iterable,
         collections.abc.Container,
         typing.Generic,
         object)
    '''

    # Tuple of either...
    #
    # Note this implicitly raises a "BeartypeDecorHintPepException" if this
    # object is *NOT* a PEP-compliant generic. Ergo, we need not explicitly
    # validate that above.
    hint_pep_generic_bases_unerased = (
        # If this is a PEP 585-compliant generic, all unerased
        # pseudo-superclasses of this PEP 585-compliant generic.
        #
        # Note that this unmemoized getter accepts keyword arguments.
        get_hint_pep585_generic_bases_unerased(
            hint=hint,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
        if is_hint_pep585_generic(hint) else
        # Else, this *MUST* be a PEP 484-compliant generic. In this case, all
        # unerased pseudo-superclasses of this PEP 484-compliant generic.
        #
        # Note that this memoized getter prohibits keyword arguments.
        get_hint_pep484_generic_bases_unerased(
            hint,
            exception_cls,
            exception_prefix,
        )
    )

    # If this generic subclasses *NO* pseudo-superclass, raise an exception.
    #
    # Note this should have already been guaranteed on our behalf by:
    # * If this generic is PEP 484-compliant, the "typing" module.
    # * If this generic is PEP 585-compliant, CPython or PyPy itself.
    if not hint_pep_generic_bases_unerased:
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        raise exception_cls(
            f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
            f'subclasses no superclasses.'
        )
    # Else, this generic subclasses one or more pseudo-superclasses.

    # Return this tuple of these pseudo-superclasses.
    return hint_pep_generic_bases_unerased

# ....................{ GETTERS ~ type                     }....................
#FIXME: Unit test us up, please.
def get_hint_pep484585_generic_type(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> type:
    '''
    Either the passed :pep:`484`- or :pep:`585`-compliant **generic** (i.e.,
    class superficially subclassing at least one PEP-compliant type hint that is
    possibly *not* an actual class) if **unsubscripted** (i.e., indexed by *no*
    arguments or type variables), the unsubscripted generic underlying this
    generic if **subscripted** (i.e., indexed by one or more child type hints
    and/or type variables), *or* raise an exception otherwise (i.e., if this
    hint is *not* a generic).

    Specifically, this getter returns (in order):

    * If this hint originates from an **origin type** (i.e., isinstanceable
      class such that *all* objects satisfying this hint are instances of that
      class), this type regardless of whether this hint is already a class.
    * Else if this hint is already a class, this hint as is.
    * Else, raise an exception.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This getter returns false positives in edge cases.** That is, this getter
    returns non-``None`` values for both generics and non-generics -- notably,
    non-generics defining the ``__origin__`` dunder attribute to an
    isinstanceable class. Callers *must* perform subsequent tests to distinguish
    these two cases.

    Parameters
    ----------
    hint : object
        Generic type hint to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    ----------
    type
        Class originating this generic.

    Raises
    ----------
    :exc:`exception_cls`
        If this hint is *not* a generic.

    See Also
    ----------
    :func:`get_hint_pep484585_generic_type_or_none`
        Further details.
    '''

    # Either this hint if this hint is an unsubscripted generic, the
    # unsubscripted generic underlying this hint if this hint is a subscripted
    # generic, *OR* "None" if this hint is not a generic.
    hint_generic_type = get_hint_pep484585_generic_type_or_none(hint)

    # If this hint is *NOT* a generic, raise an exception.
    if hint_generic_type is None:
        raise exception_cls(
            f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
            f'not generic (i.e., originates from no isinstanceable class).'
        )
    # Else, this hint is a generic.

    # Return this class.
    return hint_generic_type


def get_hint_pep484585_generic_type_or_none(hint: object) -> Optional[type]:
    '''
    Either the passed :pep:`484`- or :pep:`585`-compliant **generic** (i.e.,
    class superficially subclassing at least one PEP-compliant type hint that is
    possibly *not* an actual class) if **unsubscripted** (i.e., indexed by *no*
    arguments or type variables), the unsubscripted generic underlying this
    generic if **subscripted** (i.e., indexed by one or more child type hints
    and/or type variables), *or* ``None`` otherwise (i.e., if this hint is *not*
    a generic).

    Specifically, this getter returns (in order):

    * If this hint originates from an **origin type** (i.e., isinstanceable
      class such that *all* objects satisfying this hint are instances of that
      class), this type regardless of whether this hint is already a class.
    * Else if this hint is already a class, this hint as is.
    * Else, ``None``.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This getter returns false positives in edge cases.** That is, this getter
    returns non-``None`` values for both generics and non-generics -- notably,
    non-generics defining the ``__origin__`` dunder attribute to an
    isinstanceable class. Callers *must* perform subsequent tests to distinguish
    these two cases.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    Optional[type]
        Either:

        * If this hint is a generic, the class originating this generic.
        * Else, ``None``.

    See Also
    ----------
    :func:`get_hint_pep_origin_or_none`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_origin_or_none

    # Arbitrary object originating this hint if any *OR* "None" otherwise.
    hint_origin = get_hint_pep_origin_or_none(hint)
    # print(f'{repr(hint)} hint_origin: {repr(hint_origin)}')

    # If this origin is a type, this is the origin type originating this hint.
    # In this case, return this type.
    if isinstance(hint_origin, type):
        return hint_origin
    # Else, this origin is *NOT* a type.
    #
    # Else if this hint is already a type, this type is effectively already its
    # origin type. In this case, return this type as is.
    elif isinstance(hint, type):
        return hint
    # Else, this hint is *NOT* a type. In this case, this hint originates from
    # *NO* origin type.

    # Return the "None" singleton.
    return None

# ....................{ FINDERS                            }....................
def find_hint_pep484585_generic_module_base_first(
    # Mandatory parameters.
    hint: object,
    module_name: str,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> type:
    '''
    Iteratively find and return the first **unerased superclass** (i.e.,
    unerased pseudo-superclass that is an actual superclass) transitively
    defined under the third-party package or module with the passed name
    subclassed by the unsubscripted generic type underlying the passed
    :pep:`484`- or :pep:`585`-compliant **generic** (i.e., object that may *not*
    actually be a class despite subclassing at least one PEP-compliant type hint
    that also may *not* actually be a class).

    This finder is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Although doing so *would* dramatically
    improve the efficiency of this finder, doing so:

    * Would require all passed parameters be passed positionally, which becomes
      rather cumbersome given the number of requisite parameters.
    * Is (currently) unnecessary, as all callers of this function are themselves
      already memoized.

    Motivation
    ----------
    This finder is typically called to reduce **descriptive generics** (i.e.,
    generics defined in third-party packages intended to be used *only* as
    descriptive type hints rather than actually instantiated as objects as most
    generics are) to the isinstanceable classes those generics describe.
    Although the mere existence of descriptive generics should be considered to
    be a semantic (if not syntactic) violation of :pep:`484`, the widespread
    proliferation of descriptive generics leaves :mod:`beartype` with little
    choice but to grin wanly and bear the pain they subject us to. As example,
    this finder is currently called elsewhere to:

    * Reduce Pandera type hints (e.g., `pandera.typing.DataFrame[...]`) to the
      Pandas types they describe (e.g., `pandas.DataFrame`).
    * Reduce NumPy type hints (e.g., `numpy.typing.NDArray[...]`) to the
      NumPy types they describe (e.g., `numpy.ndarray`).

    See examples below for further discussion.

    Parameters
    ----------
    hint : object
        Generic type hint to be inspected.
    module_name : str
        Fully-qualified name of the third-party package or module to find the
        first class in this generic type hint of.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    ----------
    type
        First unerased superclass transitively defined under this package or
        module subclassed by the unsubscripted generic type underlying this
        generic type hint.

    Examples
    ----------
        >>> from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
        ...     find_hint_pep484585_generic_base_first_in_module)

        # Reduce a Pandera type hint to the Pandas type it describes.
        >>> from pandera import DataFrameModel
        >>> from pandera.typing import DataFrame
        >>> class MuhModel(DataFrameModel): pass
        >>> find_hint_pep484585_generic_base_first_in_module(
        ...     hint=DataFrame[MuhModel], module_name='pandas', ...)
        <class 'pandas.DataFrame'>
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'

    # Avoid circular import dependencies.
    from beartype._util.module.utilmodget import get_object_module_name_or_none

    # Either:
    # * If this generic is unsubscripted, this unsubscripted generic type as is.
    # * If this generic is subscripted, the unsubscripted generic type
    #   underlying this subscripted generic (e.g., the type
    #   "pandera.typing.pandas.DataFrame" given the type hint
    #   "pandera.typing.DataFrame[...]").
    hint_type = get_hint_pep484585_generic_type(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # Fully-qualified name of the module to be searched for suffixed by a "."
    # delimiter. This is a micro-optimization improving lookup speed below.
    module_name_prefix = f'{module_name}.'

    # Tuple of the one or more unerased pseudo-superclasses which this
    # unsubscripted generic type originally subclassed prior to type erasure.
    #
    # Note that we could also inspect the method-resolution order (MRO) of this
    # type via the "hint.__mro__" dunder tuple, but that doing so would only
    # needlessly reduce the efficiency of the following iteration by
    # substantially increasing the number of iterations required to find the
    # desired superclass and thus the worst-case complexity of that iteration.
    hint_type_bases = get_hint_pep484585_generic_bases_unerased(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # For each unerased pseudo-superclass of this unsubscripted generic type...
    for hint_base in hint_type_bases:
        # If this pseudo-superclass is *NOT* an actual superclass, silently
        # ignore this non-superclass and continue to the next pseudo-superclass.
        if not isinstance(hint_base, type):
            continue
        # Else, this pseudo-superclass is an actual superclass.

        # Fully-qualified name of the module declaring this superclass if any
        # *OR* "None" otherwise (i.e., if this type is only defined in-memory).
        hint_base_module_name = get_object_module_name_or_none(hint_base)

        # If this module exists *AND* either...
        if hint_base_module_name and (
            # This module is the desired module itself *OR*...
            hint_base_module_name == module_name_prefix or
            # This module is a submodule of the desired module...
            hint_base_module_name.startswith(module_name_prefix)
        # Then return this superclass.
        ):
            # print(f'Found generic {repr(hint)} type {repr(hint_type)} "{module_name}" superclass {repr(hint_base)}!')
            return hint_base
        # Else, this is *NOT* the desired module. In this case, continue to the
        # next superclass.
    # Else, *NO* superclass of this generic resides in the desired module.

    # Raise an exception of the passed type.
    raise exception_cls(
        f'{exception_prefix}PEP 484 or 585 generic {repr(hint)} '
        f'type {repr(hint_type)} subclasses no "{module_name}" type '
        f'(i.e., type with module name prefixed by "{module_name}" not '
        f'found in method resolution order (MRO) {repr(hint_type.__mro__)}).'
    )

# ....................{ ITERATORS                          }....................
#FIXME: Unit test us up, please.
def iter_hint_pep484585_generic_bases_unerased_tree(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> Iterable:
    '''
    Breadth-first search (BFS) generator iteratively yielding the one or more
    unignorable unerased transitive pseudo-superclasses originally declared as
    superclasses prior to their type erasure of the passed :pep:`484`- or
    :pep:`585`-compliant generic.

    This generator yields the full tree of all pseudo-superclasses by
    transitively visiting both all direct pseudo-superclasses of this generic
    *and* all indirect pseudo-superclasses transitively superclassing all direct
    pseudo-superclasses of this generic. For efficiency, this generator is
    internally implemented with an efficient imperative First In First Out
    (FILO) queue rather than an inefficient (and dangerous, due to both
    unavoidable stack exhaustion and avoidable infinite recursion) tree of
    recursive function calls.

    Motivation
    ----------
    Ideally, a BFS would *not* be necessary. Instead, pseudo-superclasses
    visited by this BFS should be visitable as is via whatever external parent
    BFS is currently iterating over the tree of all transitive type hints (e.g.,
    our code generation algorithm implemented by the
    :func:`beartype._check.code.codemake.make_func_wrapper_code` function).
    That's how we transitively visit all other kinds of type hints, right?
    Sadly, that simple solution fails to scale to all possible edge cases that
    arise with generics. Why? Because our code generation algorithm sensibly
    requires that *only* unignorable hints may be enqueued onto its outer BFS.
    Generics confound that constraint. Some pseudo-superclasses are
    paradoxically:

    * Ignorable from the perspective of code generation. *No* type-checking code
      should be generated for these pseudo-superclasses. See reasons below.
    * Unignorable from the perspective of algorithm visitation. These
      pseudo-superclasses generate *no* code but may themselves subclass other
      pseudo-superclasses for which type-checking code should be generated and
      which must thus be visited by our outer BFS.

    Paradoxical pseudo-superclasses include:

    * User-defined :pep:`484`-compliant subgenerics (i.e., user-defined generics
      subclassing one or more parent user-defined generic superclasses).
    * User-defined :pep:`544`-compliant subprotocols (i.e., user-defined
      protocols subclassing one or more parent user-defined protocol
      superclasses).

    Consider this example :pep:`544`-compliant subprotocol:

        >>> import typing as t
        >>> class UserProtocol(t.Protocol[t.AnyStr]): pass
        >>> class UserSubprotocol(UserProtocol[str], t.Protocol): pass
        >>> UserSubprotocol.__orig_bases__
        (UserProtocol[str], typing.Protocol)  # <-- good
        >>> UserProtocolUnerased = UserSubprotocol.__orig_bases__[0]
        >>> UserProtocolUnerased is UserProtocol
        False
        >>> isinstance(UserProtocolUnerased, type)
        False  # <-- bad

    :pep:`585`-compliant generics suffer no such issues:

        >>> from beartype._util.hint.pep.proposal.utilpep585 import is_hint_pep585_builtin
        >>> class UserGeneric(list[int]): pass
        >>> class UserSubgeneric(UserGeneric[int]): pass
        >>> UserSubgeneric.__orig_bases__
        (UserGeneric[int],)
        >>> UserGenericUnerased = UserSubgeneric.__orig_bases__[0]
        >>> isinstance(UserGenericUnerased, type)
        True  # <-- good
        >>> UserGenericUnerased.__mro__
        (UserGeneric, list, object)
        >>> is_hint_pep585_builtin(UserGenericUnerased)
        True

    Iteratively walking up the unerased inheritance hierarchy for any such
    paradoxical generic or protocol subclass (e.g., ``UserSubprotocol`` but
    *not* ``UserSubgeneric`` above) would visit a user-defined generic or
    protocol pseudo-superclass subscripted by type variables. Due to poorly
    defined obscurities in the :mod:`typing` implementation, that
    pseudo-superclass is *not* actually a class but rather an instance of a
    private :mod:`typing` class (e.g., :class:`typing._SpecialForm`). This
    algorithm would then detect that pseudo-superclass as neither a generic nor
    a :mod:`typing` object and thus raise an exception. Fortunately, that
    pseudo-superclass conveys no meaningful intrinsic semantics with respect to
    type-checking; its only use is to register its own pseudo-superclasses (one
    or more of which could convey meaningful intrinsic semantics with respect to
    type-checking) for visitation by this BFS.

    Parameters
    ----------
    hint : object
        Generic type hint to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    ----------
    Iterable
        Breadth-first search (BFS) generator iteratively yielding the one or
        more unignorable unerased transitive pseudo-superclasses originally
        declared as superclasses prior to their type erasure of this generic.

    Raises
    ----------
    :exc:`exception_cls`
        If this hint is *not* a generic.

    See Also
    ----------
    :func:`get_hint_pep484585_generic_type_or_none`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.utilpep585 import (
        is_hint_pep585_builtin)
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
    from beartype._util.hint.pep.utilpeptest import is_hint_pep_typing
    from beartype._util.hint.utilhinttest import is_hint_ignorable

    # Tuple of the one or more unerased pseudo-superclasses originally listed as
    # superclasses prior to their type erasure by this generic.
    hint_bases_direct = get_hint_pep484585_generic_bases_unerased(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # print(f'generic {hint} hint_bases_direct: {hint_bases_direct}')

    # Fixed list of the one or more unerased transitive pseudo-superclasses
    # originally listed as superclasses prior to their type erasure by this
    # generic that have yet to be visited by the breadth-first search (BFS) over
    # these superclasses performed below.
    hint_bases = acquire_fixed_list(size=FIXED_LIST_SIZE_MEDIUM)

    # 0-based index of the currently visited pseudo-superclass of this list.
    hint_bases_index_curr = 0

    # 0-based index of one *PAST* the last pseudo-superclass of this list.
    hint_bases_index_past_last = len(hint_bases_direct)

    # Initialize this list to these direct pseudo-superclasses of this generic.
    hint_bases[0:hint_bases_index_past_last] = hint_bases_direct
    # print(f'generic pseudo-superclasses [initial]: {repr(hint_bases_direct}')

    # While the 0-based index of the next visited pseudo-superclass does *NOT*
    # exceed that of the last pseudo-superclass in this list, there remains one
    # or more pseudo-superclasses to be visited in this BFS.
    while hint_bases_index_curr < hint_bases_index_past_last:
        # Currently visited pseudo-superclass.
        hint_base = hint_bases[hint_bases_index_curr]
        # print(f'generic {hint} base: {repr(hint_base)}')

        # Sign uniquely identifying this pseudo-superclass if any *OR* "None".
        hint_base_sign = get_hint_pep_sign_or_none(hint_base)

        # If this pseudo-superclass is neither...
        if not (
            # A type conveying no meaningful typing semantics *NOR*...
            #
            # Note that types conveying no meaningful typing semantics are
            # effectively ignorable. Why? Because the caller already type-checks
            # this pith against the generic subclassing this superclass and thus
            # this superclass as well in an isinstance() call (e.g., in the
            # "PEP484585_CODE_HINT_GENERIC_PREFIX" snippet leveraged by the
            # "beartype._check.code.codemake" submodule).
            hint_base_sign is None or
            # An ignorable PEP-compliant type hint...
            is_hint_ignorable(hint_base)
        # Then this pseudo-superclass is unignorable. In this case...
        ):
            #FIXME: Unit test up this branch, please.
            # If this pseudo-superclass is...
            if (
                # A PEP-compliant generic *AND*...
                hint_base_sign is HintSignGeneric and
                # Is neither...
                not (
                    # A PEP 585-compliant superclass *NOR*...
                    is_hint_pep585_builtin(hint_base) and
                    # A PEP 484- nor 544-compliant superclass defined by the
                    # "typing" module...
                    is_hint_pep_typing(hint_base)
                )
            ):
            # Then this pseudo-superclass is a user-defined PEP 484-compliant
            # generic or 544-compliant protocol. In this case, generate *NO*
            # type-checking code for this pseudo-superclass; we only enqueue all
            # parent pseudo-superclasses of this pseudo-superclasses for
            # visitation by later iteration of this inner BFS.
            #
            # See "hints_bases" for explanatory commentary.
                # Tuple of the one or more parent pseudo-superclasses of this
                # child pseudo-superclass.
                hint_base_bases = (
                    get_hint_pep484585_generic_bases_unerased(
                        hint=hint_base,
                        exception_cls=exception_cls,
                        exception_prefix=exception_prefix,
                    ))

                # 0-based index of the last pseudo-superclass
                # of this list *BEFORE* adding onto this list.
                hint_bases_index_past_last_prev = (
                    hint_bases_index_past_last)

                # 0-based index of the last pseudo-superclass
                # of this list *AFTER* adding onto this list.
                hint_bases_index_past_last += len(hint_base_bases)

                # Enqueue these superclasses onto this list.
                hint_bases[
                    hint_bases_index_past_last_prev:
                    hint_bases_index_past_last
                ] = hint_base_bases
            # Else, this pseudo-superclass is neither an ignorable user-defined
            # PEP 484-compliant generic *NOR* an ignorable 544-compliant
            # protocol. In this case, yield this unignorable pseudo-superclass.
            else:
                yield hint_base
        # Else, this pseudo-superclass is ignorable.
        # else:
        #     print(f'Ignoring generic {repr(hint)} base {repr(hint_base)}...')
        #     print(f'Is generic {hint} base {repr(hint_base)} type? {isinstance(hint_base, type)}')

        # Nullify the previously visited pseudo-superclass in this list.
        hint_bases[hint_bases_index_curr] = None

        # Increment the 0-based index of the next visited pseudo-superclass in
        # this list *BEFORE* visiting that pseudo-superclass but *AFTER*
        # performing all other logic for the current pseudo-superclass.
        hint_bases_index_curr += 1

    # Release this list. Pray for salvation, for we find none here.
    release_fixed_list(hint_bases)
