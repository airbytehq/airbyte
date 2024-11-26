#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) new-type type hint classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`-compliant :attr:`typing.NewType` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.pep.pep484.doorpep484class import ClassTypeHint
from beartype._util.cls.utilclsmake import make_type
from beartype._util.hint.pep.proposal.pep484.utilpep484newtype import (
    get_hint_pep484_newtype_alias)

# ....................{ SUBCLASSES                         }....................
class NewTypeTypeHint(ClassTypeHint):
    '''
    **New-type type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`-compliant :attr:`typing.NewType` type hint).
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint: object) -> None:

        # Initialize the superclass with all passed parameters.
        super().__init__(hint)

        # Non-new type type hint encapsulated by this new type.
        hint_embedded = get_hint_pep484_newtype_alias(hint)

        # If this non-new type hint is a class...
        if isinstance(hint_embedded, type):
            #FIXME: Define a new get_hint_pep484_newtype_name() getter ala:
            #    def get_hint_pep484_newtype_name(
            #        hint: Any, exception_prefix: str = '') -> type:
            #        #FIXME: Does this suffice? Does "NewType" guarantee the
            #        #"__name__" instance variable to exist? No idea. *sigh*
            #        return getattr(hint, '__name__')
            #Then, call that below in lieu of the "name = getattr(...)" call.
            # Unqualified basename of the new subclass of this class to be
            # created below.
            hint_name = getattr(hint, '__name__', str(hint))

            # Dynamically synthesize a new subclass of this class with the name
            # of this new type, effectively fabricating a fake origin type
            # treating this new type as a subclass of this class. For example,
            # if this new type is "NewType("MyType", str)", then this logic
            # fabricates a fake origin type resembling:
            #     class MyString(str): pass
            #
            # Note that this would typically be non-ideal due to explosive space
            # and time consumption. Thankfully, however, "TypeHint" wrappers are
            # cached; the "_TypeHintMeta" metaclass guarantees this __init__()
            # method to be called exactly once for each "NewType" type hint.
            self._origin = make_type(
                type_name=hint_name,
                type_bases=(hint_embedded,),  # type: ignore[arg-type]
            )
        # Else, this non-new type hint is a non-class (e.g., "Any"). In this
        # case, preserve this non-class as is.
        else:
            #FIXME: This can't be right. Isn't "self._origin" supposed to *ONLY*
            #be a class? Mypy complaints are probably justified here, frankly.
            self._origin = hint_embedded  # type: ignore[assignment]
