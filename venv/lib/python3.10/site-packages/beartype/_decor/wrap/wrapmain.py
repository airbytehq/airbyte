#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator code generator.**

This private submodule dynamically generates both the signature and body of the
wrapper function type-checking all annotated parameters and return value of the
the callable currently being decorated by the :func:`beartype.beartype`
decorator in a general-purpose manner. For genericity, this relatively
high-level submodule implements *no* support for annotation-based PEPs (e.g.,
:pep:`484`); other lower-level submodules do so instead.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

#FIXME: Split this large submodule into smaller submodules for maintainability.
#A useful approach might be:
#* Define a new private "_codearg" submodule and shift the _code_check_args()
#  function there.
#* Define a new private "_codereturn" submodule and shift the
#  _code_check_return() function there.

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorParamNameException,
    BeartypeDecorHintPepException,
)
from beartype.typing import NoReturn
from beartype._check.checkcall import BeartypeCall
from beartype._check.checkmagic import ARG_NAME_TYPISTRY
from beartype._check.code._codesnip import (
    PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_PREFIX,
    PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_SUFFIX,
)
from beartype._check.convert.convsanify import sanify_hint_root_func
from beartype._check.forward.fwdtype import (
    bear_typistry,
    get_hint_forwardref_code,
)
from beartype._check.util.checkutilmake import make_func_signature
from beartype._data.func.datafuncarg import (
    ARG_NAME_RETURN,
    ARG_NAME_RETURN_REPR,
)
from beartype._decor.wrap.wrapsnip import (
    CODE_INIT_ARGS_LEN,
    CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER,
    CODE_RETURN_CHECK_PREFIX,
    CODE_RETURN_CHECK_SUFFIX,
    CODE_RETURN_UNCHECKED,
    CODE_SIGNATURE,
    PARAM_KIND_TO_CODE_LOCALIZE,
    PEP484_CODE_CHECK_NORETURN,
)
from beartype._decor.wrap._wrapcode import make_func_wrapper_code
from beartype._util.error.utilerror import (
    EXCEPTION_PLACEHOLDER,
    reraise_exception_placeholder,
)
from beartype._util.func.arg.utilfuncargiter import (
    ARG_META_INDEX_KIND,
    ARG_META_INDEX_NAME,
    ArgKind,
    iter_func_args,
)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585ref import (
    get_hint_pep484585_forwardref_classname_relative_to_object)
from beartype._util.hint.utilhinttest import (
    is_hint_ignorable,
    is_hint_needs_cls_stack,
)
from beartype._util.kind.utilkinddict import update_mapping
from beartype._util.text.utiltextmunge import replace_str_substrs
from beartype._util.text.utiltextprefix import (
    prefix_beartypeable_arg,
    prefix_beartypeable_return,
)
from beartype._util.utilobject import SENTINEL
from collections.abc import (
    Callable,
    Iterable,
)

