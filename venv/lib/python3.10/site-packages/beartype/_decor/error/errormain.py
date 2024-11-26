#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype exception raisers** (i.e., high-level callables raising
human-readable exceptions called by :func:`beartype.beartype`-decorated
callables on the first invalid parameter or return value failing a type-check
against the PEP-compliant type hint annotating that parameter or return).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Generalizing the "random_int" concept (i.e., the optional "random_int"
#parameter accepted by the get_beartype_violation() function) that enables
#O(1) rather than O(n) exception handling to containers that do *NOT* provide
#efficient random access like mappings and sets will be highly non-trivial.
#While there exist a number of alternative means of implementing that
#generalization, the most reasonable *BY FAR* is probably to:
#
#* Embed additional assignment expressions in the type-checking tests generated
#  by the make_func_wrapper_code() function that uniquely store the value of
#  each item, key, or value returned by each access of a non-indexable container
#  iterator into a new unique local variable. Note this unavoidably requires:
#  * Adding a new index to the "hint_curr_meta" tuples internally created by
#    that function -- named, say, "_HINT_META_INDEX_ITERATOR_NAME". The value
#    of the tuple item at this index should either be:
#    * If the currently iterated type hint is a non-indexable container, the
#      name of the new unique local variable assigned to by this assignment
#      expression whose value is obtained from the iterator cached for that
#      container.
#    * Else, "None".
#    Actually... hmm. Perhaps we only need a new local variable
#    "iterator_nonsequence_names" whose value is a cached "FixedList" of
#    sufficiently large size (so, "FIXED_LIST_SIZE_MEDIUM"?). We could then simply
#    iteratively insert the names of the wrapper-specific new unique local
#    variables into this list.
#    Actually... *WAIT.* Is all we need a single counter initialized to, say:
#        iterators_nonsequence_len = 0
#    We then both use that counter to:
#    * Uniquify the names of these wrapper-specific new unique local variables
#      during iteration over type hints.
#    * Trivially generate a code snippet passing a list of these names to the
#      "iterators_nonsequence" parameter of get_beartype_violation() function
#      after iteration over type hints.
#    Right. That looks like The Way, doesn't it? This would seem to be quite a
#    bit easier than we'd initially thought, which is always nice. Oi!
#  * Python >= 3.8, but that's largely fine. Python 3.6 and 3.7 are
#    increasingly obsolete in 2021.
#* Add a new optional "iterators_nonsequence" parameter to the
#  get_beartype_violation() function, accepting either:
#  * If the current parameter or return of the parent wrapper function was
#    annotated with one or more non-indexable container type hints, a *LIST* of
#    the *VALUES* of all unique local variables assigned to by assignment
#    expressions in that parent wrapper function. These values were obtained
#    from the iterators cached for those containers. To enable these exception
#    handlers to efficiently treat this list like a FIFO stack (e.g., with the
#    list.pop() method), this list should be sorted in the reverse order that
#    these assignment expressions are defined in.
#* Refactor exception handlers to then preferentially retrieve non-indexable
#  container items in O(1) time from this stack rather than simply iterating
#  over all container items in O(n) brute-force time. Obviously, extreme care
#  must be taken here to ensure that this exception handling algorithm visits
#  containers in the exact same order as visited by our testing algorithm.

# ....................{ IMPORTS                            }....................
from beartype.meta import URL_ISSUES
from beartype.roar._roarexc import (
    BeartypeCallHintViolation,
    BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation,
    _BeartypeCallHintPepRaiseException,
    _BeartypeCallHintPepRaiseDesynchronizationException,
)
from beartype.typing import (
    Callable,
    Dict,
    # NoReturn,
    Optional,
)
# from beartype._cave._cavemap import NoneTypeOr
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.hint.datahinttyping import TypeStack
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAnnotated,
    HintSignForwardRef,
    HintSignGeneric,
    HintSignLiteral,
    HintSignNoReturn,
    HintSignTuple,
    HintSignType,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_SEQUENCE_ARGS_1,
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE,
    HINT_SIGNS_UNION,
)
from beartype._decor.error._errorcause import ViolationCause
from beartype._decor.error._util.errorutilcolor import (
    color_hint,
    color_repr,
    strip_text_ansi_if_configured,
)
from beartype._decor.error._util.errorutiltext import (
    prefix_beartypeable_arg_value,
    prefix_beartypeable_return_value,
)
# from beartype._util.hint.utilhinttest import die_unless_hint
from beartype._util.text.utiltextmunge import (
    suffix_str_unless_suffixed,
    uppercase_str_char_first,
)
from beartype._util.text.utiltextrepr import represent_object
from beartype._data.hint.datahinttyping import TypeException

