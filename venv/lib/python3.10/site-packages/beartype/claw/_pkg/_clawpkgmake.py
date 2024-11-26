#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook factories** (i.e., low-level utility functions creating
and returning objects of interest to higher-level import hook functions).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw._pkg.clawpkgenum import BeartypeClawCoverage
from beartype.roar import (
    BeartypeClawDecorWarning,
    BeartypeClawHookException,
)
from beartype.typing import (
    Iterable,
    Optional,
)
from beartype._conf.confcls import BeartypeConf
from beartype._util.text.utiltextidentifier import die_unless_identifier
from collections.abc import Iterable as IterableABC

# ....................{ PRIVATE ~ factories                }....................
#FIXME: Unit test us up, please.
def make_conf_hookable(conf: BeartypeConf) -> BeartypeConf:
    '''
    New **hookable beartype configuration** (i.e., beartype configuration
    suitable for use in import hooks, sanitized from the passed beartype
    configuration which is typically unsuitable for use in import hooks).

    This getter creates and returns a new configuration permuted from the passed
    configuration, forcefully enabling these parameters required by import
    hooks:

    * :attr:`beartype.BeartypeConf.warning_cls_on_decorator_exception`
      to the :class:`beartype.roar.BeartypeClawDecorWarning` warning category.
      Doing so instructs the :func:`beartype.beartype` decorator to emit
      non-fatal warnings rather than raise fatal exceptions at decoration time
      when implicitly decorating callables and classes defined by modules hooked
      by our import hooks, substantially improving the robustness and usability
      of those hooks.

    Returns
    ----------
    Optional[Iterable[str]]
        Iterable of the fully-qualified names of one or more packages to be
        either hooked or unhooked by the parent call.

    Raises
    ----------
    BeartypeClawHookException
        If the passed ``conf`` parameter is *not* a beartype configuration
        (i.e., :class:`BeartypeConf` instance).

    See Also
    ----------
    :func:`.hook_packages`
        Further details.
    '''

    # If the "conf" parameter is *NOT* a configuration, raise an exception.
    if not isinstance(conf, BeartypeConf):
        raise BeartypeClawHookException(
            f'Beartype configuration {repr(conf)} invalid (i.e., not '
            f'"beartype.BeartypeConf" instance).'
        )
    # Else, the "conf" parameter is a configuration.

    # If the caller did *NOT* explicitly set the
    # "warning_cls_on_decorator_exception" configuration parameter governing the
    # reduction of fatal exceptions to non-fatal warnings at @beartype
    # decoration-time...
    if not conf._is_warning_cls_on_decorator_exception_set:
        # Keyword dictionary with which to instantiate a new configuration
        # reducing fatal exceptions to non-fatal warnings of a warning category
        # specific to beartype import hooks.
        conf_kwargs = conf.kwargs.copy()
        conf_kwargs['warning_cls_on_decorator_exception'] = (
            BeartypeClawDecorWarning)

        # Replace this configuration with this new configuration.
        conf = BeartypeConf(**conf_kwargs)  # type: ignore[arg-type]
    # Else, this caller already explicitly set the
    # "warning_cls_on_decorator_exception" configuration parameter governing the
    # reduction of fatal exceptions to non-fatal warnings at @beartype
    # decoration-time. In this case, preserve this user-defined reduction as is.

    # Return this possibly new configuration.
    return conf


#FIXME: Unit test us up, please.
def make_package_names_from_args(
    # Keyword-only arguments.
    *,

    # Mandatory keyword-only arguments.
    claw_coverage: BeartypeClawCoverage,
    conf: BeartypeConf,

    # Optional keyword-only arguments.
    package_name: Optional[str] = None,
    package_names: Optional[Iterable[str]] = None,
) -> Optional[Iterable[str]]:
    '''
    Validate all parameters passed by the caller to the parent
    :func:`.hook_packages` or :func:`.unhook_packages` function.

    Returns
    ----------
    Optional[Iterable[str]]
        Iterable of the fully-qualified names of one or more packages to be
        either hooked or unhooked by the parent call.

    Raises
    ----------
    BeartypeClawHookException
        If the passed ``package_names`` parameter is either:

        * Neither a string nor an iterable (i.e., fails to satisfy the
          :class:`collections.abc.Iterable` protocol).
        * An empty string or iterable.
        * A non-empty string that is *not* a valid **package name** (i.e.,
          ``"."``-delimited concatenation of valid Python identifiers).
        * A non-empty iterable containing at least one item that is either:

          * *Not* a string.
          * The empty string.
          * A non-empty string that is *not* a valid **package name** (i.e.,
            ``"."``-delimited concatenation of valid Python identifiers).

    See Also
    ----------
    :func:`.hook_packages`
        Further details.
    '''
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'
    assert isinstance(claw_coverage, BeartypeClawCoverage), (
        f'{repr(claw_coverage)} not beartype claw coverage.')

    # If the caller requested all-packages coverage...
    if claw_coverage is BeartypeClawCoverage.PACKAGES_ALL:
        # If the caller improperly passed a package name despite requesting
        # all-packages coverage, raise an exception.
        if package_name is not None:
            raise BeartypeClawHookException(
                f'Coverage {repr(BeartypeClawCoverage.PACKAGES_ALL)} '
                f'but package name {repr(package_name)} passed.'
            )
        # Else, the caller properly passed *NO* package name.
        #
        # If the caller improperly passed multiple package names despite
        # requesting all-packages coverage, raise an exception.
        elif package_names is not None:
            raise BeartypeClawHookException(
                f'Coverage {repr(BeartypeClawCoverage.PACKAGES_ALL)} '
                f'but package names {repr(package_names)} passed.'
            )
        # Else, the caller properly passed *NO* package names.
    # Else, the caller did *NOT* request all-packages coverage. In this case,
    # the caller requested coverage over only a subset of packages.
    else:
        # If the caller requested mono-package coverage...
        if claw_coverage is BeartypeClawCoverage.PACKAGES_ONE:
            # If the caller improperly passed *NO* package name despite
            # requesting mono-package coverage, raise an exception.
            if package_name is None:
                raise BeartypeClawHookException(
                    f'beartype_package() '
                    f'package name {repr(package_name)} invalid.'
                )
            # Else, the caller properly passed a package name.

            # Wrap this package name in a 1-tuple containing only this name.
            # Doing so unifies logic below.
            package_names = (package_name,)
        # Else, the caller requested multi-package coverage.
        # elif coverage is BeartypeClawCoverage.PACKAGES_MANY:

        # If this package names is *NOT* iterable, raise an exception.
        if not isinstance(package_names, IterableABC):
            raise BeartypeClawHookException(
                f'beartype_packages() '
                f'package names {repr(package_name)} not iterable.'
            )
        # Else, this package names is iterable.
        #
        # If *NO* package names were passed, raise an exception.
        elif not package_names:
            raise BeartypeClawHookException(
                'beartype_packages() package names empty.')
        # Else, one or more package names were passed.

        # For each such package name...
        for package_name in package_names:
            # If this package name is *NOT* a string, raise an exception.
            if not isinstance(package_name, str):
                raise BeartypeClawHookException(
                    f'Package name {repr(package_name)} not string.')
            # Else, this package name is a string.
            #
            # If this package name is *NOT* a valid Python identifier, raise an
            # exception.
            else:
                die_unless_identifier(
                    text=package_name,
                    exception_cls=BeartypeClawHookException,
                    exception_prefix='Package name ',
                )
            # Else, this package name is a valid Python identifier.

    # Return the iterable of the fully-qualified names of one or more packages
    # to be either hooked or unhooked by the parent call.
    return package_names