# ....................{ GENERATORS                         }....................
def generate_code(
    bear_call: BeartypeCall,

    # "beartype._decor.wrap.wrapsnip" string globals required only for
    # their bound "str.format" methods.
    CODE_RETURN_UNCHECKED_format: Callable = CODE_RETURN_UNCHECKED.format,
) -> str:
    '''
    Generate a Python code snippet dynamically defining the wrapper function
    type-checking the passed decorated callable.

    This high-level function implements this decorator's core type-checking,
    converting all unignorable PEP-compliant type hints annotating this
    callable into pure-Python code type-checking the corresponding parameters
    and return values of each call to this callable.

    Parameters
    ----------
    bear_call : BeartypeCall
        Decorated callable to be type-checked.

    Returns
    ----------
    str
        Generated function wrapper code. Specifically, either:

        * If the decorated callable requires *no* type-checking (e.g., due to
          all type hints annotating this callable being ignorable), the empty
          string. Note this edge case is distinct from a related edge case at
          the head of the :func:`beartype.beartype` decorator reducing to a
          noop for unannotated callables. By compare, this boolean is ``True``
          only for callables annotated with **ignorable type hints** (i.e.,
          :class:`object`, :class:`beartype.cave.AnyType`,
          :class:`typing.Any`): e.g.,

          .. code-block:: python

              >>> from beartype.cave import AnyType
              >>> from typing import Any
              >>> def muh_func(muh_param1: AnyType, muh_param2: object) -> Any: pass
              >>> muh_func is beartype(muh_func)
              True

        * Else, a code snippet defining the wrapper function type-checking the
          decorated callable, including (in order):

          * A signature declaring this wrapper, accepting both
            beartype-agnostic and -specific parameters. The latter include:

            * A private ``__beartype_func`` parameter initialized to the
              decorated callable. In theory, this callable should be accessible
              as a closure-style local in this wrapper. For unknown reasons
              (presumably, a subtle bug in the exec() builtin), this is *not*
              the case. Instead, a closure-style local must be simulated by
              passing this callable at function definition time as the default
              value of an arbitrary parameter. To ensure this default is *not*
              overwritten by a function accepting a parameter of the same name,
              this unlikely edge case is guarded against elsewhere.

          * Statements type checking parameters passed to the decorated
            callable.
          * A call to the decorated callable.
          * A statement type checking the value returned by the decorated
            callable.

    Raises
    ----------
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__bear``.
    BeartypeDecorHintNonpepException
        If any type hint annotating any parameter of this callable is neither:

        * **PEP-compliant** (i.e., :mod:`beartype`-agnostic hint compliant with
          annotation-centric PEPs).
        * **PEP-noncompliant** (i.e., :mod:`beartype`-specific type hint *not*
          compliant with annotation-centric PEPs)).
    _BeartypeUtilMappingException
        If generated code type-checking any pair of parameters and returns
        erroneously declares an optional private beartype-specific parameter of
        the same name with differing default value. Since this should *never*
        happen, a private non-human-readable exception is raised in this case.
    '''
    assert bear_call.__class__ is BeartypeCall, (
        f'{repr(bear_call)} not @beartype call.')

    # Python code snippet type-checking all callable parameters if one or more
    # such parameters are annotated with unignorable type hints *OR* the empty
    # string otherwise.
    code_check_params = _code_check_args(bear_call)

    # Python code snippet type-checking the callable return if this return is
    # annotated with an unignorable type hint *OR* the empty string otherwise.
    code_check_return = _code_check_return(bear_call)

    # If the callable return requires *NO* type-checking...
    #
    # Note that this branch *CANNOT* be embedded in the prior call to the
    # _code_check_return() function, as doing so would prevent us from
    # efficiently reducing to a noop here.
    if not code_check_return:
        # If all callable parameters also require *NO* type-checking, this
        # callable itself requires *NO* type-checking. In this case, return the
        # empty string instructing the parent @beartype decorator to reduce to
        # a noop (i.e., the identity decorator returning this callable as is).
        if not code_check_params:
            return ''
        # Else, one or more callable parameters require type-checking.

        # Python code snippet calling this callable unchecked, returning the
        # value returned by this callable from this wrapper.
        code_check_return = CODE_RETURN_UNCHECKED_format(
            func_call_prefix=bear_call.func_wrapper_code_call_prefix)
    # Else, the callable return requires type-checking.

    # Python code snippet declaring the signature of this type-checking wrapper
    # function, deferred for efficiency until *AFTER* confirming that a wrapper
    # function is even required.
    code_signature = make_func_signature(
        func_name=bear_call.func_wrapper_name,
        func_scope=bear_call.func_wrapper_scope,
        code_signature_format=CODE_SIGNATURE,
        code_signature_prefix=bear_call.func_wrapper_code_signature_prefix,
        conf=bear_call.conf,
    )

    # Return Python code defining the wrapper type-checking this callable.
    # While there exist numerous alternatives to string formatting (e.g.,
    # appending to a list or bytearray before joining the items of that
    # iterable into a string), these alternatives are either:
    # * Slower, as in the case of a list (e.g., due to the high up-front cost
    #   of list construction).
    # * Cumbersome, as in the case of a bytearray.
    #
    # Since string concatenation is heavily optimized by the official CPython
    # interpreter, the simplest approach is the most ideal. KISS, bro.
    return (
        f'{code_signature}'
        f'{code_check_params}'
        f'{code_check_return}'
    )

