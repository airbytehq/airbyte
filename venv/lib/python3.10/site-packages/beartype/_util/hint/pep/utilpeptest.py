#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint tester** (i.e., callable validating an
arbitrary object to be a PEP-compliant type hint) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.meta import URL_PEP585_DEPRECATIONS
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepUnsupportedException,
    BeartypeDecorHintPep484Exception,
    BeartypeDecorHintPep585DeprecationWarning,
)
from beartype.typing import NoReturn
from beartype._data.hint.datahinttyping import TypeException
from beartype._data.hint.pep.datapeprepr import (
    HINTS_PEP484_REPR_PREFIX_DEPRECATED)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_SUPPORTED,
    HINT_SIGNS_TYPE_MIMIC,
)
from beartype._data.module.datamodtyping import TYPING_MODULE_NAMES
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.pep484.utilpep484 import (
    is_hint_pep484_ignorable_or_none)
from beartype._util.hint.pep.proposal.utilpep544 import (
    is_hint_pep544_ignorable_or_none)
from beartype._util.hint.pep.proposal.utilpep593 import (
    is_hint_pep593_ignorable_or_none)
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.utilobject import get_object_type_unless_type
from warnings import warn

# ....................{ EXCEPTIONS                         }....................
def die_if_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPepException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception of the passed type if the passed object is a
    **PEP-compliant type hint** (i.e., :mod:`beartype`-agnostic annotation
    compliant with annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : object
        Object to be validated.
    exception_cls : Type[Exception], optional
        Type of the exception to be raised by this function. Defaults to
        :exc:`.BeartypeDecorHintPepException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    exception_cls
        If this object is a PEP-compliant type hint.
    '''

    # If this hint is PEP-compliant...
    if is_hint_pep(hint):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise an exception of this class.
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} is PEP-compliant '
            f'(e.g., rather than isinstanceable class).'
        )


def die_unless_hint_pep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPepException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-compliant type
    hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : object
        Object to be validated.
    exception_cls : Type[Exception], optional
        Type of the exception to be raised by this function. Defaults to
        :class:`.BeartypeDecorHintPepException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    exception_cls
        If this object is *not* a PEP-compliant type hint.
    '''

    # If this hint is *NOT* PEP-compliant, raise an exception.
    if not is_hint_pep(hint):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not PEP-compliant.')

# ....................{ EXCEPTIONS ~ supported             }....................
#FIXME: *DANGER.* This function makes beartype more fragile. Instead, refactor
#all or most calls to this function into calls to the
#warn_if_hint_pep_unsupported() function; then, consider excising this as well
#as exception classes (e.g., "BeartypeDecorHintPepUnsupportedException").
def die_if_hint_pep_unsupported(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception if the passed object is a **PEP-compliant unsupported
    type hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs currently *not* supported by the
    :func:`beartype.beartype` decorator).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Caveats
    -------
    **This validator only shallowly validates this object.** If this object is
    a subscripted PEP-compliant type hint (e.g., ``Union[str, List[int]]``),
    this validator ignores all subscripted arguments (e.g., ``List[int]``) on
    this hint and may thus return false positives for hints that are directly
    supported but whose subscripted arguments are not. To deeply validate this
    object, iteratively call this validator during a recursive traversal (such
    as a breadth-first search) over each subscripted argument of this object.

    Parameters
    ----------
    hint : object
        Object to be validated.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.
    BeartypeDecorHintPepUnsupportedException
        If this object is a PEP-compliant type hint but is currently
        unsupported by the :func:`beartype.beartype` decorator.
    BeartypeDecorHintPep484Exception
        If this object is the PEP-compliant :attr:`typing.NoReturn` type hint,
        which is contextually valid in only a single use case and thus
        supported externally by the :mod:`beartype._decor.wrap.wrapmain`
        submodule rather than with general-purpose automation.
    '''

    # If this object is a supported PEP-compliant type hint, reduce to a noop.
    #
    # Note that this memoized call is intentionally passed positional rather
    # than keyword parameters to maximize efficiency.
    if is_hint_pep_supported(hint):
        return
    # Else, this object is *NOT* a supported PEP-compliant type hint. In this
    # case, subsequent logic raises an exception specific to the passed
    # parameters.

    # If this hint is *NOT* PEP-compliant, raise an exception.
    die_unless_hint_pep(hint=hint, exception_prefix=exception_prefix)
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # Else, this hint is PEP-compliant.
    #
    # If this is the PEP 484-compliant "typing.NoReturn" type hint permitted
    # *ONLY* as a return annotation, raise an exception specific to this hint.
    if hint is NoReturn:
        raise BeartypeDecorHintPep484Exception(
            f'{exception_prefix}PEP 484 type hint "{repr(hint)}" '
            f'invalid in this type hint context (i.e., '
            f'"{repr(hint)}" valid only as non-nested return annotation).'
        )
    # Else, this is any PEP-compliant type hint other than "typing.NoReturn".

    # In this case, raise a general-purpose exception.
    #
    # Note that, by definition, the sign uniquely identifying this hint *SHOULD*
    # be in the "HINT_SIGNS_SUPPORTED" set. Regardless of whether it is or not,
    # we raise a similar exception in either case. Ergo, there is *NO* practical
    # benefit to validating that expectation here.
    raise BeartypeDecorHintPepUnsupportedException(
        f'{exception_prefix}type hint {repr(hint)} '
        f'currently unsupported by @beartype.'
    )

# ....................{ WARNINGS                           }....................
#FIXME: Resurrect support for the passed "warning_prefix" parameter. We've
#currently disabled this parameter as it's typically just a non-human-readable
#placeholder substring *NOT* intended to be exposed to end users (e.g.,
#"$%ROOT_PITH_LABEL/~"). For exceptions, we simply catch raised exceptions and
#replace such substrings with human-readable equivalents. Can we perform a
#similar replacement for warnings?

def warn_if_hint_pep_deprecated(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    warning_prefix: str = '',
) -> None:
    '''
    Emit a non-fatal warning if the passed PEP-compliant type hint is
    **deprecated** (i.e., obsoleted by an equivalent type hint or set of type
    hints standardized under one or more recent PEPs).

    This validator is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be inspected.
    warning_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        warning message. Defaults to the empty string.

    Warns
    -----
    BeartypeDecorHintPep585DeprecationWarning
        If this hint is a :pep:`484`-compliant type hint deprecated by
        :pep:`585` *and* the active Python interpreter targets Python >= 3.9.
    '''

    #FIXME: Uncomment *AFTER* resolving the "FIXME:" above.
    #FIXME: Unit test that this string contains *NO* non-human-readable
    #placeholder substrings. Note that the existing
    #"beartype_test.a00_unit.decor.code.test_codemain" submodule contains
    #relevant logic currently disabled for reasons that hopefully no longer
    #apply. *Urgh!*
    # assert isinstance(exception_prefix, str), f'{repr(exception_prefix)} not string.'

    # If this hint is a PEP 484-compliant type hint originating from an origin
    # type (e.g., "typing.List[int]"), this hint has been deprecated by the
    # equivalent PEP 585-compliant type hint (e.g., "list[int]"). In this case,
    # emit a non-fatal PEP 585-specific deprecation warning.
    if is_hint_pep_deprecated(hint):
        #FIXME: Resolve issue #73 by additionally passing the "stacklevel"
        #keyword parameter. Doing so will probably require:
        #* Refactoring this function to accept an *OPTIONAL*
        #  "warning_stack_level" parameter. Why optional? Because this
        #  parameter is only reliably decidable under Python interpreters
        #  defining the implementation-specific sys._getframe() function, which
        #  is admittedly all of them everyone cares about. Nonetheless, do this
        #  right. If non-"None", conditionally pass this level below as:
        #      stacklevel=(
        #          warning_stack_level
        #          if warning_stack_level is not None else
        #          1  # <-- the official default value for this parameter
        #      ),
        #* Refactoring all callers of this function to pass that parameter.
        #  Here's where things get dicey, however. Passing this parameter
        #  reliably (so, *NOT* just hard-coding a magic number somewhere and
        #  praying devoutly for the best) will require computing the distance
        #  between the current function and the first external third-party
        #  non-@beartype scope on the call stack. So, maybe we want to actually
        #  *NOT* refactor this function to accept an *OPTIONAL*
        #  "warning_stack_level" parameter but instead locally define
        #  "warning_stack_level" based on an iterative O(n) search up the
        #  stack? That's obviously non-ideal -- but still absolutely preferable
        #  to the current untenable situation of emitting unreadable warnings.
        #
        #Okay. So, scrap everything above. Let's instead:
        #* Define a new warn_safe() wrapper function (somewhere in
        #  "beartype._util", clearly) that automatically decides the
        #  appropriate "stacklevel" by iterating up the call stack to compute
        #  the distance between the current function and the first external
        #  third-party non-@beartype scope. We perform similar iteration when
        #  resolving PEP 563-based deferred annotations, so that would probably
        #  be the first place to clean inspiration. That code is rock solid and
        #  well-tested. Things get non-trivial fast here, sadly. *sigh*
        #
        #See also: https://docs.python.org/3/library/warnings.html#warnings.warn
        warn(
            (
                f'PEP 484 type hint {repr(hint)} deprecated by PEP 585. '
                f'This hint is scheduled for removal in the first Python '
                f'version released after October 5th, 2025. To resolve this, '
                f'import this hint from "beartype.typing" rather than "typing". '
                f'For further commentary and alternatives, see also:\n'
                f'    {URL_PEP585_DEPRECATIONS}'
            ),
            BeartypeDecorHintPep585DeprecationWarning,
        )
    # Else, this hint is *NOT* deprecated. In this case, reduce to a noop.


#FIXME: Unit test us up.
#FIXME: Actually use us in place of die_if_hint_pep_unsupported().
#FIXME: Actually, it's unclear whether we still require or desire this. See
#"_pephint" commentary for further details.
# def warn_if_hint_pep_unsupported(
#     # Mandatory parameters.
#     hint: object,
#
#     # Optional parameters.
#     exception_prefix: str = 'Annotated',
# ) -> bool:
#     '''
#     Return ``True`` and emit a non-fatal warning only if the passed object is a
#     **PEP-compliant unsupported type hint** (i.e., :mod:`beartype`-agnostic
#     annotation compliant with annotation-centric PEPs currently *not* supported
#     by the :func:`beartype.beartype` decorator).
#
#     This validator is effectively (but technically *not*) memoized. See the
#     :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.
#
#     Parameters
#     ----------
#     hint : object
#         Object to be validated.
#     exception_prefix : Optional[str]
#         Human-readable label prefixing this object's representation in the
#         warning message emitted by this function. Defaults to the empty string.
#
#     Returns
#     ----------
#     bool
#         ``True`` only if this PEP-compliant type hint is currently supported by
#         that decorator.
#
#     Raises
#     ----------
#     BeartypeDecorHintPepException
#         If this object is *not* a PEP-compliant type hint.
#
#     Warnings
#     ----------
#     BeartypeDecorHintPepUnsupportedWarning
#         If this object is a PEP-compliant type hint currently unsupported by
#         that decorator.
#     '''
#
#     # True only if this object is a supported PEP-compliant type hint.
#     #
#     # Note that this memoized call is intentionally passed positional rather
#     # than keyword parameters to maximize efficiency.
#     is_hint_pep_supported_test = is_hint_pep_supported(hint)
#
#     # If this object is an unsupported PEP-compliant type hint...
#     if not is_hint_pep_supported_test:
#         assert isinstance(exception_prefix, str), f'{repr(exception_prefix)} not string.'
#
#         # If this hint is *NOT* PEP-compliant, raise an exception.
#         die_unless_hint_pep(hint=hint, exception_prefix=exception_prefix)
#
#         # Else, this hint is PEP-compliant. In this case, emit a warning.
#         warn(
#             (
#                 f'{exception_prefix}PEP type hint {repr(hint)} '
#                 f'currently unsupported by @beartype.'
#             ),
#             BeartypeDecorHintPepUnsupportedWarning
#         )
#
#     # Return true only if this object is a supported PEP-compliant type hint.
#     return is_hint_pep_supported_test

# ....................{ TESTERS                            }....................
def is_hint_pep(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a **PEP-compliant type hint**
    (i.e., object either directly defined by the :mod:`typing` module *or* whose
    type subclasses one or more classes directly defined by the :mod:`typing`
    module).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Motivation
    ----------
    Standard Python types allow callers to test for compliance with protocols,
    interfaces, and abstract base classes by calling either the
    :func:`isinstance` or :func:`issubclass` builtins. This is the
    well-established Pythonic standard for deciding conformance to an API.

    Insanely, :pep:`484` *and* the :mod:`typing` module implementing :pep:`484`
    reject community standards by explicitly preventing callers from calling
    either the :func:`isinstance` or :func:`issubclass` builtins on most but
    *not* all :pep:`484` objects and types. Moreover, neither :pep:`484` nor
    :mod:`typing` implement public APIs for testing whether arbitrary objects
    comply with :pep:`484` or :mod:`typing`.

    Thus this function, which "fills in the gaps" by implementing this
    laughably critical oversight.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a PEP-compliant type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_sign_or_none)

    # Return true only if this object is uniquely identified by a sign and thus
    # a PEP-compliant type hint.
    return get_hint_pep_sign_or_none(hint) is not None


def is_hint_pep_deprecated(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a **PEP-compliant deprecated type
    hint** (i.e., obsoleted by an equivalent type hint or set of type hints
    standardized under one or more recent PEPs).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a PEP-compliant deprecated type
        hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhintget import get_hint_repr

    # Machine-readable representation of this hint.
    hint_repr = get_hint_repr(hint)

    # Substring of the machine-readable representation of this hint preceding
    # the first "[" delimiter if this representation contains that delimiter
    # *OR* this representation as is otherwise.
    #
    # Note that the str.partition() method has been profiled to be the
    # optimally efficient means of parsing trivial prefixes.
    hint_repr_bare, _, _ = hint_repr.partition('[')

    # Return true only if this hint is a PEP 484-compliant type hint originating
    # from an origin type (e.g., "typing.List[int]").
    return hint_repr_bare in HINTS_PEP484_REPR_PREFIX_DEPRECATED

# ....................{ TESTERS ~ ignorable                }....................
#FIXME: *EXTREMELY INEFFICIENT.* See commentary below, please.
def is_hint_pep_ignorable(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a **deeply ignorable PEP-compliant
    type hint** (i.e., PEP-compliant type hint shown to be ignorable only after
    recursively inspecting the contents of this hint).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as this tester is only safely callable
    by the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a deeply ignorable PEP-compliant
        type hint.

    Warns
    -----
    BeartypeDecorHintPepIgnorableDeepWarning
        If this object is a deeply ignorable PEP-compliant type hint. Why?
        Because deeply ignorable PEP-compliant type hints convey *no*
        meaningful semantics but superficially appear to do so. Consider
        ``Union[str, List[int], NewType('MetaType', Annotated[object, 53])]``,
        for example; this PEP-compliant type hint effectively reduces to
        :obj:`typing.Any` and thus conveys *no* meaningful semantics despite
        superficially appearing to do so.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
    # print(f'Testing PEP hint {repr(hint)} deep ignorability...')

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign(hint)

    #FIXME: *EXTREMELY INEFFICIENT*. What were we thinking? Honestly. This is an
    #O(N) operation when this should instead be an O(1) operation. Refactor
    #this immediately to instead resemble the
    #beartype._check.convert.checkreduce._reduce_hint_cached() function.
    #Notably:
    #* Define a new "_HINT_SIGN_TO_IS_HINT_PEP_IGNORABLE_TESTER" private global
    #  dictionary, refactored from the "_IS_HINT_PEP_IGNORABLE_TESTERS"
    #  iterable.
    #* Remove the "_IS_HINT_PEP_IGNORABLE_TESTERS" iterable.
    #* Refactor this logic to perform a simple lookup into this dictionary.
    #
    #We are facepalming ourselves as we speak.

    # For each PEP-specific function testing whether this hint is an ignorable
    # type hint fully compliant with that PEP...
    for is_hint_pep_ignorable_tester in _IS_HINT_PEP_IGNORABLE_TESTERS:
        # True only if this hint is a ignorable under this PEP, False only if
        # this hint is unignorable under this PEP, and None if this hint is
        # *NOT* compliant with this PEP.
        is_hint_pep_ignorable_or_none = is_hint_pep_ignorable_tester(
            hint, hint_sign)

        # If this hint is compliant with this PEP...
        # print(f'{is_hint_pep_ignorable_or_none} = {is_hint_pep_ignorable_tester}({hint}, {hint_sign})')
        if is_hint_pep_ignorable_or_none is not None:
            #FIXME: Uncomment *AFTER* we properly support type variables. Since
            #we currently ignore type variables, uncommenting this now would
            #raise spurious warnings for otherwise unignorable and absolutely
            #unsuspicious generics and protocols parametrized by type
            #variables, which would be worse than the existing situation.

            # # If this hint is ignorable under this PEP, warn the user this hint
            # # is deeply ignorable. (See the docstring for justification.)
            # if is_hint_pep_ignorable_or_none:
            #     warn(
            #         (
            #             f'Ignorable PEP type hint {repr(hint)} '
            #             f'typically not intended to be ignored.'
            #         ),
            #         BeartypeDecorHintPepIgnorableDeepWarning,
            #     )

            # Return this boolean.
            return is_hint_pep_ignorable_or_none
        # Else, this hint is *NOT* compliant with this PEP. In this case,
        # silently continue to the next such tester.

    # Else, this hint is *NOT* deeply ignorable. In this case, return false.
    return False

# ....................{ TESTERS ~ supported                }....................
@callable_cached
def is_hint_pep_supported(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a **PEP-compliant supported type
    hint** (i.e., :mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs currently supported by the
    :func:`beartype.beartype` decorator).

    This tester is memoized for efficiency.

    Caveats
    -------
    **This tester only shallowly inspects this object.** If this object is a
    subscripted PEP-compliant type hint (e.g., ``Union[str, List[int]]``), this
    tester ignores all subscripted arguments (e.g., ``List[int]``) on this hint
    and may thus return false positives for hints that are directly supported
    but whose subscripted arguments are not.

    To deeply inspect this object, iteratively call this tester during a
    recursive traversal over each subscripted argument of this object.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a supported PEP-compliant type hint.
    '''

    # If this hint is *NOT* PEP-compliant, immediately return false.
    if not is_hint_pep(hint):
        return False
    # Else, this hint is PEP-compliant.

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign(hint)

    # Return true only if this sign is supported.
    return hint_sign in HINT_SIGNS_SUPPORTED

# ....................{ TESTERS ~ typing                   }....................
#FIXME: Replace all hardcoded "'typing" strings throughout the codebase with
#access of "TYPING_MODULE_NAMES" instead. We only see one remaining in:
#* beartype._util.hint.pep.proposal.pep484.utilpep484.py
#Thankfully, nobody really cares about generalizing this one edge case to
#"testing_extensions", so it's mostly fine for various definitions of fine.
@callable_cached
def is_hint_pep_typing(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is an attribute of a **typing
    module** (i.e., module officially declaring attributes usable for creating
    PEP-compliant type hints accepted by both static and runtime type checkers).

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is an attribute of a typing module.
    '''
    # print(f'is_hint_pep_typing({repr(hint)}')

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_sign_or_none)

    # Return true only if this hint is either...
    return (
        # Any PEP-compliant type hint defined by a typing module (except those
        # maliciously masquerading as another type entirely) *OR*...
        get_object_module_name_or_none(hint) in TYPING_MODULE_NAMES or
        # Any PEP-compliant type hint defined by a typing module maliciously
        # masquerading as another type entirely.
        get_hint_pep_sign_or_none(hint) in HINT_SIGNS_TYPE_MIMIC
    )


def is_hint_pep_type_typing(hint: object) -> bool:
    '''
    :data:`True` only if either the passed object is defined by a **typing
    module** (i.e., module officially declaring attributes usable for creating
    PEP-compliant type hints accepted by both static and runtime type checkers)
    if this object is a class *or* the class of this object is defined by a
    typing module otherwise (i.e., if this object is *not* a class).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if either:

        * If this object is a class, this class is defined by a typing module.
        * Else, the class of this object is defined by a typing module.
    '''

    # This hint if this hint is a class *OR* this hint's class otherwise.
    hint_type = get_object_type_unless_type(hint)
    # print(f'pep_type_typing({repr(hint)}): {get_object_module_name(hint_type)}')

    # Return true only if this type is defined by a typing module.
    #
    # Note that this implementation could probably be reduced to the
    # leading portion of the body of the get_hint_pep_sign_or_none()
    # function testing this object's representation. While certainly more
    # compact and convenient than the current approach, that refactored
    # approach would also be considerably more fragile, failure-prone, and
    # subject to whimsical "improvements" in the already overly hostile
    # "typing" API. Why? Because the get_hint_pep_sign_or_none() function:
    # * Parses the machine-readable string returned by the __repr__()
    #   dunder method of "typing" types. Since that string is *NOT*
    #   standardized by PEP 484 or any other PEP, "typing" authors remain
    #   free to violate this pseudo-standard in any manner and at any time
    #   of their choosing.
    # * Suffers common edge cases for "typing" types whose __repr__()
    #   dunder methods fail to comply with the non-standard implemented by
    #   their sibling types. This includes the common "TypeVar" type.
    # * Calls this tester function to decide whether the passed object is a
    #   PEP-compliant type hint or not before subjecting that object to
    #   further introspection, which would clearly complicate implementing
    #   this tester function in terms of that getter function.
    #
    # In contrast, the current approach only tests the standard
    # "__module__" dunder attribute and is thus significantly more robust
    # against whimsical destruction by "typing" authors. Note that there
    # might exist an alternate means of deciding this boolean, documented
    # here merely for completeness:
    #     try:
    #         isinstance(obj, object)
    #         return False
    #     except TypeError as type_error:
    #         return str(type_error).endswith(
    #             'cannot be used with isinstance()')
    #
    # The above effectively implements an Aikido throw by using the fact
    # that "typing" types prohibit isinstance() calls against those types.
    # While clever (and deliciously obnoxious), the above logic:
    # * Requires catching exceptions in the common case and is thus *MUCH*
    #   less efficient than the preferable approach implemented here.
    # * Assumes that *ALL* "typing" types prohibit such calls. Sadly, only
    #   a proper subset of these types prohibit such calls.
    # * Assumes that those "typing" types that do prohibit such calls raise
    #   exceptions with reliable messages across *ALL* Python versions.
    #
    # In short, there is no general-purpose clever solution. *sigh*
    return hint_type.__module__ in TYPING_MODULE_NAMES

# ....................{ TESTERS ~ args                     }....................
#FIXME: Overkill. Replace directly with a simple test, please.
#
#Note that the corresponding unit test should be preserved, as that test is
#essential to ensuring sanity across type hints and Python versions.
def is_hint_pep_args(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a **subscripted PEP-compliant type
    hint** (i.e., PEP-compliant type hint directly indexed by one or more
    objects).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    -------
    **Callers should not assume that the objects originally subscripting this
    hint are still accessible.** Although *most* hints preserve their
    subscripted objects over their lifetimes, a small subset of edge-case hints
    erase those objects at subscription time. This includes:

    * :pep:`585`-compliant empty tuple type hints (i.e., ``tuple[()]``), which
      despite being explicitly subscripted erroneously erase that subscription
      at subscription time. This does *not* extend to :pep:`484`-compliant
      empty tuple type hints (i.e., ``typing.Tuple[()]``), which correctly
      preserve that subscripted empty tuple.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a subscripted PEP-compliant type
        hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # Return true only if this hint is subscripted by one or more arguments.
    return bool(get_hint_pep_args(hint))

# ....................{ TESTERS ~ typevars                 }....................
#FIXME: Overkill. Replace directly with a simple test, please.
#
#Note that the corresponding unit test should be preserved, as that test is
#essential to ensuring sanity across type hints and Python versions.
def is_hint_pep_typevars(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a PEP-compliant type hint
    parametrized by one or more **type variables** (i.e., instances of the
    :class:`TypeVar` class).

    This tester detects both:

    * **Direct parametrizations** (i.e., cases in which this object itself is
      directly parametrized by type variables).
    * **Superclass parametrizations** (i.e., cases in which this object is
      indirectly parametrized by one or more superclasses of its class being
      directly parametrized by type variables).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Semantics
    ---------
    **Generics** (i.e., PEP-compliant type hints whose classes subclass one or
    more public :mod:`typing` pseudo-superclasses) are often but *not* always
    typevared. For example, consider the untypevared generic:

        >>> from typing import List
        >>> class UntypevaredGeneric(List[int]): pass
        >>> UntypevaredGeneric.__mro__
        (__main__.UntypevaredGeneric, list, typing.Generic, object)
        >>> UntypevaredGeneric.__parameters__
        ()

    Likewise, typevared hints are often but *not* always generic. For example,
    consider the typevared non-generic:

        >>> from typing import List, TypeVar
        >>> TypevaredNongeneric = List[TypeVar('T')]
        >>> type(TypevaredNongeneric).__mro__
        (typing._GenericAlias, typing._Final, object)
        >>> TypevaredNongeneric.__parameters__
        (~T,)

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a PEP-compliant type hint
        parametrized by one or more type variables.

    Examples
    --------
        >>> import typing
        >>> from beartype._util.hint.pep.utilpeptest import (
        ...     is_hint_pep_typevars)
        >>> T = typing.TypeVar('T')
        >>> class UserList(typing.List[T]): pass
        # Unparametrized type hint.
        >>> is_hint_pep_typevars(typing.List[int])
        False
        # Directly parametrized type hint.
        >>> is_hint_pep_typevars(typing.List[T])
        True
        # Superclass-parametrized type hint.
        >>> is_hint_pep_typevars(UserList)
        True
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_typevars

    # Return true only if this hint is parametrized by one or more type
    # variables, trivially detected by testing whether the tuple of all type
    # variables parametrizing this hint is non-empty.
    return bool(get_hint_pep_typevars(hint))

# ....................{ PRIVATE ~ tuples                   }....................
_IS_HINT_PEP_IGNORABLE_TESTERS = (
    is_hint_pep484_ignorable_or_none,
    is_hint_pep544_ignorable_or_none,
    is_hint_pep593_ignorable_or_none,
)
'''
Tuple of all PEP-specific functions testing whether the passed object is an
ignorable type hint fully compliant with a specific PEP.

Each such function is expected to have a signature resembling:

.. code-block:: python

    def is_hint_pep{PEP_NUMBER}_ignorable_or_none(
        hint: object, hint_sign: HintSign) -> Optional[bool]:
        ...

Each such function is expected to return either:

* If the passed object is fully compliant with that PEP:

    * If this object is ignorable, :data:`True`.
    * Else, :data:`False`.

* If this object is *not* fully compliant with that PEP, :data:`None`.
'''
