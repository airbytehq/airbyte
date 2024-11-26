from sys import exc_info
from typing import Any, Collection, Dict, List, Optional, Union, TYPE_CHECKING

try:
    from typing import TypedDict
except ImportError:  # Python < 3.8
    from typing_extensions import TypedDict

if TYPE_CHECKING:
    from ..language.ast import Node  # noqa: F401
    from ..language.location import (
        SourceLocation,
        FormattedSourceLocation,
    )  # noqa: F401
    from ..language.source import Source  # noqa: F401

__all__ = ["GraphQLError", "GraphQLErrorExtensions", "GraphQLFormattedError"]


# Custom extensions
GraphQLErrorExtensions = Dict[str, Any]
# Use a unique identifier name for your extension, for example the name of
# your library or project. Do not use a shortened identifier as this increases
# the risk of conflicts. We recommend you add at most one extension key,
# a dictionary which can contain all the values you need.


class GraphQLFormattedError(TypedDict, total=False):
    """Formatted GraphQL error"""

    # A short, human-readable summary of the problem that **SHOULD NOT** change
    # from occurrence to occurrence of the problem, except for purposes of localization.
    message: str
    # If an error can be associated to a particular point in the requested
    # GraphQL document, it should contain a list of locations.
    locations: List["FormattedSourceLocation"]
    # If an error can be associated to a particular field in the GraphQL result,
    # it _must_ contain an entry with the key `path` that details the path of
    # the response field which experienced the error. This allows clients to
    # identify whether a null result is intentional or caused by a runtime error.
    path: List[Union[str, int]]
    # Reserved for implementors to extend the protocol however they see fit,
    # and hence there are no additional restrictions on its contents.
    extensions: GraphQLErrorExtensions