# ....................{ PRIVATE ~ constants                }....................
#FIXME: Remove this set *AFTER* handling these kinds of parameters.
_PARAM_KINDS_IGNORABLE = frozenset((
    ArgKind.VAR_KEYWORD,
))
'''
Frozen set of all :attr:`ArgKind` enumeration members to be ignored
during annotation-based type checking in the :func:`beartype.beartype`
decorator.

This includes:

* Constants specific to variadic keyword parameters (e.g., ``**kwargs``), which
  are currently unsupported by :func:`beartype`.
* Constants specific to positional-only parameters, which apply only to
  non-pure-Python callables (e.g., defined by C extensions). The
  :func:`beartype` decorator applies *only* to pure-Python callables, which
  provide no syntactic means for specifying positional-only parameters.
'''


_PARAM_KINDS_POSITIONAL = frozenset((
    ArgKind.POSITIONAL_ONLY,
    ArgKind.POSITIONAL_OR_KEYWORD,
))
'''
Frozen set of all **positional parameter kinds** (i.e.,
:attr:`ArgKind` enumeration members signifying that a callable parameter
either may *or* must be passed positionally).
'''

# ....................{ PRIVATE ~ args                     }....................
def _code_check_args(bear_call: BeartypeCall) -> str:
    '''
    Generate a Python code snippet type-checking all annotated parameters of
    the decorated callable if any *or* the empty string otherwise (i.e., if
    these parameters are unannotated).

    Parameters
    ----------
    bear_call : BeartypeCall
        Decorated callable to be type-checked.

    Returns
    ----------
    str
        Code type-checking all annotated parameters of the decorated callable.

    Raises
    ----------
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__bear``.
    BeartypeDecorHintNonpepException
        If any type hint annotating any parameter of this callable is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.
    '''
    assert bear_call.__class__ is BeartypeCall, (
        f'{repr(bear_call)} not @beartype call.')

    # ..................{ LOCALS ~ func                      }..................
    #FIXME: Unit test this up, please. Specifically, unit test:
    #* A callable annotated with only a single return type hint accepting both:
    #  * *NO* parameters.
    #  * One or more parameters each of which is unannotated.
    #
    #We probably already do this, but let's be double-sure here. Safety first!

    # If *NO* callable parameters are annotated, silently reduce to a noop.
    #
    # Note that this is purely an optimization short-circuit mildly improving
    # efficiency for the common case of callables accepting either no
    # parameters *OR* one or more parameters, all of which are unannotated.
    if (
        # That callable is annotated by only one type hint *AND*...
        len(bear_call.func_arg_name_to_hint) == 1 and
        # That type hint annotates that callable's return rather than a
        # parameter accepted by that callable...
        ARG_NAME_RETURN in bear_call.func_arg_name_to_hint
    ):
        return ''
    # Else, one or more callable parameters are annotated.

    # Python code snippet to be returned.
    func_wrapper_code = ''

    # ..................{ LOCALS ~ parameter                 }..................
    #FIXME: Remove this *AFTER* optimizing signature generation, please.
    # True only if this callable possibly accepts one or more positional
    # parameters.
    is_args_positional = False

    # ..................{ LOCALS ~ hint                      }..................
    # Type hint annotating the current parameter if any *OR* "_PARAM_HINT_EMPTY"
    # otherwise (i.e., if this parameter is unannotated).
    hint = None

    # This type hint sanitized into a possibly different type hint more readily
    # consumable by @beartype's code generator.
    hint_sane = None

    # ..................{ GENERATE                           }..................
    #FIXME: Locally remove the "arg_index" local variable (and thus avoid
    #calling the enumerate() builtin here) AFTER* refactoring @beartype to
    #generate callable-specific wrapper signatures.

    # For the 0-based index of each parameter accepted by this callable and the
    # "ParameterMeta" object describing this parameter (in declaration order)...
    for arg_index, arg_meta in enumerate(iter_func_args(
        # Possibly lowest-level wrappee underlying the possibly higher-level
        # wrapper currently being decorated by the @beartype decorator. The
        # latter typically fails to convey the same callable metadata conveyed
        # by the former -- including the names and kinds of parameters accepted
        # by the possibly unwrapped callable. This renders the latter mostly
        # useless for our purposes.
        func=bear_call.func_wrappee_wrappee,
        func_codeobj=bear_call.func_wrappee_wrappee_codeobj,
        is_unwrap=False,
    )):
        # Kind and name of this parameter.
        arg_kind: ArgKind = arg_meta[ARG_META_INDEX_KIND]  # type: ignore[assignment]
        arg_name: str = arg_meta[ARG_META_INDEX_NAME]  # type: ignore[assignment]

        # Type hint annotating this parameter if any *OR* the sentinel
        # placeholder otherwise (i.e., if this parameter is unannotated).
        #
        # Note that "None" is a semantically meaningful PEP 484-compliant type
        # hint equivalent to "type(None)". Ergo, we *MUST* explicitly
        # distinguish between that type hint and unannotated parameters.
        hint = bear_call.func_arg_name_to_hint_get(arg_name, SENTINEL)

        # If this parameter is unannotated, continue to the next parameter.
        if hint is SENTINEL:
            continue
        # Else, this parameter is annotated.

        # Attempt to...
        try:
            # If this parameter's name is reserved for use by the @beartype
            # decorator, raise an exception.
            if arg_name.startswith('__bear'):
                raise BeartypeDecorParamNameException(
                    f'{EXCEPTION_PLACEHOLDER}reserved by @beartype.')
            # If either the type of this parameter is silently ignorable, continue
            # to the next parameter.
            elif arg_kind in _PARAM_KINDS_IGNORABLE:
                continue
            # Else, this parameter is non-ignorable.

            # Sanitize this hint into a possibly different type hint more
            # readily consumable by @beartype's code generator *BEFORE* passing
            # this hint to any further callables.
            hint_sane = sanify_hint_root_func(
                hint=hint, arg_name=arg_name, bear_call=bear_call)

            # If this hint is ignorable, continue to the next parameter.
            #
            # Note that this is intentionally tested *AFTER* this hint has been
            # coerced into a PEP-compliant type hint to implicitly ignore
            # PEP-noncompliant type hints as well (e.g., "(object, int, str)").
            if is_hint_ignorable(hint_sane):
                # print(f'Ignoring {bear_call.func_name} parameter {arg_name} hint {repr(hint)}...')
                continue
            # Else, this hint is unignorable.
            #
            # If this unignorable parameter either may *OR* must be passed
            # positionally, record this fact. Note this conditional branch must
            # be tested after validating this parameter to be unignorable; if
            # this branch were instead nested *BEFORE* validating this
            # parameter to be unignorable, @beartype would fail to reduce to a
            # noop for otherwise ignorable callables -- which would be rather
            # bad, really.
            elif arg_kind in _PARAM_KINDS_POSITIONAL:
                is_args_positional = True

            # Python code template localizing this parameter.
            #
            # Since @beartype now supports *ALL* parameter kinds, we safely
            # assume this behaves as expected without additional validation.
            # PARAM_LOCALIZE_TEMPLATE = PARAM_KIND_TO_CODE_LOCALIZE[arg_kind]

            #FIXME: Preserved in the event of a new future unsupported parameter kind.
            # Python code template localizing this parameter if this kind of
            # parameter is supported *OR* "None" otherwise.
            PARAM_LOCALIZE_TEMPLATE = PARAM_KIND_TO_CODE_LOCALIZE.get(  # type: ignore
                arg_kind, None)

            # If this kind of parameter is unsupported, raise an exception.
            #
            # Note this edge case should *NEVER* occur, as the parent function
            # should have simply ignored this parameter.
            if PARAM_LOCALIZE_TEMPLATE is None:
                raise BeartypeDecorHintPepException(
                    f'{EXCEPTION_PLACEHOLDER}kind {repr(arg_kind)} '
                    f'currently unsupported by @beartype.'
                )
            # Else, this kind of parameter is supported. Ergo, this code is
            # non-"None".

            # Type stack if required by this hint *OR* "None" otherwise. See the
            # is_hint_needs_cls_stack() tester for further discussion.
            #
            # Note that the original unsanitized "hint" (e.g., "typing.Self")
            # rather than the new sanitized "hint_sane" (e.g., the class
            # currently being decorated by @beartype) is passed to that tester.
            # Why? Because the latter may already have been reduced above to a
            # different and seemingly innocuous type hint that does *NOT* appear
            # to require a type stack but actually does. Only the original
            # unsanitized "hint" can tell the truth.
            cls_stack = (
                 bear_call.cls_stack if is_hint_needs_cls_stack(hint) else None)
            # print(f'arg "{arg_name}" hint {repr(hint)} cls_stack: {repr(cls_stack)}')

            # Generate a memoized parameter-agnostic code snippet type-checking
            # any parameter or return value with an arbitrary name.
            (
                code_param_check_pith,
                func_wrapper_scope,
                hint_forwardrefs_class_basename,
            ) = make_func_wrapper_code(hint_sane, bear_call.conf, cls_stack)

            # Merge the local scope required to check this parameter into the
            # local scope currently required by the current wrapper function.
            update_mapping(bear_call.func_wrapper_scope, func_wrapper_scope)

            # Python code snippet localizing this parameter.
            code_param_localize = PARAM_LOCALIZE_TEMPLATE.format(
                arg_name=arg_name, arg_index=arg_index)

            # Unmemoize this snippet against the current parameter.
            code_param_check = _unmemoize_func_wrapper_code(
                bear_call=bear_call,
                func_wrapper_code=code_param_check_pith,
                pith_repr=repr(arg_name),
                hint_forwardrefs_class_basename=hint_forwardrefs_class_basename,
            )

            # Append code type-checking this parameter against this hint.
            func_wrapper_code += f'{code_param_localize}{code_param_check}'
        # If any exception was raised, reraise this exception with each
        # placeholder substring (i.e., "EXCEPTION_PLACEHOLDER" instance)
        # replaced by a human-readable description of this callable and
        # annotated parameter.
        except Exception as exception:
            reraise_exception_placeholder(
                exception=exception,
                #FIXME: Embed the kind of parameter as well (e.g.,
                #"positional-only", "keyword-only", "variadic positional"),
                #ideally by improving the existing prefix_beartypeable_arg()
                #function to introspect this kind from the callable code object.
                target_str=prefix_beartypeable_arg(
                    func=bear_call.func_wrappee, arg_name=arg_name),
            )

    # If this callable accepts one or more positional type-checked parameters,
    # prefix this code by a snippet localizing the number of these parameters.
    if is_args_positional:
        func_wrapper_code = f'{CODE_INIT_ARGS_LEN}{func_wrapper_code}'
    # Else, this callable accepts *NO* positional type-checked parameters. In
    # this case, preserve this code as is.

    # Return this code.
    return func_wrapper_code

