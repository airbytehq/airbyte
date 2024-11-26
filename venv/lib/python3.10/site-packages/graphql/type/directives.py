from typing import Any, Collection, Dict, Optional, Tuple, cast

from ..language import ast, DirectiveLocation
from ..pyutils import inspect, is_description
from .assert_name import assert_name
from .definition import GraphQLArgument, GraphQLInputType, GraphQLNonNull, is_input_type
from .scalars import GraphQLBoolean, GraphQLString

try:
    from typing import TypedDict
except ImportError:  # Python < 3.8
    from typing_extensions import TypedDict

__all__ = [
    "is_directive",
    "assert_directive",
    "is_specified_directive",
    "specified_directives",
    "GraphQLDirective",
    "GraphQLDirectiveKwargs",
    "GraphQLIncludeDirective",
    "GraphQLSkipDirective",
    "GraphQLDeprecatedDirective",
    "GraphQLSpecifiedByDirective",
    "DirectiveLocation",
    "DEFAULT_DEPRECATION_REASON",
]


class GraphQLDirectiveKwargs(TypedDict, total=False):
    name: str
    locations: Tuple[DirectiveLocation, ...]
    args: Dict[str, GraphQLArgument]
    is_repeatable: bool
    description: Optional[str]
    extensions: Dict[str, Any]
    ast_node: Optional[ast.DirectiveDefinitionNode]


class GraphQLDirective:
    """GraphQL Directive

    Directives are used by the GraphQL runtime as a way of modifying execution behavior.
    Type system creators will usually not create these directly.
    """

    name: str
    locations: Tuple[DirectiveLocation, ...]
    is_repeatable: bool
    args: Dict[str, GraphQLArgument]
    description: Optional[str]
    extensions: Dict[str, Any]
    ast_node: Optional[ast.DirectiveDefinitionNode]

    def __init__(
        self,
        name: str,
        locations: Collection[DirectiveLocation],
        args: Optional[Dict[str, GraphQLArgument]] = None,
        is_repeatable: bool = False,
        description: Optional[str] = None,
        extensions: Optional[Dict[str, Any]] = None,
        ast_node: Optional[ast.DirectiveDefinitionNode] = None,
    ) -> None:
        assert_name(name)
        try:
            locations = tuple(
                value
                if isinstance(value, DirectiveLocation)
                else DirectiveLocation[cast(str, value)]
                for value in locations
            )
        except (KeyError, TypeError):
            raise TypeError(
                f"{name} locations must be specified"
                " as a collection of DirectiveLocation enum values."
            )
        if args is None:
            args = {}
        elif not isinstance(args, dict) or not all(
            isinstance(key, str) for key in args
        ):
            raise TypeError(f"{name} args must be a dict with argument names as keys.")
        elif not all(
            isinstance(value, GraphQLArgument) or is_input_type(value)
            for value in args.values()
        ):
            raise TypeError(
                f"{name} args must be GraphQLArgument or input type objects."
            )
        else:
            args = {
                assert_name(name): value
                if isinstance(value, GraphQLArgument)
                else GraphQLArgument(cast(GraphQLInputType, value))
                for name, value in args.items()
            }
        if not isinstance(is_repeatable, bool):
            raise TypeError(f"{name} is_repeatable flag must be True or False.")
        if ast_node and not isinstance(ast_node, ast.DirectiveDefinitionNode):
            raise TypeError(f"{name} AST node must be a DirectiveDefinitionNode.")
        if description is not None and not is_description(description):
            raise TypeError(f"{name} description must be a string.")
        if extensions is None:
            extensions = {}
        elif not isinstance(extensions, dict) or not all(
            isinstance(key, str) for key in extensions
        ):
            raise TypeError(f"{name} extensions must be a dictionary with string keys.")
        self.name = name
        self.locations = locations
        self.args = args
        self.is_repeatable = is_repeatable
        self.description = description
        self.extensions = extensions
        self.ast_node = ast_node

    def __str__(self) -> str:
        return f"@{self.name}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self})>"

    def __eq__(self, other: Any) -> bool:
        return self is other or (
            isinstance(other, GraphQLDirective)
            and self.name == other.name
            and self.locations == other.locations
            and self.args == other.args
            and self.is_repeatable == other.is_repeatable
            and self.description == other.description
            and self.extensions == other.extensions
        )

    def to_kwargs(self) -> GraphQLDirectiveKwargs:
        return GraphQLDirectiveKwargs(
            name=self.name,
            locations=self.locations,
            args=self.args,
            is_repeatable=self.is_repeatable,
            description=self.description,
            extensions=self.extensions,
            ast_node=self.ast_node,
        )

    def __copy__(self) -> "GraphQLDirective":  # pragma: no cover
        return self.__class__(**self.to_kwargs())


