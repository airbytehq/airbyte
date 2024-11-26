#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) class type hint classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`-compliant type hints that are, in fact, simple classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsuper import TypeHint
from beartype.typing import (
    TYPE_CHECKING,
    Any,
)

# ....................{ SUBCLASSES                         }....................
class ClassTypeHint(TypeHint):
    '''
    **Class type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`-compliant type hint that is, in fact, a simple class).

    Caveats
    ----------
    This wrapper also intentionally wraps :pep:`484`-compliant :data:``None`
    type hints as the simple type of the :data:``None` singleton, as :pep:`484`
    standardized the reduction of the former to the latter:

         When used in a type hint, the expression None is considered equivalent
         to type(None).

    Although a unique ``NoneTypeHint`` subclass of this class specific to the
    :data:`None` singleton *could* be declared, doing so is substantially
    complicated by the fact that numerous PEP-compliant type hints internally
    elide :data:``None` to the type of that singleton before the `beartype.door`
    API ever sees a distinction. Notably, this includes :pep:`484`-compliant
    unions subscripted by that singleton: e.g.,

    .. code-block:: python

       >>> from typing import Union
       >>> Union[str, None].__args__
       (str, NoneType)
    '''

    # ..................{ STATIC                             }..................
    # Squelch false negatives from static type checkers.
    if TYPE_CHECKING:
        _hint: type

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _is_args_ignorable(self) -> bool:

        # Unconditionally return true, as simple classes are unsubscripted and
        # could thus be said to only have ignorable arguments. Look. Semantics.
        return True

    # ..................{ PRIVATE ~ methods                  }..................
    def _is_subhint_branch(self, branch: TypeHint) -> bool:
        # print(f'is_subhint({repr(self)}, {repr(branch)})?')
        # print(f'{repr(self)}._origin: {self._origin}')
        # # print(f'{repr(self)}._origin.__args__: {self._origin.__args__}')
        # print(f'{repr(self)}._origin.__parameters__: {self._origin.__parameters__}')
        # print(f'{repr(branch)}._origin: {branch._origin}')
        # # print(f'{repr(branch)}._origin.__args__: {branch._origin.__args__}')
        # print(f'{repr(branch)}._origin.__parameters__: {branch._origin.__parameters__}')
        # print(f'{repr(self)}._is_args_ignorable: {self._is_args_ignorable}')
        # print(f'{repr(branch)}._is_args_ignorable: {branch._is_args_ignorable}')

        #FIXME: *UGH.* This is redundant. Ideally:
        #* There should exist a concrete TypeHint._is_subhint_branch()
        #  implementation performing this logic on behalf of *EVERY* subclass.
        #* TypeHint._is_subhint_branch() should then call a subclass-specific
        #  abstract TypeHint._is_subhint_branch_override() method.
        #FIXME: Actually, TypeHint._is_subhint_branch() is only called in
        #exactly one place: by TypeHint._is_subhint(). So, the simpler solution
        #would be to simply implement the following tests there, please.

        # Everything is a subclass of "Any".
        if branch._hint is Any:
            return True

        #FIXME: *UHM.* Wat? Do we really currently wrap "typing.Any" with an
        #instance of this class? Why? That makes *NO* sense. "typing.Any" should
        #be wrapped by its own "TypeHintAny" subclass, please. *sigh*
        # "Any" is only a subclass of "Any".
        elif self._hint is Any:
            return False

        #FIXME: Actually, let's avoid the implicit numeric tower for now.
        #Explicit is better than implicit and we really strongly disagree with
        #this subsection of PEP 484, which does more real-world harm than good.
        # # Numeric tower:
        # # https://peps.python.org/pep-0484/#the-numeric-tower
        # if self._origin is float and branch._origin in {float, int}:
        #     return True
        # if self._origin is complex and branch._origin in {complex, float, int}:
        #     return True

        #FIXME: This simplistic logic fails to account for parametrized
        #generics. To do so, we'll probably want to:
        #* Define a new "beartype.door._cls._pep.pep484585.doorpep484585generic"
        #  submodule.
        #* In that submodule:
        #  * Define a new "GenericTypeHint" subclass initially simply
        #    copy-pasted from this subclass.
        #* Incorporate that subclass into the "beartype.door._doordata"
        #  submodule.
        #* Validate that tests still pass.
        #* Begin implementing custom generic-specific logic in the
        #  "GenericTypeHint" subclass. Notably, this tester should be refactored
        #  as follows:
        #  # If this generic is *NOT* a subclass of that generic, then this generic
        #  # is *NOT* a subhint of that generic. In this case, return false.
        #  if not issubclass(self._hint, branch._hint):
        #      return False
        #  # Else, this generic is a subclass of that generic. Note, however,
        #  # that this does *NOT* imply this generic to be a subhint of that
        #  # generic. The issubclass() builtin ignores parametrizations and thus
        #  # returns false positives for parametrized generics: e.g.,
        #  #     >>> from typing import Generic, TypeVar
        #  #     >>> T = TypeVar('T')
        #  #     >>> class MuhGeneric(Generic[T]): pass
        #  #     >>> issubclass(MuhGeneric, MuhGeneric[int])
        #  #     True
        #  #
        #  # Clearly, the unsubscripted generic "MuhGeneric" is a superhint
        #  # (rather than a subhint) of the subscripted generic
        #  # "MuhGeneric[int]". Further introspection is needed to decide how
        #  # exactly these two generics interrelate.
        #
        #  #FIXME: Do something intelligent here. In particular, we probably
        #  #*MUST* expand unsubscripted generics like "MuhGeneric" to their
        #  #full transitive subscriptions like "MuhGeneric[T]". Of course,
        #  #"MuhGeneric" has *NO* "__args__" and only an empty "__parameters__";
        #  #both are useless. Ergo, we have *NO* recourse but to iteratively
        #  #reconstruct the full transitive subscriptions for unsubscripted
        #  #generics by iterating with the
        #  #iter_hint_pep484585_generic_bases_unerased_tree() iterator. The idea
        #  #here is that we want to iteratively inspect first the "__args__" and
        #  #then the "__parameters__" of all superclasses of both "self" and
        #  #"branch" until obtaining two n-tuples (where "n" is the number of
        #  #type variables with which the root "Generic[...]" superclass was
        #  #originally subscripted):
        #  #* "self_args", the n-tuple of all types or type variables
        #  #   subscripting this generic.
        #  #* "branch_args", the n-tuple of all types or type variables
        #  #   subscripting the "branch" generic.
        #  #
        #  #Once we have those two n-tuples, we can then decide the is_subhint()
        #  #relation by simply iteratively subjecting each pair of items from
        #  #both "self_args" and "branch_args" to is_subhint(). Notably, we
        #  #return True if and only if is_subhint() returns True for *ALL* pairs
        #  #of items of these two n-tuples.

        # Return true only if...
        return (
            # This class is unsubscripted (and thus *NOT* a subscripted generic)
            # *AND*...
            branch._is_args_ignorable and
            # This class is a subclass of that class.
            issubclass(self._origin, branch._origin)
        )