# ....................{ PRIVATE ~ return                   }....................
def _code_check_return(bear_call: BeartypeCall) -> str:
    '''
    Generate a Python code snippet type-checking the annotated return declared
    by the decorated callable if any *or* the empty string otherwise (i.e., if
    this return is unannotated).

    Parameters
    ----------
    bear_call : BeartypeCall
        Decorated callable to be type-checked.

    Returns
    ----------
    str
        Code type-checking any annotated return of the decorated callable.

    Raises
    ----------
    BeartypeDecorHintPep484585Exception
        If this callable is either:

        * A coroutine *not* annotated by a :attr:`typing.Coroutine` type hint.
        * A generator *not* annotated by a :attr:`typing.Generator` type hint.
        * An asynchronous generator *not* annotated by a
          :attr:`typing.AsyncGenerator` type hint.
    BeartypeDecorHintNonpepException
        If the type hint annotating this return (if any) of this callable is
        neither:

        * **PEP-compliant** (i.e., :mod:`beartype`-agnostic hint compliant with
          annotation-centric PEPs).
        * **PEP-noncompliant** (i.e., :mod:`beartype`-specific type hint *not*
          compliant with annotation-centric PEPs)).
    '''
    assert bear_call.__class__ is BeartypeCall, (
        f'{repr(bear_call)} not @beartype call.')

    # Type hint annotating this callable's return if any *OR* "SENTINEL"
    # otherwise (i.e., if this return is unannotated).
    #
    # Note that "None" is a semantically meaningful PEP 484-compliant type hint
    # equivalent to "type(None)". Ergo, we *MUST* explicitly distinguish
    # between that type hint and an unannotated return.
    hint = bear_call.func_arg_name_to_hint_get(ARG_NAME_RETURN, SENTINEL)

    # If this return is unannotated, silently reduce to a noop.
    if hint is SENTINEL:
        return ''
    # Else, this return is annotated.

    # Python code snippet to be returned, defaulting to the empty string
    # implying this callable's return to either be unannotated *OR* annotated by
    # a safely ignorable type hint.
    func_wrapper_code = ''

    # Attempt to...
    try:
        # Preserve the original unsanitized type hint for subsequent reference
        # *BEFORE* sanitizing this type hint.
        hint_insane = hint

        # Sanitize this hint to either:
        # * If this hint is PEP-noncompliant, the PEP-compliant type hint
        #   converted from this PEP-noncompliant type hint.
        # * If this hint is both PEP-compliant and supported, this hint as
        #   is.
        # * Else, raise an exception.
        #
        # Do this first *BEFORE* passing this hint to any further callables.
        hint = sanify_hint_root_func(
            hint=hint, arg_name=ARG_NAME_RETURN, bear_call=bear_call)

        # If this is the PEP 484-compliant "typing.NoReturn" type hint permitted
        # *ONLY* as a return annotation...
        if hint is NoReturn:
            # Default this snippet to a pre-generated snippet validating this
            # callable to *NEVER* successfully return. Yup!
            func_wrapper_code = PEP484_CODE_CHECK_NORETURN.format(
                func_call_prefix=bear_call.func_wrapper_code_call_prefix)
        # Else, this is *NOT* "typing.NoReturn". In this case...
        else:
            # If this PEP-compliant hint is unignorable, generate and return a
            # snippet type-checking this return against this hint.
            if not is_hint_ignorable(hint):
                # Type stack if required by this hint *OR* "None" otherwise. See
                # the is_hint_needs_cls_stack() tester for further discussion.
                #
                # Note that the original unsanitized "hint_insane" (e.g.,
                # "typing.Self") rather than the new sanitized "hint" (e.g., the
                # class currently being decorated by @beartype) is passed to
                # that tester. See _code_check_args() for details.
                cls_stack = (
                    bear_call.cls_stack
                    if is_hint_needs_cls_stack(hint_insane) else
                    None
                )
                # print(f'return hint {repr(hint)} cls_stack: {repr(cls_stack)}')

                # Empty tuple, passed below to satisfy the
                # _unmemoize_func_wrapper_code() API.
                hint_forwardrefs_class_basename = ()

                # Generate a memoized parameter-agnostic code snippet
                # type-checking any parameter or return with any name.
                (
                    code_return_check_pith,
                    func_wrapper_scope,
                    hint_forwardrefs_class_basename,
                ) = make_func_wrapper_code(hint, bear_call.conf, cls_stack)  # type: ignore[assignment]

                # Merge the local scope required to type-check this return into
                # the local scope currently required by the current wrapper
                # function.
                update_mapping(
                    bear_call.func_wrapper_scope, func_wrapper_scope)

                # Unmemoize this snippet against this return.
                code_return_check_pith_unmemoized = _unmemoize_func_wrapper_code(
                    bear_call=bear_call,
                    func_wrapper_code=code_return_check_pith,
                    pith_repr=ARG_NAME_RETURN_REPR,
                    hint_forwardrefs_class_basename=(
                        hint_forwardrefs_class_basename),
                )

                #FIXME: [SPEED] Optimize the following two string munging
                #operations into a single string-munging operation resembling:
                #    func_wrapper_code = CODE_RETURN_CHECK.format(
                #        func_call_prefix=bear_call.func_wrapper_code_call_prefix,
                #        check_expr=code_return_check_pith_unmemoized,
                #    )
                #
                #Then define "CODE_RETURN_CHECK" in the "wrapsnip" submodule to
                #resemble:
                #    CODE_RETURN_CHECK = (
                #        f'{CODE_RETURN_CHECK_PREFIX}{{check_expr}}'
                #        f'{CODE_RETURN_CHECK_SUFFIX}'
                #    )

                # Python code snippet type-checking this return.
                code_return_check_prefix = CODE_RETURN_CHECK_PREFIX.format(
                    func_call_prefix=bear_call.func_wrapper_code_call_prefix)

                # Return a Python code snippet:
                # * Calling the decorated callable and localize its return
                #   *AND*...
                # * Type-checking this return *AND*...
                # * Returning this return from this wrapper function.
                func_wrapper_code = (
                    f'{code_return_check_prefix}'
                    f'{code_return_check_pith_unmemoized}'
                    f'{CODE_RETURN_CHECK_SUFFIX}'
                )
            # Else, this PEP-compliant hint is ignorable.
            # if not func_wrapper_code: print(f'Ignoring {bear_call.func_name} return hint {repr(hint)}...')
    # If any exception was raised, reraise this exception with each placeholder
    # substring (i.e., "EXCEPTION_PLACEHOLDER" instance) replaced by a
    # human-readable description of this callable and annotated return.
    except Exception as exception:
        reraise_exception_placeholder(
            exception=exception,
            target_str=prefix_beartypeable_return(bear_call.func_wrappee),
        )

    # Return this code.
    return func_wrapper_code