def is_directive(directive: Any) -> bool:
    """Test if the given value is a GraphQL directive."""
    return isinstance(directive, GraphQLDirective)


def assert_directive(directive: Any) -> GraphQLDirective:
    if not is_directive(directive):
        raise TypeError(f"Expected {inspect(directive)} to be a GraphQL directive.")
    return cast(GraphQLDirective, directive)


# Used to conditionally include fields or fragments.
GraphQLIncludeDirective = GraphQLDirective(
    name="include",
    locations=[
        DirectiveLocation.FIELD,
        DirectiveLocation.FRAGMENT_SPREAD,
        DirectiveLocation.INLINE_FRAGMENT,
    ],
    args={
        "if": GraphQLArgument(
            GraphQLNonNull(GraphQLBoolean), description="Included when true."
        )
    },
    description="Directs the executor to include this field or fragment"
    " only when the `if` argument is true.",
)


# Used to conditionally skip (exclude) fields or fragments:
GraphQLSkipDirective = GraphQLDirective(
    name="skip",
    locations=[
        DirectiveLocation.FIELD,
        DirectiveLocation.FRAGMENT_SPREAD,
        DirectiveLocation.INLINE_FRAGMENT,
    ],
    args={
        "if": GraphQLArgument(
            GraphQLNonNull(GraphQLBoolean), description="Skipped when true."
        )
    },
    description="Directs the executor to skip this field or fragment"
    " when the `if` argument is true.",
)


# Constant string used for default reason for a deprecation:
DEFAULT_DEPRECATION_REASON = "No longer supported"

# Used to declare element of a GraphQL schema as deprecated:
GraphQLDeprecatedDirective = GraphQLDirective(
    name="deprecated",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.ARGUMENT_DEFINITION,
        DirectiveLocation.INPUT_FIELD_DEFINITION,
        DirectiveLocation.ENUM_VALUE,
    ],
    args={
        "reason": GraphQLArgument(
            GraphQLString,
            description="Explains why this element was deprecated,"
            " usually also including a suggestion for how to access"
            " supported similar data."
            " Formatted using the Markdown syntax, as specified by"
            " [CommonMark](https://commonmark.org/).",
            default_value=DEFAULT_DEPRECATION_REASON,
        )
    },
    description="Marks an element of a GraphQL schema as no longer supported.",
)

# Used to provide a URL for specifying the behaviour of custom scalar definitions:
GraphQLSpecifiedByDirective = GraphQLDirective(
    name="specifiedBy",
    locations=[DirectiveLocation.SCALAR],
    args={
        "url": GraphQLArgument(
            GraphQLNonNull(GraphQLString),
            description="The URL that specifies the behaviour of this scalar.",
        )
    },
    description="Exposes a URL that specifies the behaviour of this scalar.",
)


specified_directives: Tuple[GraphQLDirective, ...] = (
    GraphQLIncludeDirective,
    GraphQLSkipDirective,
    GraphQLDeprecatedDirective,
    GraphQLSpecifiedByDirective,
)
"""A tuple with all directives from the GraphQL specification"""


def is_specified_directive(directive: GraphQLDirective) -> bool:
    """Check whether the given directive is one of the specified directives."""
    return any(
        specified_directive.name == directive.name
        for specified_directive in specified_directives
    )
