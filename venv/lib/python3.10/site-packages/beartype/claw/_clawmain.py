#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hooks** (i.e., public-facing functions integrating high-level
:mod:`importlib` machinery required to implement :pep:`302`- and
:pep:`451`-compliant import hooks with the abstract syntax tree (AST)
transformations defined by the low-level :mod:`beartype.claw._ast.clawastmain`
submodule).

This private submodule is the main entry point for this subpackage. Nonetheless,
this private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Improve the beartype_package() and beartype_packages() functions to emit
#non-fatal warnings when the passed package or packages have already been
#imported (i.e., are in the "sys.modules" list).

# ....................{ IMPORTS                            }....................
from beartype.claw._pkg.clawpkgenum import BeartypeClawCoverage
from beartype.claw._pkg.clawpkghook import hook_packages
from beartype.typing import (
    Iterable,
)
from beartype._cave._cavefast import CallableFrameType
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)
from beartype._util.func.utilfuncframe import (
    get_frame,
    get_frame_package_name,
)

# ....................{ HOOKERS                            }....................
def beartype_all(
    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> None:
    '''
    Register a new **universal beartype import path hook** (i.e., callable
    inserted to the front of the standard :mod:`sys.path_hooks` list recursively
    decorating *all* annotated callables, classes, and variable assignments
    across *all* submodules of *all* packages on the first importation of those
    submodules with the :func:`beartype.beartype` decorator, wrapping those
    callables and classes with performant runtime type-checking).

    This function is the runtime equivalent of a full-blown static type checker
    like ``mypy`` or ``pyright``, enabling full-stack runtime type-checking of
    the current app -- including submodules defined by both:

    * First-party proprietary packages directly authored for this app.
    * Third-party open-source packages authored and maintained elsewhere.

    This function is thread-safe.

    Usage
    ----------
    This function is intended to be called from module scope as the first
    statement of the top-level ``__init__`` submodule of the top-level package
    of an app to be fully type-checked by :mod:`beartype`. This function then
    registers an import path hook type-checking *all* annotated callables,
    classes, and variable assignments across *all* submodules of *all* packages
    on the first importation of those submodules: e.g.,

    .. code-block:: python

       # At the very top of "muh_package.__init__":
       from beartype.claw import beartype_all
       beartype_all()  # <-- beartype all subsequent imports, yo

       # Import submodules *AFTER* calling beartype_all().
       from muh_package._some_module import muh_function  # <-- @beartype it!
       from yer_package.other_module import muh_class     # <-- @beartype it!

    Caveats
    ----------
    **This function is not intended to be called from intermediary APIs,
    libraries, frameworks, or other middleware.** This function is *only*
    intended to be called from full stack end-user applications as a convenient
    alternative to manually passing the names of all packages to be type-checked
    to the more granular :func:`.beartype_packages` function. This function
    imposes runtime type-checking on downstream reverse dependencies that may
    not necessarily want, expect, or tolerate runtime type-checking. This
    function should typically *only* be called by proprietary packages not
    expected to be reused by others. Open-source packages are advised to call
    other functions instead.

    **tl;dr:** *Only call this function in non-reusable end-user apps.*

    Parameters
    ----------
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
        Defaults to ``BeartypeConf()``, the default :math:`O(1)` configuration.

    Raises
    ----------
    BeartypeClawHookException
        If the passed ``conf`` parameter is *not* a beartype configuration
        (i.e., :class:`BeartypeConf` instance).

    See Also
    ----------
    :func:`beartype.claw.beartyping`
        Arguably safer alternative to this function isolating the effect of this
        function to only imports performed inside a context manager.
    '''

    # The advantage of one-liners is the vantage of vanity.
    hook_packages(claw_coverage=BeartypeClawCoverage.PACKAGES_ALL, conf=conf)


def beartype_this_package(
    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> None:
    '''
    Register a new **current package beartype import path hook** (i.e., callable
    inserted to the front of the standard :mod:`sys.path_hooks` list recursively
    applying the :func:`beartype.beartype` decorator to *all*
    annotated callables, classes, and variable assignments across *all*
    submodules of the current user-defined package calling this function on the
    first importation of those submodules).

    This function is thread-safe.

    Usage
    ----------
    This function is intended to be called from module scope as the first
    statement of the top-level ``__init__`` submodule of any package to be
    type-checked by :mod:`beartype`. This function then registers an import path
    hook type-checking *all* annotated callables, classes, and variable
    assignments across *all* submodules of that package on the first importation
    of those submodules: e.g.,

    .. code-block:: python

       # At the very top of "muh_package.__init__":
       from beartype.claw import beartype_this_package
       beartype_this_package()  # <-- beartype all subsequent imports, yo

       # Import package submodules *AFTER* calling beartype_this_package().
       from muh_package._some_module import muh_function  # <-- @beartype it!
       from muh_package.other_module import muh_class     # <-- @beartype it!

    Parameters
    ----------
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
        Defaults to ``BeartypeConf()``, the default :math:`O(1)` configuration.

    Raises
    ----------
    BeartypeClawHookException
        If either:

        * This function is *not* called from a module (i.e., this function is
          called directly from within a read–eval–print loop (REPL)).
        * The passed ``conf`` parameter is *not* a beartype configuration
          (i.e., :class:`.BeartypeConf` instance).

    See Also
    ----------
    :func:`.beartype_packages`
        Further details.
    '''

    # Stack frame encapsulating the user-defined lexical scope directly calling
    # this import hook.
    #
    # Note that:
    # * This call is guaranteed to succeed without error. Why? Because:
    #   * The current call stack *ALWAYS* contains at least one stack frame.
    #     Ergo, get_frame(0) *ALWAYS* succeeds without error.
    #   * The call to this import hook guaranteeably adds yet another stack
    #     frame to the current call stack. Ergo, get_frame(1) also *ALWAYS*
    #     succeeds without error in this context.
    # * This and the following logic *CANNOT* reasonably be isolated to a new
    #   private helper function. Why? Because this logic itself calls existing
    #   private helper functions assuming the caller to be at the expected
    #   position on the current call stack.
    frame_caller: CallableFrameType = get_frame(1)  # type: ignore[assignment,misc]

    # Fully-qualified name of the parent package of the child module defining
    # that caller if that module resides in some package *OR* raise an exception
    # otherwise (i.e., if that module is a top-level module or script residing
    # outside any package).
    #
    # Note that raising an exception in the latter case is appropriate here.
    # Why? Because this function uselessly (but silently) reduces to a noop
    # when called by a top-level module or script residing outside any package.
    # Why? Because this function hook installs an import hook applicable only to
    # subsequently imported submodules of the current package. By definition, a
    # top-level module or script has *NO* package and thus *NO* sibling
    # submodules and thus *NO* meaningful imports to be hooked. To avoid
    # unwanted confusion, we intentionally notify the user with an exception.
    frame_caller_package_name = get_frame_package_name(frame_caller)
    # print(f'beartype_this_package: {frame_caller_package_name}')
    # print(f'beartype_this_package: {repr(frame_caller)}')

    # Add a new import path hook beartyping this package.
    hook_packages(
        claw_coverage=BeartypeClawCoverage.PACKAGES_ONE,
        package_name=frame_caller_package_name,
        conf=conf,
    )


#FIXME: Add a "Usage" docstring section resembling that of the docstring for the
#beartype_this_package() function.
def beartype_package(
    # Mandatory parameters.
    package_name: str,

    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> None:
    '''
    Register a new **single package beartype import path hook** (i.e., callable
    inserted to the front of the standard :mod:`sys.path_hooks` list recursively
    applying the :func:`beartype.beartype` decorator to *all* annotated
    callables, classes, and variable assignments across *all* submodules of the
    package with the passed names on the first importation of those submodules).

    This function is thread-safe.

    Parameters
    ----------
    package_name : str
        Fully-qualified name of the package to be type-checked.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
        Defaults to ``BeartypeConf()``, the default :math:`O(1)` configuration.

    Raises
    ----------
    BeartypeClawHookException
        If either:

        * The passed ``conf`` parameter is *not* a beartype configuration (i.e.,
          :class:`BeartypeConf` instance).
        * The passed ``package_name`` parameter is either:

          * *Not* a string.
          * The empty string.
          * A non-empty string that is *not* a valid **package name** (i.e.,
            ``"."``-delimited concatenation of valid Python identifiers).

    See Also
    ----------
    '''

    # Add a new import path hook beartyping this package.
    hook_packages(
        claw_coverage=BeartypeClawCoverage.PACKAGES_ONE,
        package_name=package_name,
        conf=conf,
    )


#FIXME: Add a "Usage" docstring section resembling that of the docstring for the
#beartype_this_package() function.
def beartype_packages(
    # Mandatory parameters.
    package_names: Iterable[str],

    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> None:
    '''
    Register a new **multiple package beartype import path hook** (i.e.,
    callable inserted to the front of the standard :mod:`sys.path_hooks` list
    recursively applying the :func:`beartype.beartype` decorator to *all*
    annotated callables, classes, and variable assignments across *all*
    submodules of all packages with the passed names on the first importation of
    those submodules).

    This function is thread-safe.

    Parameters
    ----------
    package_names : Iterable[str]
        Iterable of the fully-qualified names of one or more packages to be
        type-checked.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
        Defaults to ``BeartypeConf()``, the default :math:`O(1)` configuration.

    Raises
    ----------
    BeartypeClawHookException
        If either:

        * The passed ``conf`` parameter is *not* a beartype configuration (i.e.,
          :class:`BeartypeConf` instance).
        * The passed ``package_names`` parameter is either:

          * Non-iterable (i.e., fails to satisfy the
            :class:`collections.abc.Iterable` protocol).
          * An empty iterable.
          * A non-empty iterable containing at least one item that is either:

            * *Not* a string.
            * The empty string.
            * A non-empty string that is *not* a valid **package name** (i.e.,
              ``"."``-delimited concatenation of valid Python identifiers).

    See Also
    ----------
    '''

    # Add a new import path hook beartyping these packages.
    hook_packages(
        claw_coverage=BeartypeClawCoverage.PACKAGES_MANY,
        package_names=package_names,
        conf=conf,
    )
