#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python module getter** (i.e., callables dynamically retrieving
modules and/or attributes in modules) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import ModuleType
from beartype.roar._roarexc import _BeartypeUtilModuleException
from beartype.typing import Optional
from inspect import findsource
from pathlib import Path
from sys import modules as sys_modules

# ....................{ GETTERS ~ object                   }....................
def get_object_module_or_none(obj: object) -> Optional[ModuleType]:
    '''
    Module declaring the passed object if this object defines the ``__module__``
    dunder instance variable *or* :data:`None` otherwise.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    Optional[ModuleType]
        Either:

        * Module declaring this object if this object declares a ``__module__``
          dunder attribute.
        * :data:`None` otherwise.
    '''

    # Fully-qualified name of the module defining this object if any or "None".
    module_name = get_object_module_name_or_none(obj)

    # Return either:
    # * If a module defines this object, that module.
    # * Else, "None".
    return sys_modules.get(module_name) if module_name else None


def get_object_module(obj: object) -> ModuleType:
    '''
    Module declaring the passed object if this object defines the ``__module__``
    dunder instance variable *or* raise an exception otherwise (i.e., if this
    object does *not* define that variable).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    ModuleType
        Module declaring this object.

    Raises
    ----------
    _BeartypeUtilModuleException
        If this object does *not* define the ``__module__`` dunder attribute.
    '''

    # Fully-qualified name of the module defining this object if any *OR* raise
    # an exception otherwise.
    module_name = get_object_module_name(obj)

    # Module defining this object if any *OR* "None" otherwise.
    module = sys_modules.get(module_name)

    # If this module was *NOT* previously imported despite this object existing
    # and thus having been imported from something, this object deceptively lies
    # about its module. In this case, raise an exception.
    if module is None:
        raise _BeartypeUtilModuleException(
            f'{repr(obj)} module "{module_name}" not found.')
    # If this module was previously imported.

    # Return this module.
    return module

# ....................{ GETTERS ~ object : line            }....................
def get_object_module_line_number_begin(obj: object) -> int:
    '''
    **Line number** (i.e., 1-based index) of the first line of the source code
    of the module declaring the passed object if this object is either a
    callable or class *or* raise an exception otherwise (i.e., if this object is
    neither a callable nor class).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    int
        1-based index of the first line of the source code of the module
        declaring the passed object.

    Raises
    ----------
    _BeartypeUtilModuleException
        If this object is neither a callable nor class.
    '''

    # If this object is a class, defer to the standard "inspect" module.
    #
    # Note that:
    # * Deciding whether an object is a class is slightly faster than deciding
    #   whether an object is a callable. The former trivially reduces to a
    #   single isinstance() call against a single superclass; the latter is
    #   considerably less trivial. Ergo, this object is tested as a class first.
    # * Deciding the line number of the first line declaring an arbitrary class
    #   in its underlying source code module file is highly non-trivial (and in
    #   fact requires extremely slow AST-based parsing). For maintainability and
    #   robustness, we defer to the well-tested standard "inspect" module
    #   despite the performance hit in doing so.
    if isinstance(obj, type):
        _, cls_source_line_number_start = findsource(obj)
        return cls_source_line_number_start
    # Else, this object is *NOT* a class.

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunccodeobj import get_func_codeobj_or_none

    # Code object underlying this object if this object is a pure-Python
    # callable *OR* "None" otherwise.
    #
    # Note this is the canonical means of deciding whether an arbitrary object
    # is a pure-Python callable, as our is_func_python() function demonstrates.
    func_codeobj = get_func_codeobj_or_none(obj)

    # If this object is a pure-Python callable, return the line number of the
    # first line declaring this object in its underlying source code file.
    if func_codeobj is not None:
        return func_codeobj.co_firstlineno
    # Else, this object is neither a pure-Python callable *NOR* a class.

    # In this case, raise an exception.
    raise _BeartypeUtilModuleException(
        f'{repr(obj)} neither callable nor class.')

# ....................{ GETTERS ~ object : name            }....................
#FIXME: Unit test us up, please.
def get_object_module_name(obj: object) -> str:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited name prefixed by the
    declaring package) of the module declaring the passed object if this
    object defines the ``__module__`` dunder instance variable *or* raise an
    exception otherwise (i.e., if this object does *not* define that variable).

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    str
        Fully-qualified name of the module declaring this object.

    Raises
    ----------
    _BeartypeUtilModuleException
        If this object does *not* define the ``__module__`` dunder attribute.
    '''

    # Fully-qualified name of the module declaring this object if this object
    # defines the "__module__" dunder instance variable *OR* "None" otherwise.
    module_name = get_object_module_name_or_none(obj)

    # If this object defines *NO* "__module__" dunder instance variable, raise
    # an exception.
    if module_name is None:
        raise _BeartypeUtilModuleException(
            f'{repr(obj)} "__module__" dunder attribute undefined '
            f'(e.g., due to being neither class nor callable).'
        )
    # Else, this fully-qualified module name exists.

    # Return this name.
    return module_name


#FIXME: Unit test us up, please.
def get_object_module_name_or_none(obj: object) -> Optional[str]:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited name prefixed by the
    declaring package) of the module declaring the passed object if this object
    defines the ``__module__`` dunder instance variable *or* :data:`None`
    otherwise.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    Optional[str]
        Either:

        * Fully-qualified name of the module declaring this object if this
          object declares a ``__module__`` dunder attribute.
        * :data:`None` otherwise.
    '''

    # Let it be, speaking one-liners of wisdom.
    return getattr(obj, '__module__', None)

