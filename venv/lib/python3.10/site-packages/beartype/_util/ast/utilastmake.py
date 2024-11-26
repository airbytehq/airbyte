#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **abstract syntax tree (AST) factories** (i.e., low-level callables
creating and returning various types of nodes, typically for inclusion in the
currently visited AST).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    ImportFrom,
    alias,
)
from beartype._util.ast.utilastmunge import copy_node_metadata

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_node_importfrom(
    module_name: str,
    source_attr_name: str,
    target_attr_name: str,
    node_sibling: AST,
) -> ImportFrom:
    '''
    Create and return a new **import-from abstract syntax tree (AST) node**
    (i.e., node encapsulating an import statement of the alias-style format
    ``from {module_name} import {attr_name}``) importing the attribute with the
    passed source name from the module with the passed name into the currently
    visited module as a new attribute with the passed target name.

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to import this attribute from.
    source_attr_name : str
        Unqualified basename of the attribute to import from this module.
    target_attr_name : str
        Unqualified basename of the same attribute to import into the currently
        visited module.
    node_sibling : AST
        Sibling node to copy source code metadata from.

    Returns
    ----------
    ImportFrom
        Import-from node importing this attribute from this module.
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'
    assert isinstance(source_attr_name, str), (
        f'{repr(source_attr_name)} not string.')
    assert isinstance(target_attr_name, str), (
        f'{repr(target_attr_name)} not string.')

    # Node encapsulating the name of the attribute to import from this module.
    node_importfrom_name = alias(name=source_attr_name, asname=target_attr_name)

    # Node encapsulating the name of the module to import this attribute from.
    node_importfrom = ImportFrom(
        module=module_name, names=[node_importfrom_name])

    # Copy all source code metadata (e.g., line numbers) from this sibling node
    # onto these new nodes.
    copy_node_metadata(
        node_src=node_sibling, node_trg=(node_importfrom, node_importfrom_name))

    # Return this import-from node.
    return node_importfrom
