#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **abstract syntax tree (AST) mungers** (i.e., low-level callables
modifying various properties of various nodes in the currently visited AST).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import AST
from beartype.typing import (
    Iterable,
    Union,
)

# ....................{ COPIERS                            }....................
#FIXME: Unit test us up, please.
def copy_node_metadata(
    node_src: AST,
    node_trg: Union[AST, Iterable[AST]],
) -> None:
    '''
    Copy all **source code metadata** (i.e., beginning and ending line and
    column numbers) from the passed source abstract syntax tree (AST) node onto
    the passed target AST node(s).

    This function is an efficient alternative to:

    * The extremely inefficient (albeit still useful)
      :func:`ast.fix_missing_locations` function.
    * The mildly inefficient (and mostly useless) :func:`ast.copy_location`
      function.

    The tradeoffs are as follows:

    * :func:`ast.fix_missing_locations` is ``O(n)`` time complexity for ``n``
      the number of AST nodes across the entire AST tree, but requires only a
      single trivial call and is thus considerably more "plug-and-play" than
      this function.
    * This function is ``O(1)`` time complexity irrespective of the size of the
      AST tree, but requires one still mostly trivial call for each synthetic
      AST node inserted into the AST tree by the
      :class:`BeartypeNodeTransformer` above.

    Caveats
    ----------
    **This function should only be passed nodes that support code metadata.**
    Although *most* nodes do, some nodes do not. Why? Because they are *not*
    actually nodes; they simply masquerade as nodes in documentation for the
    standard :mod:`ast` module, which inexplicably makes *no* distinction
    between the two. These pseudo-nodes include:

    * :class:`ast.Del` nodes.
    * :class:`ast.Load` nodes.
    * :class:`ast.Store` nodes.

    Indeed, this observation implies that these pseudo-nodes may be globalized
    as singletons for efficient reuse throughout our AST generation algorithms.

    Lastly, note that nodes may be differentiated from pseudo-nodes by passing
    the call to the :func:`ast.dump` function in the code snippet presented in
    the docstring for the :class:`BeartypeNodeTransformer` class an additional
    ``include_attributes=True`` parameter: e.g.,

    .. code-block:: python

       print(ast.dump(ast.parse(CODE), indent=4, include_attributes=True))

    Actual nodes have code metadata printed for them; pseudo-nodes do *not*.

    Parameters
    ----------
    node_src : AST
        Source AST node to copy source code metadata from.
    node_trg : Union[AST, Iterable[AST]]
        Either:

        * A single target AST node to copy source code metadata onto.
        * An iterable of zero or more target AST nodes to copy source code
          metadata onto.

    See Also
    ----------
    :func:`ast.copy_location`
        Less efficient analogue of this function running in ``O(k)`` time
        complexity for ``k`` the number of types of source code metadata.
        Typically, ``k == 4``.
    '''
    assert isinstance(node_src, AST), f'{repr(node_src)} not AST node.'

    # If passed only a single target node, wrap this node in a 1-tuple
    # containing only this node for simplicity.
    if isinstance(node_trg, AST):
        node_trg = (node_trg,)
    # In either case, "node_trg" is now an iterable of target nodes.

    # For each passed target node...
    for node_trg_cur in node_trg:
        assert isinstance(node_trg_cur, AST), (
            f'{repr(node_trg_cur)} not AST node.')

        # Copy all source code metadata from this source to target node.
        node_trg_cur.lineno         = node_src.lineno
        node_trg_cur.col_offset     = node_src.col_offset
        node_trg_cur.end_lineno     = node_src.end_lineno  # type: ignore[attr-defined]
        node_trg_cur.end_col_offset = node_src.end_col_offset  # type: ignore[attr-defined]
