import logging
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union, cast

from graphql import (
    IDLE,
    REMOVE,
    DocumentNode,
    FieldNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    GraphQLError,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLType,
    InlineFragmentNode,
    NameNode,
    Node,
    OperationDefinitionNode,
    SelectionSetNode,
    TypeInfo,
    TypeInfoVisitor,
    Visitor,
    is_leaf_type,
    print_ast,
    visit,
)
from graphql.language.visitor import VisitorActionEnum
from graphql.pyutils import inspect

log = logging.getLogger(__name__)

# Equivalent to QUERY_DOCUMENT_KEYS but only for fields interesting to
# visit to parse the results
RESULT_DOCUMENT_KEYS: Dict[str, Tuple[str, ...]] = {
    "document": ("definitions",),
    "operation_definition": ("selection_set",),
    "selection_set": ("selections",),
    "field": ("selection_set",),
    "inline_fragment": ("selection_set",),
    "fragment_definition": ("selection_set",),
}


def _ignore_non_null(type_: GraphQLType):
    """Removes the GraphQLNonNull wrappings around types."""
    if isinstance(type_, GraphQLNonNull):
        return type_.of_type
    else:
        return type_


def _get_fragment(document, fragment_name):
    """Returns a fragment from the document."""
    for definition in document.definitions:
        if isinstance(definition, FragmentDefinitionNode):
            if definition.name.value == fragment_name:
                return definition

    raise GraphQLError(f'Fragment "{fragment_name}" not found in document!')


