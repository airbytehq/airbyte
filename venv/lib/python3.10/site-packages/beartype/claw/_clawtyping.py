#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hook type hints** (i.e., PEP-compliant hints annotating
callables and classes declared throughout the :mod:`beartype.claw` subpackage,
either for compliance with :pep:`561`-compliant static type checkers like
:mod:`mypy` or simply for documentation purposes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    AsyncFunctionDef,
    ClassDef,
    FunctionDef,
)
from beartype.typing import (
    List,
    Optional,
    TypeVar,
    Union,
)

# ....................{ HINTS ~ node                       }....................
NodeCallable = Union[FunctionDef, AsyncFunctionDef]
'''
PEP-compliant type hint matching a **callable node** (i.e., abstract syntax tree
(AST) node encapsulating the definition of a pure-Python function or method that
is either synchronous or asynchronous).
'''


NodeDecoratable = Union[NodeCallable, ClassDef]
'''
PEP-compliant type hint matching a **decoratable node** (i.e., abstract syntax
tree (AST) node encapsulating the definition of a pure-Python object supporting
decoration by one or more ``"@"``-prefixed decorations, including both
pure-Python classes *and* callables).
'''


NodeT = TypeVar('NodeT', bound=AST)
'''
**Node type variable** (i.e., type variable constrained to match *only* abstract
syntax tree (AST) nodes).
'''

# ....................{ HINTS ~ visit                      }....................
NodeVisitResult = Optional[Union[AST, List[AST]]]
'''
PEP-compliant type hint matching a **node visitation result** (i.e., object
returned by any visitor method of an :class:`ast.NodeVisitor` subclass).

Specifically, this hint matches either:

* A single node, in which case a visitor method has effectively preserved the
  currently visited node passed to that method in the AST.
* A list of zero or more nodes, in which case a visitor method has replaced the
  currently visited node passed to that method with those nodes in the AST.
* :data:`None`, in which case a visitor method has effectively destroyed the
  currently visited node passed to that method from the AST.
'''
