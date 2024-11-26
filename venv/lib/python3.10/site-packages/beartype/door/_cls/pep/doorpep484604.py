#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) union type hint classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`-compliant :attr:`typing.Optional` and :attr:`typing.Union` type
hints and :pep:`604`-compliant ``|``-delimited union type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsub import _TypeHintSubscripted
from beartype.door._cls.doorsuper import TypeHint
from beartype.typing import Iterable

# ....................{ SUBCLASSES                         }....................
class UnionTypeHint(_TypeHintSubscripted):
    '''
    **Union type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`-compliant :attr:`typing.Optional` or
    :attr:`typing.Union` type hint *or* :pep:`604`-compliant ``|``-delimited
    union type hint).
    '''

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _branches(self) -> Iterable[TypeHint]:
        return self._args_wrapped_tuple

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_subhint_branch(self, branch: TypeHint) -> bool:
        raise NotImplementedError('UnionTypeHint._is_subhint_branch() unsupported.')  # pragma: no cover


    def _is_subhint(self, other: TypeHint) -> bool:

        # Return true only if *EVERY* child type hint of this union is a subhint
        # of at least one other child type hint of the passed other union.
        #
        # Note that this test has O(n**2) time complexity. Although non-ideal,
        # this is also unavoidable. Thankfully, since most real-world unions are
        # subscripted by only a small number of child type hints, this is also
        # mostly ignorable in practice.
        return all(
            # For each child type hint subscripting this union...
            (
                # If that other type hint is itself a union, true only if...
                any(
                    # For at least one other child type hint subscripting that
                    # other union, this child type hint is a subhint of that
                    # other child type hint.
                    this_branch.is_subhint(that_branch)
                    for that_branch in other._branches
                ) if isinstance(other, UnionTypeHint) else
                # Else, that other type hint is *NOT* a union. In this case,
                # true only if this child type hint is a subhint of that other
                # type hint.
                #
                # Note that this is a common edge case. Examples include:
                # * "TypeHint(Union[...]) <= TypeHint(Any)". Although "Any" is
                #   *NOT* a union, *ALL* unions are subhints of "Any".
                # * "TypeHint(Union[A, B]) <= TypeHint(Union[A])" where "A" is
                #   the superclass of "B". Since Python reduces "Union[A]" to
                #   just "A", this is exactly equivalent to the comparison
                #   "TypeHint(Union[A, B]) <= TypeHint(A)". Although "A" is
                #   *NOT* a union, this example clearly demonstrates that a
                #   union may be a subhint of a non-union that is *NOT* "Any" --
                #   contrary to intuition. Examples include:
                #   * "TypeHint(Union[int, bool]) <= TypeHint(Union[int])".
                this_branch.is_subhint(other)
            )
            for this_branch in self._branches
        )
