#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Public beartype decorator.**

This private submodule defines the core :func:`beartype` decorator, which the
:mod:`beartype.__init__` submodule then imports for importation as the public
:mod:`beartype.beartype` decorator by downstream callers -- completing the
virtuous cycle of code life.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                            }....................
from beartype.typing import TYPE_CHECKING
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)
from beartype._data.hint.datahinttyping import (
    BeartypeConfedDecorator,
    BeartypeReturn,
    BeartypeableT,
)

# Intentionally import the standard mypy-friendly @typing.overload decorator
# rather than a possibly mypy-unfriendly @beartype.typing.overload decorator --
# which, in any case, would be needlessly inefficient and thus bad.
from typing import overload

# ....................{ OVERLOADS                          }....................
# Declare PEP 484-compliant overloads to avoid breaking downstream code
# statically type-checked by a static type checker (e.g., mypy). The concrete
# @beartype decorator declared below is permissively annotated as returning a
# union of multiple types desynchronized from the types of the passed arguments
# and thus fails to accurately convey the actual public API of that decorator.
# See also: https://www.python.org/dev/peps/pep-0484/#function-method-overloading
@overload  # type: ignore[misc,no-overload-impl]
def beartype(obj: BeartypeableT) -> BeartypeableT: ...
@overload
def beartype(*, conf: BeartypeConf) -> BeartypeConfedDecorator: ...

# ....................{ DECORATORS                         }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: *THE ORDER OF CONDITIONAL STATEMENTS BELOW IS SIGNIFICANT.* Notably,
# mypy 0.940 erroneously emits this fatal error when the "TYPE_CHECKING or"
# condition is *NOT* the first condition of this "if" statement:
#     beartype/_decor/main.py:294: error: Condition can't be inferred, unable
#     to merge overloads [misc]
# See also: https://github.com/python/mypy/issues/12335#issuecomment-1065591703
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# If the active Python interpreter is either...
if (
    # Running under an external static type checker -- in which case there is
    # no benefit to attempting runtime type-checking whatsoever...
    #
    # Note that this test is largely pointless. By definition, static type
    # checkers should *NOT* actually run any code -- merely parse and analyze
    # that code. Ergo, this boolean constant should *ALWAYS* be false from the
    # runtime context under which @beartype is only ever run. Nonetheless, this
    # test is only performed once per process and is thus effectively free.
    TYPE_CHECKING or
    # Optimized (e.g., option "-O" was passed to this interpreter) *OR*...
    not __debug__
):
# Then unconditionally disable @beartype-based type-checking across the entire
# codebase by reducing the @beartype decorator to the identity decorator.
# Ideally, this would have been implemented at the top rather than bottom of
# this submodule as a conditional resembling:
#     if __debug__:
#         def beartype(func: CallableTypes) -> CallableTypes:
#             return func
#         return
#
# Tragically, Python fails to support module-scoped "return" statements. *sigh*
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Synchronize the signature of this identity decorator with the
# non-identity decorator imported below.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def beartype(  # type: ignore[no-redef]
        obj: BeartypeableT,  # pyright: ignore[reportInvalidTypeVarUse]

        # Optional keyword-only parameters.
        *,
        conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    ) -> BeartypeReturn:
        return obj
# Else, the active Python interpreter is in a standard runtime state. In this
# case, define the @beartype decorator in the standard way.
else:
    # This is where @beartype *REALLY* lives. Grep here for all the goods.
    from beartype._decor.decorcache import beartype

