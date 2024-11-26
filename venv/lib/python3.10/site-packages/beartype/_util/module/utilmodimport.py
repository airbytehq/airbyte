#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module importer** utilities (i.e., callables dynamically
importing modules and/or attributes from modules).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeModuleUnimportableWarning
from beartype.roar._roarexc import _BeartypeUtilModuleException
from beartype.typing import (
    Any,
    Optional,
)
from beartype._data.hint.datahinttyping import TypeException
from importlib import import_module as importlib_import_module
from sys import modules as sys_modules
from types import ModuleType
from warnings import warn

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_module_imported_or_none(module_name: str) -> Optional[ModuleType]:
    '''
    Previously imported module, package, or C extension with the passed
    fully-qualified name if previously imported *or* :data:`None` otherwise
    (i.e., if that module, package, or C extension has yet to be imported).

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the previously imported module to be returned.

    Returns
    ----------
    Either:

    * If a module, package, or C extension with this fully-qualified name has
      already been imported, that module, package, or C extension.
    * Else, :data:`None`.
    '''

    # Donkey One-liner Country: Codebase Freeze!
    return sys_modules.get(module_name)

# ....................{ IMPORTERS                          }....................
#FIXME: Preserved until requisite, which shouldn't be long.
#FIXME: Unit test us up, please.
# def import_module(
#     # Mandatory parameters.
#     module_name: str,
#
#     # Optional parameters.
#     exception_cls: TypeException = _BeartypeUtilModuleException,
# ) -> ModuleType:
#     '''
#     Dynamically import and return the module, package, or C extension with the
#     passed fully-qualified name if importable *or* raise an exception
#     otherwise (i.e., if that module, package, or C extension is unimportable).
#
#     Parameters
#     ----------
#     module_name : str
#         Fully-qualified name of the module to be imported.
#     exception_cls : type
#         Type of exception to be raised by this function. Defaults to
#         :class:`_BeartypeUtilModuleException`.
#
#     Raises
#     ----------
#     exception_cls
#         If no module with this name exists.
#     Exception
#         If a module with this name exists *but* that module is unimportable
#         due to raising module-scoped exceptions at importation time. Since
#         modules may perform arbitrary Turing-complete logic at module scope,
#         callers should be prepared to handle *any* possible exception.
#     '''
#     assert isinstance(exception_cls, type), (
#         f'{repr(exception_cls)} not type.')
#
#     # Module with this name if this module is importable *OR* "None" otherwise.
#     module = import_module_or_none(module_name)
#
#     # If this module is unimportable, raise an exception.
#     if module is None:
#         raise exception_cls(
#             f'Module "{module_name}" not found.') from exception
#     # Else, this module is importable.
#
#     # Return this module.
#     return module


