#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) annotated type hint
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`593`-compliant :attr:`typing.Annotated` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsuper import TypeHint
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.utilpep593 import (
    get_hint_pep593_metadata,
    get_hint_pep593_metahint,
)
from contextlib import suppress

# ....................{ SUBCLASSES                         }....................
class AnnotatedTypeHint(TypeHint):
    '''
    **Annotated type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`593`-compliant :attr:`typing.Annotated` type hint).

    Attributes (Private)
    --------
    _metadata : tuple[object]
        **Metadata** (i.e., tuple of zero or more arbitrary low-level
        caller-defined objects annotating this :attr:`typing.Annotated` type
        hint, equivalent to all remaining arguments subscripting this hint).
    _metahint_wrapper : TypeHint
        **Metahint wrapper** (i.e., :class:`TypeHint` instance wrapping the
        child type hint annotated by this parent :attr:`typing.Annotated` type
        hint, equivalent to the first argument subscripting this hint).
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint: object) -> None:

        # Initialize our superclass.
        super().__init__(hint)

        # Tuple of the zero or more arbitrary caller-defined arguments following
        # the first argument subscripting this hint.
        self._metadata = get_hint_pep593_metadata(hint)

        # Wrapper wrapping the first argument subscripting this hint.
        self._metahint_wrapper = TypeHint(get_hint_pep593_metahint(hint))

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _is_args_ignorable(self) -> bool:
        # since Annotated[] must be used with at least two arguments, we are
        # never just the origin of the metahint
        return False

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_equal(self, other: TypeHint) -> bool:

        return (
            isinstance(other, AnnotatedTypeHint)
            and self._metahint_wrapper == other._metahint_wrapper
            and self._metadata == other._metadata
        )


    def _is_subhint_branch(self, branch: TypeHint) -> bool:

        # If the other type is not annotated, we ignore annotations on this
        # one and just check that the metahint is a subhint of the other.
        # e.g. Annotated[t.List[int], 'meta'] <= List[int]
        if not isinstance(branch, AnnotatedTypeHint):
            return self._metahint_wrapper.is_subhint(branch)

        # Else, that hint is a "typing.Annotated[...]" type hint. If either...
        if (
            # The child type hint annotated by this parent hint does not subhint
            # the child type hint annotated by that parent hint *OR*...
            self._metahint_wrapper > branch._metahint_wrapper or
            # These hints are annotated by a differing number of objects...
            len(self._metadata) != len(branch._metadata)
        ):
            # This hint *CANNOT* be a subhint of that hint. Return false.
            return False

        # Attempt to...
        #
        # Note that the following iteration performs equality comparisons on
        # arbitrary caller-defined objects. Since these comparisons may raise
        # arbitrary caller-defined exceptions, we silently squelch any such
        # exceptions that arise by returning false below instead.
        with suppress(Exception):
            # Return true only if these hints are annotated by equivalent
            # objects. We avoid testing for a subhint relation here (e.g., with
            # the "<=" operator), as arbitrary caller-defined objects are *MUCH*
            # more likely to define a relevant equality comparison than a
            # relevant less-than-or-equal-to comparison.
            return self._metadata == branch._metadata

        # Else, one or more objects annotating these hints are incomparable. So,
        # this hint *CANNOT* be a subhint of that hint. Return false.
        return False  # pragma: no cover
