#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) procedural
type-checkers** (i.e., high-level functions type-checking arbitrary objects
against PEP-compliant type hints at *any* time during the lifecycle of the
active Python process).
'''

# ....................{ TODO                               }....................
#FIXME: Re-enable type-narrowing (i.e., "typing.TypeGuard[...]") for both the
#is_bearable() function defined below *AND* TypeHint.is_bearable() method
#defined elsewhere *AFTER* resolving this effectively still-open issue:
#    https://github.com/beartype/beartype/issues/255
#
#Note that doing so will require upstream static type-checkers to explicitly
#support this use case, which they appear loathe to do. In short, this is
#unlikely to work this decade -- possibly, this century. The future depends upon
#us and we failed it, everybody! *gurgles*
#FIXME: Consider validating the signatures of both the is_bearable() function
#defined below *AND* TypeHint.is_bearable() method defined elsewhere to have
#returns annotated as "TypeGuard[T]" from the perspective of static
#type-checking. Sadly, doing so is extremely non-trivial -- requiring usage of a
#new mandatory "pytest-mypy-plugins" test-time dependency, which itself requires
#definition of mypy-specific cases in a new supplementary top-level directory.
#Honestly, it's all a bit insane. We just wish we could call mypy's fake
#reveal_type() function at runtime, honestly. *sigh*

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: This submodule intentionally does *not* import the
# @beartype.beartype decorator. Why? Because that decorator conditionally
# reduces to a noop under certain contexts (e.g., `python3 -O` optimization),
# whereas the API defined by this submodule is expected to unconditionally
# operate as expected regardless of the current context.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.door._doortyping import (
    # T,
    BeartypeTypeChecker,
)
from beartype.roar import (
    BeartypeCallHintReturnViolation,
    BeartypeDoorHintViolation,
)
from beartype.roar._roarexc import _BeartypeDoorTextException
from beartype._check.checkmake import make_func_tester
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)
# from beartype._data.hint.datahintfactory import TypeGuard
from beartype._decor.decorcache import beartype
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.error.utilerror import reraise_exception_placeholder
from beartype._util.hint.utilhinttest import die_unless_hint

# ....................{ VALIDATORS                         }....................
def die_if_unbearable(
    # Mandatory flexible parameters.
    obj: object,
    hint: object,

    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> None:
    '''
    Raise an exception if the passed arbitrary object violates the passed
    PEP-compliant type hint under the passed beartype configuration.

    Parameters
    ----------
    obj : object
        Arbitrary object to be tested against this hint.
    hint : object
        PEP-compliant type hint to test this object against.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to ``BeartypeConf()``, the default ``O(1)`` constant-time configuration.

    Raises
    ----------
    beartype.roar.BeartypeDecorHintNonpepException
        If this hint is *not* PEP-compliant (i.e., complies with *no* Python
        Enhancement Proposals (PEPs) currently supported by :mod:`beartype`).
    beartype.roar.BeartypeDecorHintPepUnsupportedException
        If this hint is currently unsupported by :mod:`beartype`.
    beartype.roar.BeartypeDoorHintViolation
        If this object violates this hint.

    Examples
    ----------
        >>> from beartype.door import die_if_unbearable
        >>> die_if_unbearable(['And', 'what', 'rough', 'beast,'], list[str])
        >>> die_if_unbearable(['its', 'hour', 'come', 'round'], list[int])
        beartype.roar.BeartypeDoorHintViolation: Object ['its', 'hour', 'come',
        'round'] violates type hint list[int], as list index 0 item 'its' not
        instance of int.
    '''

    # @beartype-decorated closure raising an
    # "BeartypeCallHintReturnViolation" exception when the parameter passed to
    # this closure violates the hint passed to this parent tester.
    _check_object = _get_object_checker(hint, conf)

    # Attempt to type-check this object by passing this object to this closure,
    # which then implicitly type-checks this object as a return value.
    try:
        _check_object(obj)
    # If this closure raises a beartype-specific exception implying that this
    # object violates this hint...
    except BeartypeCallHintReturnViolation as exception:
        # Exception message.
        exception_message = str(exception)

        # If this exception message is *NOT* prefixed by the expected substring,
        # raise an exception.
        #
        # Note that this should *NEVER* occur in production releases, but that
        # this could potentially occur during pre-production testing. Ergo, it
        # is worth explicitly checking but *NOT* worth investing time and effort
        # in raising a human-readable exception.
        if not exception_message.startswith(
            _TYPE_CHECKER_EXCEPTION_MESSAGE_PREFIX):
            raise _BeartypeDoorTextException(
                f'_check_object() exception '
                f'"{exception_message}" not prefixed by '
                f'"{_TYPE_CHECKER_EXCEPTION_MESSAGE_PREFIX}".'
            ) from exception
        # Else, this exception message is prefixed by the expected substring.

        # Replace the irrelevant substring prefixing this message with a
        # relevant substring applicable to this higher-level function.
        exception_message = (
            f'Object '
            f'{exception_message[_TYPE_CHECKER_EXCEPTION_MESSAGE_PREFIX_LEN:]}'
        )

        # Wrap this exception in a more readable higher-level exception.
        raise BeartypeDoorHintViolation(
            message=exception_message,
            culprits=exception.culprits,
        ) from exception
    # Else, this closure raised another exception. In this case, percolate this
    # exception back up this call stack.

# ....................{ TESTERS                            }....................
def is_subhint(subhint: object, superhint: object) -> bool:
    '''
    ``True`` only if the first passed hint is a **subhint** of the second passed
    hint, in which case this second hint is a **superhint** of this first hint.

    Equivalently, this tester returns ``True`` only if *all* of the following
    conditions apply:

    * These two hints are **semantically related** (i.e., convey broadly similar
      semantics enabling these two hints to be reasonably compared). For
      example:

      * ``callable.abc.Iterable[str]`` and ``callable.abc.Sequence[int]`` are
        semantically related. These two hints both convey container semantics.
        Despite their differing child hints, these two hints are broadly similar
        enough to be reasonably comparable.
      * ``callable.abc.Iterable[str]`` and ``callable.abc.Callable[[], int]``
        are *not* semantically related. Whereas the first hints conveys a
        container semantic, the second hint conveys a callable semantic. Since
        these two semantics are unrelated, these two hints are dissimilar
        enough to *not* be reasonably comparable.

    * The first hint is **semantically equivalent** to or **narrower** than the
      second hint. Equivalently:

      * The first hint matches less than or equal to the total number of all
        possible objects matched by the second hint.
      * The size of the countably infinite set of all possible objects matched
        by the first hint is less than or equal to that of those matched by the
        second hint.

    * The first hint is **compatible** with the second hint. Since the first
      hint is semantically narrower than the second, APIs annotated by the first
      hint may safely replace that hint with the second hint; doing so preserves
      backward compatibility.

    Parameters
    ----------
    subhint : object
        PEP-compliant type hint or type to be tested as the subhint.
    superhint : object
        PEP-compliant type hint or type to be tested as the superhint.

    Returns
    -------
    bool
        ``True`` only if this first hint is a subhint of this second hint.

    Examples
    --------
        >>> from beartype.door import is_subhint
        >>> is_subhint(int, int)
        True
        >>> is_subhint(Callable[[], list], Callable[..., Sequence[Any]])
        True
        >>> is_subhint(Callable[[], list], Callable[..., Sequence[int]])
        False
    '''

    # Avoid circular import dependencies.
    from beartype.door._cls.doorsuper import TypeHint

    # The one-liner is mightier than the... many-liner.
    return TypeHint(subhint).is_subhint(TypeHint(superhint))

# ....................{ TESTERS ~ is_bearable              }....................
#FIXME: Improve unit tests to exhaustively exercise edge cases, including:
#* Invalid hints. In this case, test that the raised exception is prefixed by
#  the expected substring rather than our exception placeholder.

def is_bearable(
    # Mandatory flexible parameters.
    obj: object,
    #FIXME: Re-enable after static type-checkers support "TypeGuard[T]". See above!
    # hint: T,
    hint: object,

    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
#FIXME: Re-enable after static type-checkers support "TypeGuard[T]". See above!
# ) -> TypeGuard[T]:
) -> bool:
    '''
    :data:`True` only if the passed arbitrary object satisfies the passed
    PEP-compliant type hint under the passed beartype configuration.

    Parameters
    ----------
    obj : object
        Arbitrary object to be tested against this hint.
    hint : object
        PEP-compliant type hint to test this object against.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to ``BeartypeConf()``, the default constant-time configuration.

    Returns
    ----------
    bool
        :data:`True` only if this object satisfies this hint.

    Raises
    ----------
    beartype.roar.BeartypeConfException
        If this configuration is *not* a :class:`BeartypeConf` instance.
    beartype.roar.BeartypeDecorHintForwardRefException
        If this hint contains one or more relative forward references, which
        this tester explicitly prohibits to improve both the efficiency and
        portability of calls to this tester.
    beartype.roar.BeartypeDecorHintNonpepException
        If this hint is *not* PEP-compliant (i.e., complies with *no* Python
        Enhancement Proposals (PEPs) currently supported by :mod:`beartype`).
    beartype.roar.BeartypeDecorHintPepUnsupportedException
        If this hint is currently unsupported by :mod:`beartype`.

    Examples
    ----------
        >>> from beartype.door import is_bearable
        >>> is_bearable(['Things', 'fall', 'apart;'], list[str])
        True
        >>> is_bearable(['the', 'centre', 'cannot', 'hold;'], list[int])
        False
    '''

    # Attempt to dynamically generate a memoized low-level type-checking
    # tester function returning true only if the object passed to that
    # tester satisfies the type hint passed to this high-level type-checking
    # tester function.
    #
    # Note that parameters are intentionally passed positionally for
    # efficiency. Since make_func_tester() is memoized, passing parameters
    # by keyword would raise a non-fatal
    # "_BeartypeUtilCallableCachedKwargsWarning" warning.
    try:
        func_tester = make_func_tester(hint, conf)
    # If any exception was raised, reraise this exception with each placeholder
    # substring (i.e., "EXCEPTION_PLACEHOLDER" instance) replaced by the passed
    # exception prefix.
    except Exception as exception:
        reraise_exception_placeholder(
            exception=exception, target_str='is_bearable() ')

    # Return true only if the passed object satisfies this hint.
    return func_tester(obj)  # pyright: ignore[reportUnboundVariable]

# ....................{ PRIVATE ~ getters                  }....................
#FIXME: Shift into a more public location for widespread usage elsewhere: e.g.,
#* Define a new "beartype._check.checkget" submodule.
#* Rename this function to get_object_checker() in that submodule.
#* Shift the "_TYPE_CHECKER_EXCEPTION_MESSAGE_PREFIX*" globals into that
#  submodule as well, probably publicized and renamed to:
#  * "CHECKER_EXCEPTION_MESSAGE_PREFIX".
#  * "CHECKER_EXCEPTION_MESSAGE_PREFIX_LEN".
#* *COPY* (i.e., do *NOT* move) the die_if_unbearable() into that submodule,
#  renamed to either:
#  * check_object(). This is the one, due to orthogonality with the
#    get_object_checker() getter.
#  * die_if_object_violates_hint(). Fairly long, but disambiguous.
#* Generalize check_object() to accept additional *MANDATORY* "exception_cls"
#  and "exception_prefix" parameters. Replace the currently hard-coded 'Object '
#  prefix in check_object() by "exception_prefix".
#* Refactor die_if_unbearable() in this submodule to defer entirely to
#  check_object() in that submodule.
#* Shift the "BeartypeTypeChecker" type hint into the existing
#  "beartype._data.hint.datahinttyping" submodule, publicized and renamed to
#  "BeartypeChecker".
#FIXME: And... the prior "FIXME:" comment is almost certainly obsolete already.
#Eventually, we want to eliminate this getter entirely in favour of dynamically
#generating a full-blown exception raiser specific to the passed hint. *shrig*
@callable_cached
def _get_object_checker(
    hint: object, conf: BeartypeConf) -> BeartypeTypeChecker:
    '''
    Create, cache, and return a **synthetic runtime type-checker** (i.e.,
    function raising a :exc:`.BeartypeCallHintReturnViolation` exception when
    the object passed to that function violates the hint passed to this parent
    getter under the passed beartype configuration).

    This factory intentionally raises :exc:`BeartypeCallHintReturnViolation`
    rather than :exc:`BeartypeCallHintParamViolation` exceptions. Since
    type-checking returns is *slightly* faster than type-checking parameters,
    this factory intentionally annotates the return rather than a parameter of
    this checker.

    This factory is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Type hint to validate *all* objects passed to the checker returned by
        this factory against.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring how this
        object is type-checked).

    Returns
    ----------
    BeartypeTypeChecker
        Synthetic runtime type-checker specific to this hint and configuration.

    Raises
    ----------
    beartype.roar.BeartypeDecorHintPepUnsupportedException
        If this hint is a PEP-compliant type hint currently unsupported by
        the :func:`beartype.beartype` decorator.
    beartype.roar.BeartypeDecorHintNonpepException
        If this hint is neither a:

        * Supported PEP-compliant type hint.
        * Supported PEP-noncompliant type hint.
    '''

    # If this hint is unsupported, raise an exception.
    #
    # Note that this technically duplicates a similar check performed by the
    # @beartype decorator below except that the exception prefix passed here
    # results in substantially more readable and relevant exceptions.
    die_unless_hint(hint=hint, exception_prefix='Functional ')
    # Else, this hint is supported.

    # @beartype-decorated closure raising an
    # "BeartypeCallHintReturnViolation" exception when the parameter passed to
    # this closure violates the hint passed to this parent tester.
    @beartype(conf=conf)
    def _die_if_unbearable(pith) -> hint:  # type: ignore[valid-type]
        return pith

    # Return this closure.
    return _die_if_unbearable

# ....................{ PRIVATE ~ constants                }....................
_TYPE_CHECKER_EXCEPTION_MESSAGE_PREFIX = (
    'Function '
    'beartype.door._doorcheck._get_object_checker._die_if_unbearable() '
    'return '
)
'''
Irrelevant substring prefixing *all* exception messages raised by *all*
**synthetic runtime type-checkers** (i.e., callables dynamically created and
returned by the :func:`._get_object_checker` getter).
'''


_TYPE_CHECKER_EXCEPTION_MESSAGE_PREFIX_LEN = (
    len(_TYPE_CHECKER_EXCEPTION_MESSAGE_PREFIX))
'''
Length of the irrelevant substring prefixing *all*
exception messages raised by *all* **synthetic runtime type-checkers** (i.e.,
callables dynamically created and returned by the :func:`._get_object_checker`
getter).
'''
