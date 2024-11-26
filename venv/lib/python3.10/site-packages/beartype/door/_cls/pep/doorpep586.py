#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) literal type hint
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`586`-compliant :attr:`typing.Literal` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsub import _TypeHintSubscripted
from beartype.door._cls.doorsuper import TypeHint
from beartype.typing import Tuple

# ....................{ SUBCLASSES                         }....................
class LiteralTypeHint(_TypeHintSubscripted):
    '''
    **Literal type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`586`-compliant :attr:`typing.Literal` type hint).
    '''

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _args_wrapped_tuple(self) -> Tuple[TypeHint, ...]:

        # Return the empty tuple, thus presenting "Literal" type hints as having
        # *NO* child type hints. Why? Because the arguments subscripting a
        # Literal type hint are *NOT* generally PEP-compliant type hints and
        # thus *CANNOT* be safely wrapped by "TypeHint" instances. These
        # arguments are merely arbitrary values.
        #
        # Note that this property getter is intentionally *NOT* memoized with
        # @property_cached, as Python already efficiently guarantees the empty
        # tuple to be a singleton.
        return ()


    @property
    def _is_args_ignorable(self) -> bool:
        return False

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_subhint(self, other: TypeHint) -> bool:

        # If the passed hint is also a literal, return true only if the set of
        # all child hints subscripting this literal is a subset of the set of
        # all child hints subscripting that literal.
        if isinstance(other, LiteralTypeHint):
            return all(self_arg in other._args for self_arg in self._args)
        # Else, the passed hint is *NOT* also a literal.

        # Return true only if either...
        return (
            # The class of each child hint subscripting this literal is a
            # subhint (e.g., subclass) of the passed hint *OR*...
            #
            # Note that, unlike most type hints, each child hints subscripting
            # this literal is typically *NOT* a valid type hint in and of itself
            # (e.g., "Literal[True]" is a valid type hint, but "True" is not).
            # This test *CANNOT* be reduced to the simpler and sensible variant:
            #     return all(
            #         hint_child.is_subhint(other)
            #         for hint_child in self._args_wrapped_tuple
            #     )
            all(
                TypeHint(type(literal_child)).is_subhint(other)
                for literal_child in self._args
            ) or
            # Else, the class of one or more child hints subscripting this
            # literal is *NOT* a subhint (e.g., subclass) of the passed hint.
            #
            # Defer to the superclass implementation of this method. Why?
            # Because this literal could still be a subhint of passed hint
            # according to standard typing semantics. Notably, this literal
            # could be a child type hint and thus a subhint of the passed type
            # hint - despite failing all of the above literal-specific subhint
            # tests: e.g.,
            #     # The call below handles this surprisingly common edge case.
            #     >>> Literal[True] <= Union[Literal[True], Literal[False]]
            #     True
            super()._is_subhint(other)
        )