# ....................{ DECORATORS ~ doc                   }....................
# Document the @beartype decorator with the same documentation regardless of
# which of the above implementations currently implements that decorator.
beartype.__doc__ = (
    '''
    Decorate the passed **beartypeable** (i.e., pure-Python callable or
    class) with optimal type-checking dynamically generated unique to that
    beartypeable under the passed beartype configuration.

    This decorator supports two distinct (albeit equally efficient) modes
    of operation:

    * **Decoration mode.** The caller activates this mode by passing this
      decorator a type-checkable object via the ``obj`` parameter; this
      decorator then creates and returns a new callable wrapping that object
      with optimal type-checking. Specifically:

      * If this object is a callable, this decorator creates and returns a new
        **runtime type-checker** (i.e., pure-Python function validating all
        parameters and returns of all calls to that callable against all
        PEP-compliant type hints annotating those parameters and returns). The
        type-checker returned by this decorator is:

        * Optimized uniquely for the passed callable.
        * Guaranteed to run in ``O(1)`` constant-time with negligible constant
          factors.
        * Type-check effectively instantaneously.
        * Add effectively no runtime overhead to the passed callable.

      * If the passed object is a class, this decorator iteratively applies
        itself to all annotated methods of this class by dynamically wrapping
        each such method with a runtime type-checker (as described previously).

    * **Configuration mode.** The caller activates this mode by passing this
      decorator a beartype configuration via the ``conf`` parameter; this
      decorator then creates and returns a new beartype decorator enabling that
      configuration. That decorator may then be called (in decoration mode) to
      create and return a new callable wrapping the passed type-checkable
      object with optimal type-checking configured by that configuration.

    If optimizations are enabled by the active Python interpreter (e.g., due to
    option ``-O`` passed to this interpreter), this decorator silently reduces
    to a noop.

    Parameters
    ----------
    obj : Optional[BeartypeableT]
        **Beartypeable** (i.e., pure-Python callable or class) to be decorated.
        Defaults to ``None``, in which case this decorator is in configuration
        rather than decoration mode. In configuration mode, this decorator
        creates and returns an efficiently cached private decorator that
        generically applies the passed beartype configuration to any
        beartypeable object passed to that decorator. Look... It just works.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to ``BeartypeConf()``, the default ``O(1)`` constant-time configuration.

    Returns
    ----------
    BeartypeReturn
        Either:

        * If in decoration mode (i.e., ``obj`` is *not* ``None` while ``conf``
          is ``None``) *and*:

          * If ``obj`` is a callable, a new callable wrapping that callable
            with dynamically generated type-checking.
          * If ``obj`` is a class, this existing class embellished with
            dynamically generated type-checking.

        * If in configuration mode (i.e., ``obj`` is ``None` while ``conf`` is
          *not* ``None``), a new beartype decorator enabling this
          configuration.

    Raises
    ----------
    BeartypeConfException
        If the passed configuration is *not* actually a configuration (i.e.,
        instance of the :class:`BeartypeConf` class).
    BeartypeDecorHintException
        If any annotation on this callable is neither:

        * A **PEP-compliant type** (i.e., instance or class complying with a
          PEP supported by :mod:`beartype`), including:

          * :pep:`484` types (i.e., instance or class declared by the stdlib
            :mod:`typing` module).

        * A **PEP-noncompliant type** (i.e., instance or class complying with
          :mod:`beartype`-specific semantics rather than a PEP), including:

          * **Fully-qualified forward references** (i.e., strings specified as
            fully-qualified classnames).
          * **Tuple unions** (i.e., tuples containing one or more classes
            and/or forward references).
    BeartypePep563Exception
        If :pep:`563` is active for this callable and evaluating a **postponed
        annotation** (i.e., annotation whose value is a string) on this
        callable raises an exception (e.g., due to that annotation referring to
        local state no longer accessible from this deferred evaluation).
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__beartype_``.
    BeartypeDecorWrappeeException
        If this callable is either:

        * Uncallable.
        * A class, which :mod:`beartype` currently fails to support.
        * A C-based callable (e.g., builtin, third-party C extension).
    BeartypeDecorWrapperException
        If this decorator erroneously generates a syntactically invalid wrapper
        function. This should *never* happen, but here we are, so this probably
        happened. Please submit an upstream issue with our issue tracker if you
        ever see this. (Thanks and abstruse apologies!)
    '''
)
