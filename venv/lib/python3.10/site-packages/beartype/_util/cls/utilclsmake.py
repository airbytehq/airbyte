#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable factories** (i.e., low-level functions dynamically
creating and returning new in-memory callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilTypeException
from beartype.typing import (
    Optional,
    Type,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._data.hint.datahinttyping import (
    LexicalScope,
    TupleTypes,
    TypeException,
)
from beartype._data.kind.datakinddict import DICT_EMPTY
from beartype._util.text.utiltextidentifier import die_unless_identifier

# ....................{ MAKERS                             }....................
def make_type(
    # Mandatory arguments.
    type_name: str,

    # Optional arguments.
    type_module_name: Optional[str] = None,
    type_bases: Optional[TupleTypes] = None,
    type_scope: Optional[LexicalScope] = None,
    type_doc: Optional[str] = None,
    exception_cls: TypeException = _BeartypeUtilTypeException,
) -> type:
    '''
    Dynamically create and return a new class with the passed name subclassing
    all passed base classes and defined by the passed class scope.

    Parameters
    ----------
    type_name : str
        Name of the class to be created.
    type_module_name : Optional[str]
        Fully-qualified name of the module declaring this class. Defaults to
        :data:`None`, in which case this class remains undeclared by any module.
    type_bases : Optional[Tuple[type, ...]]
        Tuple of all base classes to be inherited by this class. Defaults to
        the empty tuple, equivalent to the 1-tuple ``(object,)`` inheriting this
        class from only the root base class :class:`object` of all classes.
    type_scope : Optional[Dict[str, Any]]
        Dictionary mapping from the name to value of each **class-scoped
        attribute** (i.e., method, variable) to be defined by this class.
        Defaults to the empty dictionary, equivalent to declaring a class with
        the trivial body ``pass``.
    type_doc : Optional[str]
        Human-readable docstring documenting this class. Defaults to
        :data:`None`, in which case this class remains undocumented.
    exception_cls : Type[Exception], optional
        Type of exception to raise in the event of a fatal error. Defaults to
        :exc:`._BeartypeUtilTypeException`.

    Returns
    ----------
    type
        Class with this name subclassing these base classes and defined by this
        class scope.

    Raises
    ----------
    exception_cls
        If either:

        * The passed classname is empty.
        * The passed classname is non-empty but *not* a valid unqualified Python
          identifier.
    '''
    assert isinstance(type_name, str), f'{repr(type_name)} not string.'
    assert isinstance(type_module_name, NoneTypeOr[str]), (
        f'{repr(type_module_name)} neither string nor "None".')
    assert isinstance(type_doc, NoneTypeOr[str]), (
        f'{repr(type_doc)} neither string nor "None".')

    # If this classname is *NOT* a valid unqualified Python identifier, raise an
    # exception. Insanely, the builtin type.__init__() constructor silently
    # allows this classname to be invalid -- despite the resulting class
    # violating sanity and normative standards. Note that invalid names include:
    # * The empty string.
    # * An invalid Python identifier.
    # * A valid fully-qualified Python identifier.
    if not type_name.isidentifier():
        raise exception_cls(f'Class name {repr(type_name)} invalid.')
    # Else, this classname is a valid unqualified Python identifier.

    # Default all unpassed parameters.
    if type_bases is None:
        type_bases = ()  # type: ignore[assignment]
    if type_scope is None:
        type_scope = DICT_EMPTY  # type: ignore[assignment]
    assert isinstance(type_bases, tuple), (
        f'{repr(type_bases)} neither tuple nor "None".')
    assert isinstance(type_scope, dict), (
        f'{repr(type_scope)} neither dictionary nor "None".')

    # Thank you, bizarre 3-parameter variant of the type.__init__() constructor.
    cls = type(type_name, type_bases, type_scope)

    # If this class has a module name...
    if type_module_name is not None:
        # If this module name is *NOT* a valid Python identifier, raise an
        # exception.
        die_unless_identifier(
            text=type_module_name,
            exception_cls=exception_cls,
            exception_prefix='Class module name ',
        )
        # Else, this module name is a valid Python identifier.

        # Set the module name of this class.
        cls.__module__ = type_module_name
    # Else, this class has *NO* module name.

    # If documenting this class, do so.
    if type_doc is not None:
        cls.__doc__ = type_doc
    # Else, this class is undocumented.

    # Return this class.
    return cls