# ....................{ PRIVATE ~ unmemoize                }....................
def _unmemoize_func_wrapper_code(
    bear_call: BeartypeCall,
    func_wrapper_code: str,
    pith_repr: str,
    hint_forwardrefs_class_basename: tuple,
) -> str:
    '''
    Convert the passed memoized code snippet type-checking any parameter or
    return of the decorated callable into an "unmemoized" code snippet
    type-checking a specific parameter or return of that callable.

    Specifically, this function (in order):

    #. Globally replaces all references to the
       :data:`.CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER` placeholder substring
       cached into this code with the passed ``pith_repr`` parameter.
    #. Unmemoizes this code by globally replacing all relative forward
       reference placeholder substrings cached into this code with Python
       expressions evaluating to the classes referred to by those substrings
       relative to that callable when accessed via the private
       ``__beartypistry`` parameter.

    Parameters
    ----------
    bear_call : BeartypeCall
        Decorated callable to be type-checked.
    func_wrapper_code : str
        Memoized callable-agnostic code snippet type-checking any parameter or
        return of the decorated callable.
    pith_repr : str
        Machine-readable representation of the name of this parameter or
        return.
    hint_forwardrefs_class_basename : tuple
        Tuple of the unqualified classnames referred to by all relative forward
        reference type hints visitable from the current root type hint.

    Returns
    ----------
    str
        This memoized code unmemoized by globally resolving all relative
        forward reference placeholder substrings cached into this code relative
        to the currently decorated callable.
    '''
    assert bear_call.__class__ is BeartypeCall, (
        f'{repr(bear_call)} not @beartype call.')
    assert isinstance(func_wrapper_code, str), (
        f'{repr(func_wrapper_code)} not string.')
    assert isinstance(pith_repr, str), f'{repr(pith_repr)} not string.'
    assert isinstance(hint_forwardrefs_class_basename, Iterable), (
        f'{repr(hint_forwardrefs_class_basename)} not iterable.')

    # Generate an unmemoized parameter-specific code snippet type-checking this
    # parameter by replacing in this parameter-agnostic code snippet...
    func_wrapper_code = replace_str_substrs(
        text=func_wrapper_code,
        # This placeholder substring cached into this code with...
        old=CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER,
        # This object representation of the name of this parameter or return.
        new=pith_repr,
    )

    # If this code contains one or more relative forward reference placeholder
    # substrings memoized into this code, unmemoize this code by globally
    # resolving these placeholders relative to the decorated callable.
    if hint_forwardrefs_class_basename:
        # Callable currently being decorated by @beartype.
        func = bear_call.func_wrappee

        # Pass the beartypistry singleton as a private "__beartypistry"
        # parameter to this wrapper function.
        bear_call.func_wrapper_scope[ARG_NAME_TYPISTRY] = bear_typistry

        # For each unqualified classname referred to by a relative forward
        # reference type hints visitable from the current root type hint...
        for hint_forwardref_class_basename in hint_forwardrefs_class_basename:
            # Generate an unmemoized callable-specific code snippet checking
            # this class by globally replacing in this callable-agnostic code...
            func_wrapper_code = replace_str_substrs(
                text=func_wrapper_code,
                # This placeholder substring cached into this code with...
                old=(
                    f'{PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_PREFIX}'
                    f'{hint_forwardref_class_basename}'
                    f'{PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_SUFFIX}'
                ),
                # Python expression evaluating to this class when accessed
                # via the private "__beartypistry" parameter.
                new=get_hint_forwardref_code(
                    # Fully-qualified classname referred to by this forward
                    # reference relative to the decorated callable.
                    get_hint_pep484585_forwardref_classname_relative_to_object(
                        hint=hint_forwardref_class_basename, obj=func)
                ),
            )

    # Return this unmemoized callable-specific code snippet.
    return func_wrapper_code
