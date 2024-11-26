#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward scope classes** (i.e., dictionary subclasses deferring the
resolutions of local and global scopes of classes and callables decorated by the
:func:`beartype.beartype` decorator when dynamically evaluating stringified type
hints for those classes and callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.typing import Type
from beartype._data.hint.datahinttyping import LexicalScope
from beartype._check.forward._fwdref import (
    make_forwardref_indexable_subtype,
    _BeartypeForwardRefIndexableABC,
)
from beartype._util.text.utiltextidentifier import die_unless_identifier
# from sys import modules as sys_modules

# ....................{ SUBCLASSES                         }....................
#FIXME: Unit test us up, please.
class BeartypeForwardScope(LexicalScope):
    '''
    **Forward scope** (i.e., dictionary mapping from the name to value of each
    locally and globally accessible attribute in the local and global scope of a
    class or callable as well as deferring the resolution of each currently
    undeclared attribute in that scope by replacing that attribute with a
    forward reference proxy resolved only when that attribute is passed as the
    second parameter to an :func:`isinstance`-based runtime type-check).

    This dictionary is principally employed to dynamically evaluate stringified
    type hints, including:

    * :pep:`484`-compliant forward references.
    * :pep:`563`-postponed type hints.

    Attributes
    ----------
    _scope_dict : LexicalScope
        **Composite local and global scope** (i.e., dictionary mapping from
        the name to value of each locally and globally accessible attribute
        in the local and global scope of some class or callable) underlying
        this forward scope. See the :meth:`__init__` method for details.
    _scope_name : str
        Fully-qualified name of this forward scope. See the :meth:`__init__`
        method for details.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_scope_dict',
        '_scope_name',
    )

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, scope_dict: LexicalScope, scope_name: str) -> None:
        '''
        Initialize this forward scope.

        Attributes
        ----------
        scope_dict : LexicalScope
            **Composite local and global scope** (i.e., dictionary mapping from
            the name to value of each locally and globally accessible attribute
            in the local and global scope of some class or callable) underlying
            this forward scope.

            Crucially, **this dictionary must composite both the local and
            global scopes for that class or callable.** This dictionary must
            *not* provide only the local or global scope; this dictionary must
            provide both. Why? Because this forward scope is principally
            intended to be passed as the second and last parameter to the
            :func:`eval` builtin, called by the
            :func:`beartype._check.forward.fwdhint.resolve_hint` function. For
            unknown reasons, :func:`eval` only calls the :meth:`__missing__`
            dunder method of this forward scope when passed only two parameters
            (i.e., when passed only a global scope); :func:`eval` does *not*
            call the :meth:`__missing__` dunder method of this forward scope
            when passed three parameters (i.e., when passed both a global and
            local scope). Presumably, this edge case pertains to the official
            :func:`eval` docstring -- which reads:

                The globals must be a dictionary and locals can be any mapping,
                defaulting to the current globals and locals.
                If only globals is given, locals defaults to it.

            Clearly, :func:`eval` treats globals and locals fundamentally
            differently (probably for efficiency or obscure C implementation
            details). Since :func:`eval` only supports a single unified globals
            dictionary for our use case, the caller *must* composite together
            the global and local scopes into this dictionary. Praise to Guido.
        scope_name : str
            Fully-qualified name of this forward scope. For example:

            * ``"some_package.some_module"`` for a module scope (e.g., to
              resolve a global class or callable against this scope).
            * ``"some_package.some_module.SomeClass"`` for a class scope (e.g.,
              to resolve a nested class or callable against this scope).

        Raises
        ----------
        BeartypeDecorHintForwardRefException
            If this scope name is *not* a valid Python attribute name.
        '''
        assert isinstance(scope_dict, dict), (
            f'{repr(scope_dict)} not dictionary.')

        # Initialize our superclass with this lexical scope, efficiently
        # pre-populating this dictionary with all previously declared attributes
        # underlying this forward scope.
        super().__init__(scope_dict)

        # If this scope name is syntactically invalid, raise an exception.
        die_unless_identifier(
            text=scope_name,
            exception_cls=BeartypeDecorHintForwardRefException,
            exception_prefix='Forward scope name ',
        )
        # Else, this scope name is syntactically valid.

        # Classify all passed parameters.
        self._scope_dict = scope_dict
        self._scope_name = scope_name

    # ..................{ DUNDERS                            }..................
    def __missing__(self, hint_name: str) -> Type[
        _BeartypeForwardRefIndexableABC]:
        '''
        Dunder method explicitly called by the superclass
        :meth:`dict.__getitem__` method implicitly called on each ``[``- and
        ``]``-delimited attempt to access an **unresolved type hint** (i.e.,
        *not* currently defined in this scope) with the passed name.

        This method transparently replaces this unresolved type hint with a
        **forward reference proxy** (i.e., concrete subclass of the private
        :class:`beartype._check.forward._fwdref._BeartypeForwardRefABC` abstract
        base class (ABC), which resolves this type hint on the first call to the
        :func:`isinstance` builtin whose second argument is that subclass).

        This method assumes that:

        * This scope is only partially initialized.
        * This type hint has yet to be declared in this scope.
        * This type hint will be declared in this scope by the later time that
          this method is called.

        Parameters
        ----------
        hint_name : str
            Relative (i.e., unqualified) or absolute (i.e., fully-qualified)
            name of this unresolved type hint.

        Returns
        ----------
        Type[_BeartypeForwardRefIndexableABC]
            Forward reference proxy deferring the resolution of this unresolved
            type hint.

        Raises
        ----------
        BeartypeDecorHintForwardRefException
            If this type hint name is *not* a valid Python attribute name.
        '''
        # print(f'Missing type hint: {repr(hint_name)}')

        # If this type hint name is syntactically invalid, raise an exception.
        die_unless_identifier(
            text=hint_name,
            exception_cls=BeartypeDecorHintForwardRefException,
            exception_prefix='Forward reference ',
        )
        # Else, this type hint name is syntactically valid.

        # Forward reference proxy to be returned.
        forwardref_subtype = make_forwardref_indexable_subtype(
            self._scope_name, hint_name)

        # Return this proxy. The superclass dict.__getitem__() dunder method
        # then implicitly maps the passed unresolved type hint name to this
        # proxy by effectively assigning this name to this proxy: e.g.,
        #     self[hint_name] = forwardref_subtype
        return forwardref_subtype