# ....................{ GLOBALS                            }....................
# Initialized with automated inspection below in the _init() function.
HINT_SIGN_TO_GET_CAUSE_FUNC: Dict[
    HintSign, Callable[[ViolationCause], ViolationCause]] = {}
'''
Dictionary mapping each **sign** (i.e., arbitrary object uniquely identifying a
category of type hints) to a private getter function defined by this submodule
whose signature matches that of the :func:`._find_cause` function and
which is dynamically dispatched by that function to describe type-checking
failures specific to that unsubscripted :mod:`typing` attribute.
'''

# ....................{ GETTERS                            }....................
def get_beartype_violation(
    # Mandatory parameters.
    func: Callable,
    conf: BeartypeConf,
    pith_name: str,
    pith_value: object,

    # Optional parameters.
    cls_stack: TypeStack = None,
    random_int: Optional[int] = None,
) -> BeartypeCallHintViolation:
    '''
    Human-readable exception detailing the failure of the parameter with the
    passed name *or* return if this name is the magic string ``return`` of the
    passed decorated function fails to satisfy the PEP-compliant type hint
    annotating this parameter or return.

    This function intentionally returns rather than raises this exception. Why?
    Because the ignorable stack frame encapsulating the call of the parent
    type-checking wrapper function generated by the :mod:`beartype.beartype`
    decorator complicates inspection of type-checking violations in tracebacks
    (especially from :mod:`pytest`, which unhelpfully recapitulates the full
    definition of this function including this docstring in those tracebacks).
    Instead, that wrapper function raises this exception directly from itself.

    Design
    ----------
    The :mod:`beartype` package actually implements two parallel PEP-compliant
    runtime type-checkers, each complementing the other by providing
    functionality unsuited for the other. These are:

    * The :mod:`beartype._check.code` submodule, dynamically generating
      optimized PEP-compliant runtime type-checking code embedded in the body
      of the wrapper function wrapping the decorated callable. For both
      efficiency and maintainability, that code only tests whether or not a
      parameter passed to that callable or value returned from that callable
      satisfies a PEP-compliant annotation on that callable; that code does
      *not* raise human-readable exceptions in the event that value fails to
      satisfy that annotation. Instead, that code defers to...
    * This function, performing unoptimized PEP-compliant runtime type-checking
      generically applicable to all wrapper functions. The aforementioned
      code calls this function only in the event that value fails to satisfy
      that annotation, in which case this function then returns a human-readable
      exception after discovering the underlying cause of this type failure by
      recursively traversing that value and annotation. While efficiency is the
      foremost focus of this package, efficiency is irrelevant during exception
      handling -- which typically only occurs under infrequent edge cases.
      Likewise, while raising this exception *would* technically be feasible
      from the aforementioned code, doing so proved sufficiently non-trivial,
      fragile, and ultimately unmaintainable to warrant offloading to this
      function universally callable from all wrapper functions.

    Parameters
    ----------
    func : CallableTypes
        Decorated callable to raise this exception from.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable or class).
    pith_name : str
        Either:

        * If the object failing to satisfy this hint is a passed parameter, the
          name of this parameter.
        * Else, the magic string ``"return"`` implying this object to be the
          value returned from this callable.
    pith_value : object
        Passed parameter or returned value violating this hint.
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        Defaults to :data:`None`.
    random_int: Optional[int], optional
        **Pseudo-random integer** (i.e., unsigned 32-bit integer
        pseudo-randomly generated by the parent :func:`beartype.beartype`
        wrapper function in type-checking randomly indexed container items by
        the current call to that function) if that function generated such an
        integer *or* :data:`None` otherwise (i.e., if that function generated
        *no* such integer). Note that this parameter critically governs whether
        this exception handler runs in constant or linear time. Specifically, if
        this parameter is:

        * An integer, this handler runs in **constant time.** Since there
          exists a one-to-one relation between this integer and the random
          container item(s) type-checked by the parent
          :func:`beartype.beartype` wrapper function, receiving this integer
          enables this handler to efficiently re-type-check the same random
          container item(s) type-checked by the parent in constant time rather
          type-checking all container items in linear time.
        * :data:`None`, this handler runs in **linear time.**

        Defaults to :data:`None`, implying this exception handler runs in linear
        time by default.

    Returns
    ----------
    BeartypeCallHintViolation
        Human-readable exception detailing the failure of this parameter or
        return to satisfy the PEP-compliant type hint annotating this parameter
        or return value, guaranteed to be an instance of either:

        * :class:`.BeartypeCallHintParamViolation`, if the object failing to
          satisfy this hint is a parameter.
        * :class:`.BeartypeCallHintReturnViolation`, if the object failing to
          satisfy this hint is a return.

    Raises
    ----------
    BeartypeDecorHintPepException
        If the type hint annotating this object is *not* PEP-compliant.
    _BeartypeCallHintPepRaiseException
        If the parameter or return value with the passed name is unannotated.
    _BeartypeCallHintPepRaiseDesynchronizationException
        If this pith actually satisfies this hint, implying either:

        * The parent wrapper function generated by the :mod:`beartype.beartype`
          decorator type-checking this pith triggered a false negative by
          erroneously misdetecting this pith as failing this type check.
        * This child helper function re-type-checking this pith triggered a
          false positive by erroneously misdetecting this pith as satisfying
          this type check when in fact this pith fails to do so.
    '''
    assert callable(func), f'{repr(func)} uncallable.'
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'
    assert isinstance(pith_name, str), f'{repr(pith_name)} not string.'

    # print('''get_beartype_violation(
    #     func={!r},
    #     conf={!r},
    #     pith_name={!r},
    #     pith_value={!r}',
    # )'''.format(func, conf, pith_name, pith_value))

    # ....................{ LOCALS                         }....................
    # Type of exception to be raised.
    exception_cls: TypeException = None  # type: ignore[assignment]

    # Substring prefixing the message of the violation to be raised below,
    # initialized to a human-readable label describing this parameter or return.
    exception_prefix: str = None  # type: ignore[assignment]

    # If the name of this parameter is the magic string implying the passed
    # object to be a return value, set the above local variables appropriately.
    if pith_name == ARG_NAME_RETURN:
        exception_cls = BeartypeCallHintReturnViolation
        exception_prefix = prefix_beartypeable_return_value(
            func=func, return_value=pith_value)
    # Else, the passed object is a parameter. In this case, set the above local
    # variables appropriately.
    else:
        exception_cls = BeartypeCallHintParamViolation
        exception_prefix = prefix_beartypeable_arg_value(
            func=func, arg_name=pith_name, arg_value=pith_value)

    # Uppercase the first character of this violation message prefix if needed.
    exception_prefix = uppercase_str_char_first(exception_prefix)

    # ....................{ HINTS                          }....................
    # If this parameter or return value is unannotated, raise an exception.
    #
    # Note that this should *NEVER* occur, as the caller guarantees this
    # parameter or return to be annotated. However, since malicious callers
    # *COULD* deface the "__annotations__" dunder dictionary without our
    # knowledge or permission, precautions are warranted.
    if pith_name not in func.__annotations__:
        raise _BeartypeCallHintPepRaiseException(
            f'{exception_prefix}unannotated.')
    # Else, this parameter or return value is annotated.

    # PEP-compliant type hint annotating this parameter or return value.
    hint = func.__annotations__[pith_name]

    # ....................{ CAUSE                          }....................
    # Cause describing the failure of this pith to satisfy this hint.
    violation_cause = ViolationCause(
        func=func,
        cause_indent='',
        cls_stack=cls_stack,
        conf=conf,
        exception_prefix=exception_prefix,
        hint=hint,
        pith=pith_value,
        pith_name=pith_name,
        random_int=random_int,
    ).find_cause()

    # If this pith satisfies this hint, *SOMETHING HAS GONE TERRIBLY AWRY.*
    #
    # In theory, this should never happen, as the parent wrapper function
    # performing type checking should *ONLY* call this child helper function
    # when this pith does *NOT* satisfy this hint. In this case, raise an
    # exception encouraging the end user to submit an upstream issue with us.
    if not violation_cause.cause_str_or_none:
        pith_value_repr = represent_object(
            obj=pith_value, max_len=_CAUSE_TRIM_OBJECT_REPR_MAX_LEN)
        raise _BeartypeCallHintPepRaiseDesynchronizationException(
            f'{exception_prefix}violates type hint {color_hint(repr(hint))}, '
            f'but utility function get_beartype_violation() '
            f'erroneously suggests this object satisfies this hint. '
            f'Please report this desynchronization failure to '
            f'the beartype issue tracker ({URL_ISSUES}) with '
            f'the accompanying exception traceback and '
            f'the representation of this object:\n'
            f'{color_repr(pith_value_repr)}'
        )
    # Else, this pith violates this hint as expected and as required for sanity.

    # This failure suffixed by a period if *NOT* yet suffixed by a period.
    violation_cause_suffixed = suffix_str_unless_suffixed(
        text=violation_cause.cause_str_or_none, suffix='.')

    # List of the one or more culprits responsible for this violation,
    # initialized to the passed parameter or returned value violating this hint.
    violation_culprits = [pith_value,]

    # If the actual object directly responsible for this violation is *NOT* the
    # passed parameter or returned value indirectly violating this hint, then
    # the latter is almost certainly a container transitively containing the
    # former as an item. In this case, add this item to this list as well.
    if pith_value is not violation_cause.pith:
        violation_culprits.append(violation_cause.pith)
    # Else, the actual object directly responsible for this violation is the
    # passed parameter or returned value indirectly violating this hint. In this
    # case, avoid adding duplicate items to this list.

    # ....................{ EXCEPTION                      }....................
    # Substring prefixing this exception message.
    exception_message_prefix = (
        f'{exception_prefix}violates type hint {color_hint(repr(hint))}')

    # If this configuration is *NOT* the default configuration, append the
    # machine-readable representation of this non-default configuration to this
    # exception message for disambiguity and clarity.
    exception_message_conf = (
        ''
        if conf == BEARTYPE_CONF_DEFAULT else
        f' under non-default configuration {repr(conf)}'
    )

    # Exception message embedding this cause.
    exception_message = (
        f'{exception_message_prefix}{exception_message_conf}, as '
        f'{violation_cause_suffixed}'
    )

    #FIXME: Unit test us up, please.
    # Strip all ANSI escape sequences from this message if requested by this
    # external user-defined configuration.
    exception_message = strip_text_ansi_if_configured(
        text=exception_message, conf=conf)

    #FIXME: Unit test that the caller receives the expected culprit, please.
    # Exception of the desired class embedding this cause.
    exception = exception_cls(  # type: ignore[misc]
        message=exception_message,
        culprits=tuple(violation_culprits),
    )

    # Return this exception to the @beartype-generated type-checking wrapper
    # (which directly calls this function), which will then squelch the
    # ignorable stack frame encapsulating that call to this function by raising
    # this exception directly from that wrapper.
    return exception

