#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type-checking function code factories** (i.e., low-level
callables dynamically generating pure-Python code snippets type-checking
arbitrary objects passed to arbitrary callables against PEP-compliant type hints
passed to those same callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: [SPEED] Create a new make_func_raiser_code() factory. After doing so,
#refactor the lower-level
#beartype._decor.wrap._wrapcode.make_func_wrapper_code() factory in terms of
#that higher-level make_func_raiser_code() factory, please.
#
#Note that doing so *WILL* prove non-trivial. That's why this submodule has
#currently focused only on the make_func_tester_code() factory. Why the
#non-triviality? Because make_func_raiser_code() will need to embed a substring
#raising an exception by calling a beartype-specific exception handler that does
#*NOT* currently exist. To create that handler, we'll need to:
#* Generalize the existing decoration-specific
#  "beartype._decor.error.errormain" submodule into a new general-purpose
#  "beartype._check._checkerror" submodule. To do so, initially just copy the
#  former to the latter. Do *NOT* bother generalizing any other submodules of
#  the "beartype._decor.error" subpackage, for the moment. One thing at a time.
#* Rename the *COPIED* beartype._check._checkerror.get_beartype_violation()
#  getter to get_func_raiser_violation().
#* Refactor get_func_raiser_violation() to have a signature resembling:
#      def get_func_raiser_violation(
#          # Mandatory parameters.
#          obj: object,
#          hint: object,
#          exception_prefix: str,
#
#          # Optional parameters.
#          random_int: Optional[int] = None,
#      ) -> BeartypeCallHintViolation:
#
#  Crucially, note the new mandatory "exception_prefix" parameter, enabling
#  callers to generate violation exceptions with arbitrary context-specific
#  human-readable prefixes.
#* Shift code currently residing in the BeartypeCall.reinit() method that
#  adds "ARG_NAME_RAISE_EXCEPTION" to "func_wrapper_scope" into the
#  make_func_raiser_code() factory instead.
#* Refactor the original lower-level
#  beartype._decor.error.errormain.get_beartype_violation() getter in terms of
#  the new higher-level get_func_raiser_violation() getter.
#* Define a new make_func_raiser_code() factory. Note that:
#  * This factory will need to generate a code snippet raising an exception. The
#    code for doing so is currently hard-coded elsewhere in the
#    make_func_wrapper_code() factory. Indeed, it seems likely that either:
#    * make_func_raiser_code() should internally call make_func_wrapper_code().
#      This is *PROBABLY* the right approach, but research is warranted.
#    * make_func_wrapper_code() should internally call make_func_raiser_code().
#    It's unclear which is preferable. One should be higher-level than the other
#    and defer to the other.

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeConfException,
    BeartypeDecorHintForwardRefException,
)
# from beartype.roar._roarexc import _BeartypeCheckException
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)
from beartype._data.hint.datahinttyping import (
    CallableTester,
    # TypeException,
)
from beartype._check.checkmagic import (
    FUNC_TESTER_NAME_PREFIX,
)
from beartype._check.convert.convsanify import sanify_hint_root_statement
from beartype._check.code.codemake import make_check_expr
from beartype._check.util.checkutilmake import make_func_signature
from beartype._check._checksnip import (
    FUNC_TESTER_CODE_RETURN,
    FUNC_TESTER_CODE_SIGNATURE,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.error.utilerror import EXCEPTION_PLACEHOLDER
from beartype._util.func.utilfuncmake import make_func
from beartype._util.hint.utilhinttest import is_hint_ignorable
from itertools import count

# ....................{ MAKERS                             }....................
@callable_cached
def make_func_tester(
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: All calls to this memoized factory pass parameters *POSITIONALLY*
    # rather than by keyword. Care should be taken when refactoring parameters,
    # particularly with respect to parameter position.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> CallableTester:
    '''
    **Type-checking tester function factory** (i.e., low-level callable
    dynamically generating a pure-Python tester function testing whether an
    arbitrary object passed to that tester satisfies the PEP-compliant type hint
    passed to this factory and returning that result as its boolean return).

    This factory is memoized for efficiency.

    Caveats
    ----------
    **This factory intentionally accepts no** ``exception_prefix``
    **parameter.** Why? Since that parameter is typically specific to the
    context-sensitive use case of the caller, accepting that parameter would
    prevent this factory from memoizing the passed hint with the returned code,
    which would rather defeat the point. Instead, this factory only:

    * Raises generic non-human-readable exceptions containing the placeholder
      :attr:`beartype._util.error.utilerror.EXCEPTION_PLACEHOLDER` substring
      that the caller is required to explicitly catch and raise non-generic
      human-readable exceptions from by calling the
      :func:`beartype._util.error.utilerror.reraise_exception_placeholder`
      function.

    **This factory intentionally accepts no** ``exception_cls`` **parameter.**
    Doing so would only ambiguously obscure context-sensitive exceptions raised
    by lower-level utility functions called by this higher-level factory.

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be type-checked.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to ``BeartypeConf()``, the default ``O(1)`` constant-time configuration.

    Returns
    ----------
    CallableTester
        Type-checking tester function generated by this factory for this hint.

    Raises
    ----------
    All exceptions raised by the lower-level :func:`make_check_expr` factory.
    Additionally, this factory also raises:

    BeartypeConfException
        If this configuration is *not* a :class:`BeartypeConf` instance.
    BeartypeDecorHintForwardRefException
        If this hint contains one or more relative forward references, which
        this factory explicitly prohibits to improve both the efficiency and
        portability of calls by users to the resulting type-checker.
    _BeartypeUtilCallableException
        If this function erroneously generates a syntactically invalid
        type-checking tester function. That should *never* happen, but let's
        admit that you're still reading this for a reason.

    Warns
    ----------
    All warnings emitted by the lower-level :func:`.make_check_expr` factory.
    '''

    # If the passed "conf" is *NOT* a configuration, raise an exception.
    if not isinstance(conf, BeartypeConf):
        raise BeartypeConfException(
            f'{repr(conf)} not beartype configuration.')
    # Else, the passed "conf" is a configuration.

    # Either:
    # * If this hint is PEP-noncompliant, the PEP-compliant type hint converted
    #   from this PEP-noncompliant type hint.
    # * Else if this hint is both PEP-compliant and supported, this hint as is.
    # * Else, raise an exception (i.e., if this hint is neither PEP-noncompliant
    #   nor a supported PEP-compliant hint).
    #
    # Do this first *BEFORE* passing this hint to any further callables.
    hint = sanify_hint_root_statement(
        hint=hint,
        conf=conf,
        exception_prefix=EXCEPTION_PLACEHOLDER,
    )

    # If this hint is ignorable, all objects satisfy this hint. In this case,
    # return the trivial tester function unconditionally returning true.
    if is_hint_ignorable(hint):
        return _func_tester_ignorable
    # Else, this hint is unignorable.

    # Python code snippet comprising a single boolean expression type-checking
    # an arbitrary object against this hint.
    (
        code_check_expr,
        func_scope,
        hint_forwardrefs_class_basename,
    ) = make_check_expr(hint, conf)

    # If this hint contains one or more relative forward references, this hint
    # is non-portable across lexical scopes. Why? Because this hint is relative
    # to and thus valid only with respect to the caller's current lexical scope.
    # However, there is *NO* guarantee that the tester function created and
    # returned by this factory resides in the same lexical scope.
    #
    # Suppose that tester does, however. Even in that best case, *ALL* calls to
    # that tester would still be non-portable. Why? Because those calls would
    # now tacitly assume the original lexical scope that they were called in.
    # Those calls are now lexically-dependent and thus could *NOT* be trivially
    # copy-and-pasted into different lexical scopes (e.g., submodules, classes,
    # or callables); doing so would raise exceptions at call time, due to being
    # unable to resolve those references. Preventing users from doing something
    # that will blow up in their test suites commits after the fact is not
    # simply a good thing; it's really the only sane thing left.
    #
    # Suppose that we didn't particularly care about end user sanity, however.
    # Even in that worst case, resolving these references would still be
    # non-trivial, non-portable, and (perhaps most importantly) incredibly slow.
    # Why? Because doing so would require iteratively introspecting the call
    # stack for the first callable *NOT* residing in the "beartype" codebase.
    # These references would then be resolved against the global and local
    # lexical scope of that callable. While technically feasible, doing so would
    # render higher-level "beartype" functions calling this lower-level
    # factory (e.g., our increasingly popular public beartype.door.is_bearable()
    # tester) sufficiently slow as to be pragmatically infeasible.
    if hint_forwardrefs_class_basename:
        raise BeartypeDecorHintForwardRefException(
            f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
            f'contains one or more relative forward references:\n'
            f'\t{repr(hint_forwardrefs_class_basename)}\n'
            f'Beartype prohibits relative forward references outside of '
            f'@beartype-decorated callables. For your own personal safety and '
            f'those of the codebases you love, consider canonicalizing these '
            f'relative forward references into absolute forward references '
            f'(e.g., by replacing "MuhClass" with "muh_module.MuhClass").'
        )
    # Else, this hint contains *NO* relative forward references.

    # Unqualified basename of this tester function, uniquified by suffixing an
    # arbitrary integer guaranteed to be unique to this tester function.
    func_tester_name = (
        f'{FUNC_TESTER_NAME_PREFIX}{next(_func_tester_name_counter)}')

    # Python code snippet declaring the signature of this tester function.
    code_signature = make_func_signature(
        func_name=func_tester_name,
        func_scope=func_scope,
        code_signature_format=FUNC_TESTER_CODE_SIGNATURE,
        conf=conf,
    )

    # Python code snippet returning the boolean result of type-checking the
    # arbitrary object passed to this tester function against this type hint.
    code_check_return = FUNC_TESTER_CODE_RETURN.format(
        code_check_expr=code_check_expr)

    # Python code snippet defining this tester function in entirety.
    func_tester_code = (
        f'{code_signature}'
        f'{code_check_return}'
    )

    # Type-checking tester function to be returned.
    func_tester = make_func(
        func_name=func_tester_name,
        func_code=func_tester_code,
        func_locals=func_scope,
        func_label=f'{EXCEPTION_PLACEHOLDER}tester {func_tester_name}()',
        is_debug=conf.is_debug,
    )

    # Return this tester function.
    return func_tester

# ....................{ PRIVATE ~ globals                  }....................
_func_tester_name_counter = count(start=0, step=1)
'''
**Type-checking tester function name uniquifier** (i.e., iterator yielding the
next integer incrementation starting at 0, leveraged by the
:func:`make_func_tester` factory to uniquify the names of the tester functions
created by that factory).
'''

# ....................{ PRIVATE ~ testers                  }....................
def _func_tester_ignorable(obj: object) -> bool:
    '''
    **Ignorable type-checking tester function singleton** (i.e., function
    unconditionally returning ``True``, semantically equivalent to a tester
    testing whether an arbitrary object passed to this tester satisfies an
    ignorable PEP-compliant type hint).

    The :func:`make_func_tester` factory efficiently returns this singleton when
    passed an ignorable type hint rather than inefficiently regenerating a
    unique ignorable type-checking tester function for that hint.
    '''

    return True
