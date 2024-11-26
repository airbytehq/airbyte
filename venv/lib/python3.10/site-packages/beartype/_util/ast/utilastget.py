#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **abstract syntax tree (AST) getters** (i.e., low-level callables
acquiring various properties of various nodes in the currently visited AST).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    dump as ast_dump,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def get_node_repr_indented(node: AST) -> str:
    '''
    Human-readable string pretty-printing the contents of the passed abstract
    syntax tree (AST), complete with readable indentation.

    Parameters
    ----------
    node : AST
        AST to be pretty-printed.

    Returns
    ----------
    str
        Human-readable string pretty-printing the contents of this AST.
    '''
    assert isinstance(node, AST), f'{repr(node)} not AST.'

    # Return either...
    return (
        # If the active Python interpreter targets Python >= 3.9, the
        # pretty-printed contents of this AST. Sadly, the "indent=4" parameter
        # pretty-printing this AST was first introduced by Python 3.9.
        ast_dump(node, indent=4)  # type: ignore[call-arg]
        if IS_PYTHON_AT_LEAST_3_9 else
        # Else, the active Python interpreter targets Python < 3.9. In this
        # case, the non-pretty-printed contents of this AST as a single line.
        ast_dump(node)
    )
