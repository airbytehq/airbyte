from typing import TYPE_CHECKING

from .graphql_error import GraphQLError

if TYPE_CHECKING:
    from ..language.source import Source  # noqa: F401

__all__ = ["GraphQLSyntaxError"]


class GraphQLSyntaxError(GraphQLError):
    """A GraphQLError representing a syntax error."""

    def __init__(self, source: "Source", position: int, description: str) -> None:
        super().__init__(
            f"Syntax Error: {description}", source=source, positions=[position]
        )
        self.description = description
