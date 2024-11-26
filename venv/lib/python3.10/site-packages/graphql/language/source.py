from typing import Any

from .location import SourceLocation

__all__ = ["Source", "is_source"]


class Source:
    """A representation of source input to GraphQL."""

    # allow custom attributes and weak references (not used internally)
    __slots__ = "__weakref__", "__dict__", "body", "name", "location_offset"

    def __init__(
        self,
        body: str,
        name: str = "GraphQL request",
        location_offset: SourceLocation = SourceLocation(1, 1),
    ) -> None:
        """Initialize source input.

        The ``name`` and ``location_offset`` parameters are optional, but they are
        useful for clients who store GraphQL documents in source files. For example,
        if the GraphQL input starts at line 40 in a file named ``Foo.graphql``, it might
        be useful for ``name`` to be ``"Foo.graphql"`` and location to be ``(40, 0)``.

        The ``line`` and ``column`` attributes in ``location_offset`` are 1-indexed.
        """
        self.body = body
        self.name = name
        if not isinstance(location_offset, SourceLocation):
            location_offset = SourceLocation._make(location_offset)
        if location_offset.line <= 0:
            raise ValueError(
                "line in location_offset is 1-indexed and must be positive."
            )
        if location_offset.column <= 0:
            raise ValueError(
                "column in location_offset is 1-indexed and must be positive."
            )
        self.location_offset = location_offset

    def get_location(self, position: int) -> SourceLocation:
        lines = self.body[:position].splitlines()
        if lines:
            line = len(lines)
            column = len(lines[-1]) + 1
        else:
            line = 1
            column = 1
        return SourceLocation(line, column)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"

    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, Source) and other.body == self.body) or (
            isinstance(other, str) and other == self.body
        )

    def __ne__(self, other: Any) -> bool:
        return not self == other


def is_source(source: Any) -> bool:
    """Test if the given value is a Source object.

    For internal use only.
    """
    return isinstance(source, Source)
