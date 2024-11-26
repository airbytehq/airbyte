from itertools import chain
from typing import Collection

from ..language.ast import DocumentNode

__all__ = ["concat_ast"]


def concat_ast(asts: Collection[DocumentNode]) -> DocumentNode:
    """Concat ASTs.

    Provided a collection of ASTs, presumably each from different files, concatenate
    the ASTs together into batched AST, useful for validating many GraphQL source files
    which together represent one conceptual application.
    """
    return DocumentNode(
        definitions=list(chain.from_iterable(document.definitions for document in asts))
    )