class ParseResultVisitor(Visitor):
    def __init__(
        self,
        schema: GraphQLSchema,
        document: DocumentNode,
        node: Node,
        result: Dict[str, Any],
        type_info: TypeInfo,
        visit_fragment: bool = False,
        inside_list_level: int = 0,
        operation_name: Optional[str] = None,
    ):
        """Recursive Implementation of a Visitor class to parse results
        correspondind to a schema and a document.

        Using a TypeInfo class to get the node types during traversal.

        If we reach a list in the results, then we parse each
        item of the list recursively, traversing the same nodes
        of the query again.

        During traversal, we keep the current position in the result
        in the result_stack field.

        Alongside the field type, we calculate the "result type"
        which is computed from the field type and the current
        recursive level we are for this field
        (:code:`inside_list_level` argument).
        """
        self.schema: GraphQLSchema = schema
        self.document: DocumentNode = document
        self.node: Node = node
        self.result: Dict[str, Any] = result
        self.type_info: TypeInfo = type_info
        self.visit_fragment: bool = visit_fragment
        self.inside_list_level = inside_list_level
        self.operation_name = operation_name

        self.result_stack: List[Any] = []

        super().__init__()

    @property
    def current_result(self):
        try:
            return self.result_stack[-1]
        except IndexError:
            return self.result

    @staticmethod
    def leave_document(node: DocumentNode, *_args: Any) -> Dict[str, Any]:
        results = cast(List[Dict[str, Any]], node.definitions)
        return {k: v for result in results for k, v in result.items()}

    def enter_operation_definition(
        self, node: OperationDefinitionNode, *_args: Any
    ) -> Union[None, VisitorActionEnum]:

        if self.operation_name is not None:
            if not hasattr(node.name, "value"):
                return REMOVE  # pragma: no cover

            node.name = cast(NameNode, node.name)

            if node.name.value != self.operation_name:
                log.debug(f"SKIPPING operation {node.name.value}")
                return REMOVE

        return IDLE

    @staticmethod
    def leave_operation_definition(
        node: OperationDefinitionNode, *_args: Any
    ) -> Dict[str, Any]:
        selections = cast(List[Dict[str, Any]], node.selection_set)
        return {k: v for s in selections for k, v in s.items()}

    @staticmethod
    def leave_selection_set(node: SelectionSetNode, *_args: Any) -> Dict[str, Any]:
        partial_results = cast(Dict[str, Any], node.selections)
        return partial_results

    @staticmethod
    def in_first_field(path):
        return path.count("selections") <= 1

    def get_current_result_type(self, path):
        field_type = self.type_info.get_type()

        list_level = self.inside_list_level

        result_type = _ignore_non_null(field_type)

        if self.in_first_field(path):

            while list_level > 0:
                assert isinstance(result_type, GraphQLList)
                result_type = _ignore_non_null(result_type.of_type)

                list_level -= 1

        return result_type

    def enter_field(
        self,
        node: FieldNode,
        key: str,
        parent: Node,
        path: List[Node],
        ancestors: List[Node],
    ) -> Union[None, VisitorActionEnum, Dict[str, Any]]:

        name = node.alias.value if node.alias else node.name.value

        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"Enter field {name}")
            log.debug(f"  path={path!r}")
            log.debug(f"  current_result={self.current_result!r}")

        if self.current_result is None:
            # Result was null for this field -> remove
            return REMOVE

        elif isinstance(self.current_result, Mapping):

            try:
                result_value = self.current_result[name]
            except KeyError:
                # Key not found in result.
                # Should never happen in theory with a correct GraphQL backend
                # Silently ignoring this field
                log.debug(f"  Key {name} not found in result --> REMOVE")
                return REMOVE

            log.debug(f"  result_value={result_value}")

            # We get the field_type from type_info
            field_type = self.type_info.get_type()

            # We calculate a virtual "result type" depending on our recursion level.
            result_type = self.get_current_result_type(path)

            # If the result for this field is a list, then we need
            # to recursively visit the same node multiple times for each
            # item in the list.
            if (
                not isinstance(result_value, Mapping)
                and isinstance(result_value, Iterable)
                and not isinstance(result_value, str)
                and not is_leaf_type(result_type)
            ):

                # Finding out the inner type of the list
                inner_type = _ignore_non_null(result_type.of_type)

                if log.isEnabledFor(logging.DEBUG):
                    log.debug("  List detected:")
                    log.debug(f"    field_type={inspect(field_type)}")
                    log.debug(f"    result_type={inspect(result_type)}")
                    log.debug(f"    inner_type={inspect(inner_type)}\n")

                visits: List[Dict[str, Any]] = []

                # Get parent type
                initial_type = self.type_info.get_parent_type()
                assert isinstance(
                    initial_type, (GraphQLObjectType, GraphQLInterfaceType)
                )

                # Get parent SelectionSet node
                selection_set_node = ancestors[-1]
                assert isinstance(selection_set_node, SelectionSetNode)

                # Keep only the current node in a new selection set node
                new_node = SelectionSetNode(selections=[node])

                for item in result_value:

                    new_result = {name: item}

                    if log.isEnabledFor(logging.DEBUG):
                        log.debug(f"      recursive new_result={new_result}")
                        log.debug(f"      recursive ast={print_ast(node)}")
                        log.debug(f"      recursive path={path!r}")
                        log.debug(f"      recursive initial_type={initial_type!r}\n")

                    if self.in_first_field(path):
                        inside_list_level = self.inside_list_level + 1
                    else:
                        inside_list_level = 1

                    inner_visit = parse_result_recursive(
                        self.schema,
                        self.document,
                        new_node,
                        new_result,
                        initial_type=initial_type,
                        inside_list_level=inside_list_level,
                    )
                    log.debug(f"      recursive result={inner_visit}\n")

                    inner_visit = cast(List[Dict[str, Any]], inner_visit)
                    visits.append(inner_visit[0][name])

                result_value = {name: visits}
                log.debug(f"    recursive visits final result = {result_value}\n")
                return result_value

            # If the result for this field is not a list, then add it
            # to the result stack so that it becomes the current_value
            # for the next inner fields
            self.result_stack.append(result_value)

            return IDLE

        raise GraphQLError(
            f"Invalid result for container of field {name}: {self.current_result!r}"
        )

    def leave_field(
        self,
        node: FieldNode,
        key: str,
        parent: Node,
        path: List[Node],
        ancestors: List[Node],
    ) -> Dict[str, Any]:

        name = cast(str, node.alias.value if node.alias else node.name.value)

        log.debug(f"Leave field {name}")

        if self.current_result is None:

            return_value = None

        elif node.selection_set is None:

            field_type = self.type_info.get_type()
            result_type = self.get_current_result_type(path)

            if log.isEnabledFor(logging.DEBUG):
                log.debug(f"  field type of {name} is {inspect(field_type)}")
                log.debug(f"  result type of {name} is {inspect(result_type)}")

            assert is_leaf_type(result_type)

            # Finally parsing a single scalar using the parse_value method
            return_value = result_type.parse_value(self.current_result)
        else:

            partial_results = cast(List[Dict[str, Any]], node.selection_set)

            return_value = {k: v for pr in partial_results for k, v in pr.items()}

        # Go up a level in the result stack
        self.result_stack.pop()

        log.debug(f"Leave field {name}: returning {return_value}")

        return {name: return_value}

    # Fragments

    def enter_fragment_definition(
        self, node: FragmentDefinitionNode, *_args: Any
    ) -> Union[None, VisitorActionEnum]:

        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"Enter fragment definition {node.name.value}.")
            log.debug(f"visit_fragment={self.visit_fragment!s}")

        if self.visit_fragment:
            return IDLE
        else:
            return REMOVE

    @staticmethod
    def leave_fragment_definition(
        node: FragmentDefinitionNode, *_args: Any
    ) -> Dict[str, Any]:

        selections = cast(List[Dict[str, Any]], node.selection_set)
        return {k: v for s in selections for k, v in s.items()}

    def leave_fragment_spread(
        self, node: FragmentSpreadNode, *_args: Any
    ) -> Dict[str, Any]:

        fragment_name = node.name.value

        log.debug(f"Start recursive fragment visit {fragment_name}")

        fragment_node = _get_fragment(self.document, fragment_name)

        fragment_result = parse_result_recursive(
            self.schema,
            self.document,
            fragment_node,
            self.current_result,
            visit_fragment=True,
        )

        log.debug(
            f"Result of recursive fragment visit {fragment_name}: {fragment_result}"
        )

        return cast(Dict[str, Any], fragment_result)

    @staticmethod
    def leave_inline_fragment(node: InlineFragmentNode, *_args: Any) -> Dict[str, Any]:

        selections = cast(List[Dict[str, Any]], node.selection_set)
        return {k: v for s in selections for k, v in s.items()}