# ....................{ GETTERS ~ object : type : name     }....................
#FIXME: Unit test us up, please.
def get_object_type_module_name_or_none(obj: object) -> Optional[str]:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited name prefixed by the
    declaring package) of the module declaring either the passed object if this
    object is a class *or* the class of this object otherwise (i.e., if this
    object is *not* a class) if this class declares the ``__module__`` dunder
    instance variable *or* ``None`` otherwise.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    Optional[str]
        Either:

        * Fully-qualified name of the module declaring the type of this object
          if this type declares a ``__module__`` dunder attribute.
        * ``None`` otherwise.
    '''

    # Avoid circular import dependencies.
    from beartype._util.utilobject import get_object_type_unless_type

    # Make it so, ensign.
    return get_object_module_name_or_none(get_object_type_unless_type(obj))

# ....................{ GETTERS ~ module : dir             }....................
#FIXME: Unit test us up.
def get_module_dir(module: ModuleType) -> Path:
    '''
    High-level :class:`Path` object encapsulating the absolute dirname of the
    parent directory containing the passed module if this module is physically
    defined on-disk *or* raise an exception otherwise (i.e., if this module is
    abstractly defined only in-memory).

    Parameters
    ----------
    module : ModuleType
        Module to be inspected.

    Returns
    ----------
    Path
        High-level :class:`Path` object encapsulating the absolute dirname of
        the parent directory containing this on-disk module.

    Raises
    ----------
    _BeartypeUtilModuleException
        If this module *only* resides in memory.
    '''

    # Absolute filename of this module if this module is physically defined
    # on-disk *OR* raise an exception otherwise (i.e., if this module is
    # abstractly defined only in-memory).
    module_filename = get_module_filename(module)

    # High-level "Path" object encapsulating this file and the parent directory
    # directly containing this file.
    module_file = Path(module_filename)
    module_dir = module_file.parent

    # Return this "Path" object.
    return module_dir

# ....................{ GETTERS ~ module : file            }....................
#FIXME: Unit test us up.
def get_module_filename(module: ModuleType) -> str:
    '''
    Absolute filename of the passed module if this module is physically defined
    on-disk *or* raise an exception otherwise (i.e., if this module is
    abstractly defined only in-memory).

    Parameters
    ----------
    module : ModuleType
        Module to be inspected.

    Returns
    ----------
    str
        Absolute filename of this on-disk module.

    Raises
    ----------
    _BeartypeUtilModuleException
        If this module *only* resides in memory.

    See Also
    ----------
    :func:`get_module_filename_or_none`
        Further details.
    '''

    # Absolute filename of this module if on-disk *OR* "None" otherwise.
    module_filename = get_module_filename_or_none(module)

    # If this module resides *ONLY* in memory, raise an exception.
    if module_filename is None:
        raise _BeartypeUtilModuleException(
            f'Module {repr(module)} file not found '
            f'(e.g., due to either being a namespace (sub)package or '
            f'a dynamically defined in-memory module).'
        )
    # Else, this module resides on disk.

    # Return this filename.
    return module_filename


#FIXME: Unit test us up.
def get_module_filename_or_none(module: ModuleType) -> Optional[str]:
    '''
    Absolute filename of the passed module if this module is physically defined
    on-disk *or* :data:`None` otherwise (i.e., if this module is abstractly
    defined only in-memory).

    Specifically, this getter returns either:

    * If this module is actually a package, the absolute filename of the
      ``"__init__.py"`` submodule directly contained in this package.
    * Else, the absolute filename of this module as provided by the `__file__`
      dunder attribute of this in-memory module object.

    In either case, the filename returned by this getter (if any) necessarily
    refers to a file rather than a directory.

    Parameters
    ----------
    module : ModuleType
        Module to be inspected.

    Returns
    ----------
    Optional[str]
        Either:

        * Absolute filename of this module if this module resides on disk.
        * :data:`None` if this module *only* resides in memory.
    '''

    # Thus spake Onelinerthustra.
    return getattr(module, '__file__', None)
