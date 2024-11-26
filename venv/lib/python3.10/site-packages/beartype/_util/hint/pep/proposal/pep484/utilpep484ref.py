#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **forward reference type hint utilities**
(i.e., callables specifically applicable to :pep:`484`-compliant forward
reference type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.typing import (
    Any,
    ForwardRef,
)
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ HINTS                              }....................
#FIXME: Refactor this now-useless global away, please. Specifically:
#* Globally replace all references to this global with references to
#  "beartype.typing.ForwardRef" instead.
#* Excise this global.
HINT_PEP484_FORWARDREF_TYPE = ForwardRef
'''
:pep:`484`-compliant **forward reference type** (i.e., class of all forward
reference objects implicitly created by all :mod:`typing` type hint factories
when subscripted by a string).
'''

# ....................{ TESTERS                            }....................
def is_hint_pep484_forwardref(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a :pep:`484`-compliant **forward
    reference type hint** (i.e., instance of the :class:`typing.ForwardRef`
    class implicitly replacing all string arguments subscripting :mod:`typing`
    objects).

    The :mod:`typing` module implicitly replaces all strings subscripting
    :mod:`typing` objects (e.g., the ``MuhType`` in ``List['MuhType']``) with
    :class:`typing.ForwardRef` instances containing those strings as instance
    variables, for nebulous reasons that make little justifiable sense.

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a :pep:`484`-compliant forward
        reference type hint.
    '''

    # Return true only if this hint is an instance of the PEP 484-compliant
    # forward reference superclass.
    return isinstance(hint, HINT_PEP484_FORWARDREF_TYPE)

# ....................{ GETTERS                            }....................
@callable_cached
def get_hint_pep484_forwardref_type_basename(hint: Any) -> str:
    '''
    **Unqualified classname** (i.e., name of a class *not* containing a ``.``
    delimiter and thus relative to the fully-qualified name of the lexical
    scope declaring that class) referred to by the passed :pep:`484`-compliant
    **forward reference type hint** (i.e., instance of the
    :class:`typing.ForwardRef` class implicitly replacing all string arguments
    subscripting :mod:`typing` objects).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    str
        Unqualified classname referred to by this :pep:`484`-compliant forward
        reference type hint.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this object is *not* a :pep:`484`-compliant forward reference.

    See Also
    ----------
    :func:`is_hint_pep484_forwardref`
        Further commentary.
    '''

    # If this object is *NOT* a PEP 484-compliant forward reference, raise an
    # exception.
    if not is_hint_pep484_forwardref(hint):
        raise BeartypeDecorHintForwardRefException(
            f'Type hint {repr(hint)} not forward reference.')
    # Else, this object is a PEP 484-compliant forward reference.

    # Return the unqualified classname referred to by this reference. Note
    # that:
    # * This requires violating privacy encapsulation by accessing a dunder
    #   instance variable unique to the "typing.ForwardRef" class.
    # * This object defines a significant number of other "__forward_"-prefixed
    #   dunder instance variables, which exist *ONLY* to enable the blatantly
    #   useless typing.get_type_hints() function to avoid repeatedly (and thus
    #   inefficiently) reevaluating the same forward reference. *sigh*
    return hint.__forward_arg__
