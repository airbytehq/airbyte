#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **abstract syntax tree (AST) testers** (i.e., low-level callables
testing various properties of various nodes in the currently visited AST).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw._clawtyping import NodeCallable
# from beartype.typing import (
#     List,
#     Union,
# )

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_node_callable_typed(node: NodeCallable) -> bool:
    '''
    :data:`True` only if the passed **callable node** (i.e., node signifying the
    definition of a pure-Python function or method) is **typed** (i.e.,
    annotated by a return type hint and/or one or more parameter type hints).

    Parameters
    ----------
    node : NodeCallable
        Callable node to be tested.

    Returns
    ----------
    bool
        :data:`True` only if this callable node is typed.
    '''

    # True only if the passed callable is untyped (i.e., annotated by *NO* type
    # hints), defaulting to whether that callable is annotated by *NO* return
    # type hint.
    #
    # Note that this boolean is intentionally defined in an unintuitive order so
    # as to increase the likelihood of efficiently defining this boolean in O(1)
    # time. Specifically:
    # * It is most efficient to test whether that callable is annotated by a
    #   return type hint.
    # * It is next-most efficient to test whether that callable accepts a
    #   variadic positional argument annotated by a type hint.
    # * It is least efficient to test whether that callable accepts a
    #   non-variadic argument annotated by a type hint, as doing so requires
    #   O(n) iteration for "n" the number of such arguments..
    #
    # Lastly, note that we could naively avoid doing this entirely and instead
    # unconditionally decorate *ALL* callables by @beartype -- in which case
    # @beartype would simply reduce to a noop for untyped callables annotated by
    # *NO* type hints. Technically, that works. Pragmatically, that would almost
    # certainly be slower than the current approach under the common assumption
    # that any developer annotating one or more non-variadic arguments of a
    # callable would also annotate the return of that callable -- in which case
    # this detection reduces to O(1) time complexity. Even where this is *NOT*
    # the case, however, this is still almost certainly slightly faster or of an
    # equivalent speed to the naive approach. Why? Because treating untyped
    # callables as typed would needlessly:
    # * Increase space complexity by polluting this AST with needlessly many
    #   "Name" child nodes performing untyped @beartype decorations.
    # * Increase time complexity by instantiating, initializing, and inserting
    #   (the three dread i's) those nodes.
    is_untyped = node.returns is None

    # If that callable is possibly untyped...
    if is_untyped:
        # Child arguments node of all arguments accepted by that callable.
        node_args = node.args

        # Variadic positional argument accepted by that callable if any.
        #
        # Note that @beartype currently prohibits type hints annotating
        # variadic keyword arguments, since there currently appears to be no
        # use case encouraging @beartype to support that.
        node_arg_varpos = node_args.vararg

        # If that callable accepts a variadic positional argument...
        if node_arg_varpos:
            # That callable is typed if that argument is annotated by
            # a type hint.
            is_untyped = node_arg_varpos.annotation is None
        # Else, that callable accepts *NO* variadic positional argument.

        # If that callable is still possibly untyped, fallback to deciding
        # whether that callable accepts one or more non-variadic arguments
        # annotated by type hints. Since doing is considerably more
        # computationally expensive, we do so *ONLY* as needed.
        #
        # Note that manual iteration is considerably more efficient than more
        # syntactically concise any() and all() generator expressions.
        if is_untyped:
            for node_arg_nonvar in node_args.args:
                if node_arg_nonvar.annotation is not None:
                    is_untyped = False
                    break
        # Else, that callable is now typed.
    # Else, that callable is now typed.

    # Return true only if that callable is *NOT* untyped (i.e., is typed).
    return not is_untyped
