from typing import Any, Callable, Dict, List, NamedTuple, Optional, Set, Union, cast

from ..error import GraphQLError
from ..language import (
    DocumentNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    OperationDefinitionNode,
    SelectionSetNode,
    VariableNode,
    Visitor,
    VisitorAction,
    visit,
)
from ..type import (
    GraphQLArgument,
    GraphQLCompositeType,
    GraphQLDirective,
    GraphQLEnumValue,
    GraphQLField,
    GraphQLInputType,
    GraphQLOutputType,
    GraphQLSchema,
)
from ..utilities import TypeInfo, TypeInfoVisitor

__all__ = [
    "ASTValidationContext",
    "SDLValidationContext",
    "ValidationContext",
    "VariableUsage",
    "VariableUsageVisitor",
]

NodeWithSelectionSet = Union[OperationDefinitionNode, FragmentDefinitionNode]


class VariableUsage(NamedTuple):
    node: VariableNode
    type: Optional[GraphQLInputType]
    default_value: Any


class VariableUsageVisitor(Visitor):
    """Visitor adding all variable usages to a given list."""

    usages: List[VariableUsage]

    def __init__(self, type_info: TypeInfo):
        super().__init__()
        self.usages = []
        self._append_usage = self.usages.append
        self._type_info = type_info

    def enter_variable_definition(self, *_args: Any) -> VisitorAction:
        return self.SKIP

    def enter_variable(self, node: VariableNode, *_args: Any) -> VisitorAction:
        type_info = self._type_info
        usage = VariableUsage(
            node, type_info.get_input_type(), type_info.get_default_value()
        )
        self._append_usage(usage)
        return None


class ASTValidationContext:
    """Utility class providing a context for validation of an AST.

    An instance of this class is passed as the context attribute to all Validators,
    allowing access to commonly useful contextual information from within a validation
    rule.
    """

    document: DocumentNode

    _fragments: Optional[Dict[str, FragmentDefinitionNode]]
    _fragment_spreads: Dict[SelectionSetNode, List[FragmentSpreadNode]]
    _recursively_referenced_fragments: Dict[
        OperationDefinitionNode, List[FragmentDefinitionNode]
    ]

    def __init__(
        self, ast: DocumentNode, on_error: Callable[[GraphQLError], None]
    ) -> None:
        self.document = ast
        self.on_error = on_error  # type: ignore
        self._fragments = None
        self._fragment_spreads = {}
        self._recursively_referenced_fragments = {}

    def on_error(self, error: GraphQLError) -> None:
        pass

    def report_error(self, error: GraphQLError) -> None:
        self.on_error(error)

    def get_fragment(self, name: str) -> Optional[FragmentDefinitionNode]:
        fragments = self._fragments
        if fragments is None:
            fragments = {
                statement.name.value: statement
                for statement in self.document.definitions
                if isinstance(statement, FragmentDefinitionNode)
            }

            self._fragments = fragments
        return fragments.get(name)

    def get_fragment_spreads(self, node: SelectionSetNode) -> List[FragmentSpreadNode]:
        spreads = self._fragment_spreads.get(node)
        if spreads is None:
            spreads = []
            append_spread = spreads.append
            sets_to_visit = [node]
            append_set = sets_to_visit.append
            pop_set = sets_to_visit.pop
            while sets_to_visit:
                visited_set = pop_set()
                for selection in visited_set.selections:
                    if isinstance(selection, FragmentSpreadNode):
                        append_spread(selection)
                    else:
                        set_to_visit = cast(
                            NodeWithSelectionSet, selection
                        ).selection_set
                        if set_to_visit:
                            append_set(set_to_visit)
            self._fragment_spreads[node] = spreads
        return spreads

    def get_recursively_referenced_fragments(
        self, operation: OperationDefinitionNode
    ) -> List[FragmentDefinitionNode]:
        fragments = self._recursively_referenced_fragments.get(operation)
        if fragments is None:
            fragments = []
            append_fragment = fragments.append
            collected_names: Set[str] = set()
            add_name = collected_names.add
            nodes_to_visit = [operation.selection_set]
            append_node = nodes_to_visit.append
            pop_node = nodes_to_visit.pop
            get_fragment = self.get_fragment
            get_fragment_spreads = self.get_fragment_spreads
            while nodes_to_visit:
                visited_node = pop_node()
                for spread in get_fragment_spreads(visited_node):
                    frag_name = spread.name.value
                    if frag_name not in collected_names:
                        add_name(frag_name)
                        fragment = get_fragment(frag_name)
                        if fragment:
                            append_fragment(fragment)
                            append_node(fragment.selection_set)
            self._recursively_referenced_fragments[operation] = fragments
        return fragments