# ....................{ PRIVATE ~ constants                }....................
# Assuming a line length of 80 characters, this magic number truncates
# arbitrary object representations to 100 lines (i.e., 8000/80), which seems
# more than reasonable and (possibly) not overly excessive.
_CAUSE_TRIM_OBJECT_REPR_MAX_LEN = 8000
'''
Maximum length of arbitrary object representations suffixing human-readable
strings returned by the :func:`_find_cause` getter function, intended to
be sufficiently long to assist in identifying type-check failures but not so
excessively long as to prevent human-readability.
'''

# ....................{ PRIVATE ~ initializers             }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer heavyweight imports.
    from beartype._decor.error._errortype import (
        find_cause_instance_type_forwardref,
        find_cause_subclass_type,
        find_cause_type_instance_origin,
    )
    from beartype._decor.error._pep._pep484._errornoreturn import (
        find_cause_noreturn)
    from beartype._decor.error._pep._pep484._errorunion import (
        find_cause_union)
    from beartype._decor.error._pep._pep484585._errorgeneric import (
        find_cause_generic)
    from beartype._decor.error._pep._pep484585._errorsequence import (
        find_cause_sequence_args_1,
        find_cause_tuple,
    )
    from beartype._decor.error._pep._errorpep586 import (
        find_cause_literal)
    from beartype._decor.error._pep._errorpep593 import (
        find_cause_annotated)

    # Map each originative sign to the appropriate getter *BEFORE* any other
    # mappings. This is merely a generalized fallback subsequently replaced by
    # sign-specific getters below.
    for pep_sign_origin_isinstanceable in HINT_SIGNS_ORIGIN_ISINSTANCEABLE:
        HINT_SIGN_TO_GET_CAUSE_FUNC[pep_sign_origin_isinstanceable] = (
            find_cause_type_instance_origin)

    # Map each 1-argument sequence sign to its corresponding getter.
    for pep_sign_sequence_args_1 in HINT_SIGNS_SEQUENCE_ARGS_1:
        HINT_SIGN_TO_GET_CAUSE_FUNC[pep_sign_sequence_args_1] = (
            find_cause_sequence_args_1)

    # Map each union-specific sign to its corresponding getter.
    for pep_sign_type_union in HINT_SIGNS_UNION:
        HINT_SIGN_TO_GET_CAUSE_FUNC[pep_sign_type_union] = (
            find_cause_union)

    # Map each sign validated by a unique getter to that getter *AFTER* all
    # other mappings. These sign-specific getters are intended to replace all
    # other automated mappings above.
    HINT_SIGN_TO_GET_CAUSE_FUNC.update({
        HintSignAnnotated: find_cause_annotated,
        HintSignForwardRef: find_cause_instance_type_forwardref,
        HintSignGeneric: find_cause_generic,
        HintSignLiteral: find_cause_literal,
        HintSignNoReturn: find_cause_noreturn,
        HintSignTuple: find_cause_tuple,
        HintSignType: find_cause_subclass_type,
    })


# Initialize this submodule.
_init()