def parse_result_recursive(
    schema: GraphQLSchema,
    document: DocumentNode,
    node: Node,
    result: Optional[Dict[str, Any]],
    initial_type: Optional[GraphQLType] = None,
    inside_list_level: int = 0,
    visit_fragment: bool = False,
    operation_name: Optional[str] = None,
) -> Any:

    if result is None:
        return None

    type_info = TypeInfo(schema, initial_type=initial_type)

    visited = visit(
        node,
        TypeInfoVisitor(
            type_info,
            ParseResultVisitor(
                schema,
                document,
                node,
                result,
                type_info=type_info,
                inside_list_level=inside_list_level,
                visit_fragment=visit_fragment,
                operation_name=operation_name,
            ),
        ),
        visitor_keys=RESULT_DOCUMENT_KEYS,
    )

    return visited


def parse_result(
    schema: GraphQLSchema,
    document: DocumentNode,
    result: Optional[Dict[str, Any]],
    operation_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Unserialize a result received from a GraphQL backend.

    :param schema: the GraphQL schema
    :param document: the document representing the query sent to the backend
    :param result: the serialized result received from the backend
    :param operation_name: the optional operation name

    :returns: a parsed result with scalars and enums parsed depending on
              their definition in the schema.

    Given a schema, a query and a serialized result,
    provide a new result with parsed values.

    If the result contains only built-in GraphQL scalars (String, Int, Float, ...)
    then the parsed result should be unchanged.

    If the result contains custom scalars or enums, then those values
    will be parsed with the parse_value method of the custom scalar or enum
    definition in the schema."""

    return parse_result_recursive(
        schema, document, document, result, operation_name=operation_name
    )