class GraphQLError(Exception):
    """GraphQL Error

    A GraphQLError describes an Error found during the parse, validate, or execute
    phases of performing a GraphQL operation. In addition to a message, it also includes
    information about the locations in a GraphQL document and/or execution result that
    correspond to the Error.
    """

    message: str
    """A message describing the Error for debugging purposes"""

    locations: Optional[List["SourceLocation"]]
    """Source locations

    A list of (line, column) locations within the source GraphQL document which
    correspond to this error.

    Errors during validation often contain multiple locations, for example to point out
    two things with the same name. Errors during execution include a single location,
    the field which produced the error.
    """

    path: Optional[List[Union[str, int]]]
    """

    A list of field names and array indexes describing the JSON-path into the execution
    response which corresponds to this error.

    Only included for errors during execution.
    """

    nodes: Optional[List["Node"]]
    """A list of GraphQL AST Nodes corresponding to this error"""

    source: Optional["Source"]
    """The source GraphQL document for the first location of this error

    Note that if this Error represents more than one node, the source may not represent
    nodes after the first node.
    """

    positions: Optional[Collection[int]]
    """Error positions

    A list of character offsets within the source GraphQL document which correspond
    to this error.
    """

    original_error: Optional[Exception]
    """The original error thrown from a field resolver during execution"""

    extensions: Optional[GraphQLErrorExtensions]
    """Extension fields to add to the formatted error"""

    __slots__ = (
        "message",
        "nodes",
        "source",
        "positions",
        "locations",
        "path",
        "original_error",
        "extensions",
    )

    __hash__ = Exception.__hash__

    def __init__(
        self,
        message: str,
        nodes: Union[Collection["Node"], "Node", None] = None,
        source: Optional["Source"] = None,
        positions: Optional[Collection[int]] = None,
        path: Optional[Collection[Union[str, int]]] = None,
        original_error: Optional[Exception] = None,
        extensions: Optional[GraphQLErrorExtensions] = None,
    ) -> None:
        super().__init__(message)
        self.message = message

        if path and not isinstance(path, list):
            path = list(path)
        self.path = path or None  # type: ignore
        self.original_error = original_error

        # Compute list of blame nodes.
        if nodes and not isinstance(nodes, list):
            nodes = [nodes]  # type: ignore
        self.nodes = nodes or None  # type: ignore
        node_locations = (
            [node.loc for node in nodes if node.loc] if nodes else []  # type: ignore
        )

        # Compute locations in the source for the given nodes/positions.
        self.source = source
        if not source and node_locations:
            loc = node_locations[0]
            if loc.source:  # pragma: no cover else
                self.source = loc.source
        if not positions and node_locations:
            positions = [loc.start for loc in node_locations]
        self.positions = positions or None
        if positions and source:
            locations: Optional[List["SourceLocation"]] = [
                source.get_location(pos) for pos in positions
            ]
        else:
            locations = [loc.source.get_location(loc.start) for loc in node_locations]
        self.locations = locations or None

        if original_error:
            self.__traceback__ = original_error.__traceback__
            if original_error.__cause__:
                self.__cause__ = original_error.__cause__
            elif original_error.__context__:
                self.__context__ = original_error.__context__
            if extensions is None:
                original_extensions = getattr(original_error, "extensions", None)
                if isinstance(original_extensions, dict):
                    extensions = original_extensions
        self.extensions = extensions or {}
        if not self.__traceback__:
            self.__traceback__ = exc_info()[2]

    def __str__(self) -> str:
        # Lazy import to avoid a cyclic dependency between error and language
        from ..language.print_location import print_location, print_source_location

        output = [self.message]

        if self.nodes:
            for node in self.nodes:
                if node.loc:
                    output.append(print_location(node.loc))
        elif self.source and self.locations:
            source = self.source
            for location in self.locations:
                output.append(print_source_location(source, location))

        return "\n\n".join(output)

    def __repr__(self) -> str:
        args = [repr(self.message)]
        if self.locations:
            args.append(f"locations={self.locations!r}")
        if self.path:
            args.append(f"path={self.path!r}")
        if self.extensions:
            args.append(f"extensions={self.extensions!r}")
        return f"{self.__class__.__name__}({', '.join(args)})"

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, GraphQLError)
            and self.__class__ == other.__class__
            and all(
                getattr(self, slot) == getattr(other, slot)
                for slot in self.__slots__
                if slot != "original_error"
            )
        ) or (
            isinstance(other, dict)
            and "message" in other
            and all(
                slot in self.__slots__ and getattr(self, slot) == other.get(slot)
                for slot in other
                if slot != "original_error"
            )
        )

    def __ne__(self, other: Any) -> bool:
        return not self == other

    @property
    def formatted(self) -> GraphQLFormattedError:
        """Get error formatted according to the specification.

        Given a GraphQLError, format it according to the rules described by the
        "Response Format, Errors" section of the GraphQL Specification.
        """
        formatted: GraphQLFormattedError = {
            "message": self.message or "An unknown error occurred.",
        }
        if self.locations is not None:
            formatted["locations"] = [location.formatted for location in self.locations]
        if self.path is not None:
            formatted["path"] = self.path
        if self.extensions:
            formatted["extensions"] = self.extensions
        return formatted


def print_error(error: GraphQLError) -> str:
    """Print a GraphQLError to a string.

    Represents useful location information about the error's position in the source.

    .. deprecated:: 3.2
       Please use ``str(error)`` instead. Will be removed in v3.3.
    """
    if not isinstance(error, GraphQLError):
        raise TypeError("Expected a GraphQLError.")
    return str(error)


def format_error(error: GraphQLError) -> GraphQLFormattedError:
    """Format a GraphQL error.

    Given a GraphQLError, format it according to the rules described by the "Response
    Format, Errors" section of the GraphQL Specification.

    .. deprecated:: 3.2
       Please use ``error.formatted`` instead. Will be removed in v3.3.
    """
    if not isinstance(error, GraphQLError):
        raise TypeError("Expected a GraphQLError.")
    return error.formatted
