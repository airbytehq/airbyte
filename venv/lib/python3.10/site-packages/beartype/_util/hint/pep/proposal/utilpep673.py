#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`673`-compliant **self type hint** (i.e., the
:obj:`typing.Self` type hint singleton) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep673Exception
from beartype._cave._cavemap import NoneTypeOr
from beartype._data.hint.datahinttyping import TypeStack

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, please.
def reduce_hint_pep673(
    hint: object,
    cls_stack: TypeStack,
    exception_prefix: str,
    *args, **kwargs
) -> type:
    '''
    Reduce the passed :pep:`673`-compliant **self type hint** (i.e.,
    the :obj:`typing.Self` type hint singleton) to the **currently decorated
    class** (i.e., the most deeply nested class on the passed type stack,
    signifying the class currently being decorated by :func:`beartype.beartype`)
    if any *or* raise an exception otherwise (i.e., if *no* class is currently
    being decorated).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : object
        Self type hint to be reduced.
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either tuple of zero or more arbitrary types *or*
        :data:`None`). Defaults to :data:`None`. See also the
        :func:`.beartype_object` decorator for further commentary.
    exception_prefix : str, optional
        Human-readable substring prefixing exception messages raised by this
        function.

    All remaining passed arguments are silently ignored.

    Returns
    ----------
    type
        Most deeply nested class on this type stack.

    Raises
    ----------
    BeartypeDecorHintPep673Exception
        If either:

        * ``cls_stack`` is :data:`None`.
        * ``cls_stack`` is non-:data:`None` but empty.
    '''
    assert isinstance(cls_stack, NoneTypeOr[tuple]), (
        f'{repr(cls_stack)} neither tuple nor "None".')

    # If either no type stack *OR* an empty type stack was passed, *NO* class is
    # currently being decorated by @beartype. It follows that either:
    # * @beartype is currently decorating a function or method directly.
    # * A statement-level runtime type-checker (e.g.,
    #   beartype.door.is_bearable()) is currently being called.
    #
    # However, the "typing.Self" type hint *CANNOT* be reliably resolved outside
    # of a class context. Although @beartype could attempt to heuristically
    # differentiate functions from methods via the first passed argument, Python
    # itself does *NOT* require that argument of a method to be named "self";
    # such a heuristic would catastrophically fail in common edge cases. Our
    # only recourse is to raise an exception encouraging the user to refactor
    # their code to decorate classes rather than methods.
    if not cls_stack:
        # We didn't make crazy. We only document it.
        raise BeartypeDecorHintPep673Exception(
            f'{exception_prefix}PEP 673 type hint "{repr(hint)}" '
            f'invalid outside @beartype-decorated class. '
            f'PEP 673 type hints are valid only inside classes decorated by '
            f'@beartype. If this hint annotates a method decorated by '
            f'@beartype, instead decorate the class declaring this method by '
            f'@beartype: e.g.,\n'
            f'\n'
            f'    # Instead of decorating methods by @beartype like this...\n'
            f'    class BadClassIsBad(object):\n'
            f'        @beartype\n'
            f'        def awful_method_is_awful(self: Self) -> Self:\n'
            f'            return self\n'
            f'\n'
            f'    # ...decorate classes by @beartype instead - like this!\n'
            f'    @beartype\n'
            f'    class GoodClassIsGood(object):\n'
            f'        def wonderful_method_is_wonderful(self: Self) -> Self:\n'
            f'            return self\n'
            f'\n'
            f"This has been a message of the Bearhugger Broadcasting Service."
        )
    # Else, a non-empty type stack was passed.

    # Reduce this hint to the currently decorated class (i.e., the most deeply
    # nested class on this type stack, signifying the class currently being
    # decorated by @beartype.beartype).
    return cls_stack[-1]