def import_module_or_none(module_name: str) -> Optional[ModuleType]:
    '''
    Dynamically import and return the module, package, or C extension with the
    passed fully-qualified name if importable *or* return :data:`None` otherwise
    (i.e., if that module, package, or C extension is unimportable).

    For safety, this function also emits a non-fatal warning when that module,
    package, or C extension exists but is still unimportable (e.g., due to
    raising an exception at module scope).

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be imported.

    Returns
    ----------
    Either:

    * If a module, package, or C extension with this fully-qualified name is
      importable, that module, package, or C extension.
    * Else, :data:`None`.

    Warns
    ----------
    BeartypeModuleUnimportableWarning
        If a module with this name exists *but* that module is unimportable
        due to raising module-scoped exceptions at importation time.
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'

    # Module cached with "sys.modules" if this module has already been imported
    # elsewhere under the active Python interpreter *OR* "None" otherwise.
    module = get_module_imported_or_none(module_name)

    # If this module has already been imported, return this cached module.
    if module is not None:
        return module
    # Else, this module has yet to be imported.

    # Attempt to dynamically import and return this module.
    try:
        return importlib_import_module(module_name)
    # If this module does *NOT* exist, return "None".
    except ModuleNotFoundError:
        pass
    # If this module exists but raises unexpected exceptions from module scope,
    # first emit a non-fatal warning notifying the user and then return "None".
    except Exception as exception:
        warn(
            (
                f'Ignoring module "{module_name}" importation exception:\n'
                f'\t{exception.__class__.__name__}: {exception}'
            ),
            BeartypeModuleUnimportableWarning,
        )

    # Inform the caller that this module is unimportable.
    return None

# ....................{ IMPORTERS ~ attr                   }....................
def import_module_attr(
    # Mandatory parameters.
    module_attr_name: str,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilModuleException,
    exception_prefix: str = 'Module attribute ',
) -> Any:
    '''
    Dynamically import and return the **module attribute** (i.e., object
    declared at module scope) with the passed fully-qualified name if
    importable *or* raise an exception otherwise.

    Parameters
    ----------
    module_attr_name : str
        Fully-qualified name of the module attribute to be imported.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`_BeartypeUtilModuleException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    object
        The module attribute with this fully-qualified name.

    Raises
    ----------
    :exc:`exception_cls`
        If either:

        * This name is syntactically invalid.
        * *No* module prefixed this name exists.
        * A module prefixed by this name exists *but* that module declares no
          attribute by this name.

    Warns
    ----------
    :class:`BeartypeModuleUnimportableWarning`
        If a module prefixed by this name exists *but* that module is
        unimportable due to module-scoped side effects at importation time.

    See Also
    ----------
    :func:`import_module_attr_or_none`
        Further commentary.
    '''

    # Module attribute with this name if that module declares this attribute
    # *OR* "None" otherwise.
    module_attr = import_module_attr_or_none(
        module_attr_name=module_attr_name,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # If this module declares *NO* such attribute, raise an exception.
    if module_attr is None:
        raise exception_cls(
            f'{exception_prefix}"{module_attr_name}" unimportable.')
    # Else, this module declares this attribute.

    # Else, return this attribute.
    return module_attr


def import_module_attr_or_none(
    # Mandatory parameters.
    module_attr_name: str,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilModuleException,
    exception_prefix: str = 'Module attribute ',
) -> Any:
    '''
    Dynamically import and return the **module attribute** (i.e., object
    declared at module scope) with the passed fully-qualified name if
    importable *or* return :data:`None` otherwise.

    Parameters
    ----------
    module_attr_name : str
        Fully-qualified name of the module attribute to be imported.
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`_BeartypeUtilModuleException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    object
        Either:

        * If *no* module prefixed this name exists, :data:`None`.
        * If a module prefixed by this name exists *but* that module declares
          no attribute by this name, ``None``.
        * Else, the module attribute with this fully-qualified name.

    Raises
    ----------
    :exc:`exception_cls`
        If this name is syntactically invalid.

    Warns
    ----------
    :class:`BeartypeModuleUnimportableWarning`
        If a module with this name exists *but* that module is unimportable
        due to raising module-scoped exceptions at importation time.
    '''

    # Avoid circular import dependencies.
    from beartype._util.module.utilmodtest import die_unless_module_attr_name

    # If this object is *NOT* the fully-qualified syntactically valid name of a
    # module attribute that may or may not actually exist, raise an exception.
    die_unless_module_attr_name(
        module_attr_name=module_attr_name,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is the fully-qualified syntactically valid name of a
    # module attribute. In particular, this implies this name to contain one or
    # more "." delimiters.

    # Fully-qualified name of the module declaring this attribute *AND* the
    # unqualified name of this attribute relative to this module, efficiently
    # split from the passed name. By the prior validation, this split is
    # guaranteed to be safe.
    module_name, _, module_attr_basename = module_attr_name.rpartition('.')

    # That module if importable *OR* "None" otherwise.
    module = import_module_or_none(module_name)

    # Return either...
    return (
        # If that module is importable, the module attribute with this name
        # if that module declares this attribute *OR* "None" otherwise;
        getattr(module, module_attr_basename, None)
        if module is not None else
        # Else, that module is unimportable. In this case, "None".
        None
    )