class SDLValidationContext(ASTValidationContext):
    """Utility class providing a context for validation of an SDL AST.

    An instance of this class is passed as the context attribute to all Validators,
    allowing access to commonly useful contextual information from within a validation
    rule.
    """

    schema: Optional[GraphQLSchema]

    def __init__(
        self,
        ast: DocumentNode,
        schema: Optional[GraphQLSchema],
        on_error: Callable[[GraphQLError], None],
    ) -> None:
        super().__init__(ast, on_error)
        self.schema = schema


class ValidationContext(ASTValidationContext):
    """Utility class providing a context for validation using a GraphQL schema.

    An instance of this class is passed as the context attribute to all Validators,
    allowing access to commonly useful contextual information from within a validation
    rule.
    """

    schema: GraphQLSchema

    _type_info: TypeInfo
    _variable_usages: Dict[NodeWithSelectionSet, List[VariableUsage]]
    _recursive_variable_usages: Dict[OperationDefinitionNode, List[VariableUsage]]

    def __init__(
        self,
        schema: GraphQLSchema,
        ast: DocumentNode,
        type_info: TypeInfo,
        on_error: Callable[[GraphQLError], None],
    ) -> None:
        super().__init__(ast, on_error)
        self.schema = schema
        self._type_info = type_info
        self._variable_usages = {}
        self._recursive_variable_usages = {}

    def get_variable_usages(self, node: NodeWithSelectionSet) -> List[VariableUsage]:
        usages = self._variable_usages.get(node)
        if usages is None:
            usage_visitor = VariableUsageVisitor(self._type_info)
            visit(node, TypeInfoVisitor(self._type_info, usage_visitor))
            usages = usage_visitor.usages
            self._variable_usages[node] = usages
        return usages

    def get_recursive_variable_usages(
        self, operation: OperationDefinitionNode
    ) -> List[VariableUsage]:
        usages = self._recursive_variable_usages.get(operation)
        if usages is None:
            get_variable_usages = self.get_variable_usages
            usages = get_variable_usages(operation)
            for fragment in self.get_recursively_referenced_fragments(operation):
                usages.extend(get_variable_usages(fragment))
            self._recursive_variable_usages[operation] = usages
        return usages

    def get_type(self) -> Optional[GraphQLOutputType]:
        return self._type_info.get_type()

    def get_parent_type(self) -> Optional[GraphQLCompositeType]:
        return self._type_info.get_parent_type()

    def get_input_type(self) -> Optional[GraphQLInputType]:
        return self._type_info.get_input_type()

    def get_parent_input_type(self) -> Optional[GraphQLInputType]:
        return self._type_info.get_parent_input_type()

    def get_field_def(self) -> Optional[GraphQLField]:
        return self._type_info.get_field_def()

    def get_directive(self) -> Optional[GraphQLDirective]:
        return self._type_info.get_directive()

    def get_argument(self) -> Optional[GraphQLArgument]:
        return self._type_info.get_argument()

    def get_enum_value(self) -> Optional[GraphQLEnumValue]:
        return self._type_info.get_enum_value()
