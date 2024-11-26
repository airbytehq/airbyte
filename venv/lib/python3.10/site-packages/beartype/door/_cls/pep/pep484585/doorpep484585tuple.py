#!/usr/bin/env python3
#--------------------( LICENSE                             )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) callable type hint classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support for
:pep:`484`- and :pep:`585`-compliant ``Tuple[...]`` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsub import _TypeHintSubscripted
from beartype.door._cls.doorsuper import TypeHint
from beartype.typing import Any

# ....................{ SUBCLASSES                         }....................
# FIXME: Document all public and private attributes of this class, please.
class _TupleTypeHint(_TypeHintSubscripted):
    '''
    **Tuple type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`- or :pep:`585`-compliant ``Tuple[...]`` type hint).

    Attributes (Private)
    --------
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint: object) -> None:

        #FIXME: Actually, it might be preferable to define two distinct
        #subclasses:
        #* "class _TypeHintTupleVariadic(_TypeHintSequence)", handling variadic
        #  tuple type hints of the form "Tuple[T, ...]".
        #* "class _TypeHintTupleFixed(_TypeHintSubscripted)", handling
        #  fixed-length tuple type hints.
        #
        #Why? Because variadic and fixed-length tuple type hints have *NOTHING*
        #semantically to do with one another. All they share is the common
        #prefix "Tuple". Aside from that, everything is dissimilar. Indeed,
        #most of the logic below (especially _is_subhint_branch(), which is kinda
        #cray-cray) would strongly benefit from separating this class into two
        #subclasses.
        #
        #Note that implementing this division will probably require generalizing
        #the TypeHint.__new__() method to support this division.

        # Initialize all subclass-specific instance variables for safety.
        self._is_variable_length: bool = False

        #FIXME: Non-ideal. The superclass __len__() method already returns 0 as
        #expected for "Tuple[()]" type hints. Excise us up!
        self._is_empty_tuple: bool = False

        # Initialize the superclass with all passed parameters.
        super().__init__(hint)


    def _make_args(self) -> tuple:

        # Tuple of the zero or more low-level child type hints subscripting
        # (indexing) the low-level parent type hint wrapped by this wrapper.
        args = super()._make_args()

        # Validate these child hints. Specifically, remove any
        # PEP-noncompliant child hints from this tuple and set associated flags.
        #
        # e.g. `Tuple` without any arguments
        # This may be unreachable (since a bare Tuple will go to ClassTypeHint),
        # but it's here for completeness and safety.
        if len(args) == 0:  # pragma: no cover
            args = (Any,)
            self._is_variable_length = True
        #FIXME: This is non-portable and thus basically broken. Ideally, empty
        #tuples should instead be detected by explicitly calling the
        #is_hint_pep484585_tuple_empty() tester.
        elif len(args) == 1 and args[0] == ():
            args = ()
            self._is_empty_tuple = True
        elif len(args) == 2 and args[1] is Ellipsis:
            args = (args[0],)
            self._is_variable_length = True

        # Return these child hints.
        return args

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _is_args_ignorable(self) -> bool:

        #FIXME: Actually, pretty sure this only returns true if this hint is
        #"Tuple[Any, ...]". *shrug*
        # Return true only if this hint is either "Tuple[Any, ...]" or the
        # unsubscripted "Tuple" type hint factory.
        return (
            self._is_variable_length and
            bool(self) and
            self[0].is_ignorable
        )

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_subhint_branch(self, branch: TypeHint) -> bool:

        if branch._is_args_ignorable:
            return issubclass(self._origin, branch._origin)
        elif not isinstance(branch, _TupleTypeHint):
            return False
        elif self._is_args_ignorable:
            return False
        elif branch._is_empty_tuple:
            return self._is_empty_tuple
        elif branch._is_variable_length:
            that_hint = branch._args_wrapped_tuple[0]

            if self._is_variable_length:
                return that_hint.is_subhint(self._args_wrapped_tuple[0])

            return all(
                this_child.is_subhint(that_hint)
                for this_child in self._args_wrapped_tuple
            )
        elif self._is_variable_length:
            return (
                branch._is_variable_length and
                self._args_wrapped_tuple[0].is_subhint(
                    branch._args_wrapped_tuple[0])
            )
        elif len(self._args) != len(branch._args):
            return False

        return all(
            this_child <= that_child
            for this_child, that_child in zip(
                self._args_wrapped_tuple, branch._args_wrapped_tuple
            )
        )
