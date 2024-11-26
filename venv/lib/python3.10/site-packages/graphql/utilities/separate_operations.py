from typing import Any, Dict, List, Set

from ..language import (
    DocumentNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    OperationDefinitionNode,
    SelectionSetNode,
    Visitor,
    visit,
)

__all__ = ["separate_operations"]


DepGraph = Dict[str, List[str]]


def separate_operations(document_ast: DocumentNode) -> Dict[str, DocumentNode]:
    """Separate operations in a given AST document.

    This function accepts a single AST document which may contain many operations and
    fragments and returns a collection of AST documents each of which contains a single
    operation as well the fragment definitions it refers to.
    """
    operations: List[OperationDefinitionNode] = []
    dep_graph: DepGraph = {}

    # Populate metadata and build a dependency graph.
    for definition_node in document_ast.definitions:
        if isinstance(definition_node, OperationDefinitionNode):
            operations.append(definition_node)
        elif isinstance(
            definition_node, FragmentDefinitionNode
        ):  # pragma: no cover else
            dep_graph[definition_node.name.value] = collect_dependencies(
                definition_node.selection_set
            )

    # For each operation, produce a new synthesized AST which includes only what is
    # necessary for completing that operation.
    separated_document_asts: Dict[str, DocumentNode] = {}
    for operation in operations:
        dependencies: Set[str] = set()

        for fragment_name in collect_dependencies(operation.selection_set):
            collect_transitive_dependencies(dependencies, dep_graph, fragment_name)

        # Provides the empty string for anonymous operations.
        operation_name = operation.name.value if operation.name else ""

        # The list of definition nodes to be included for this operation, sorted
        # to retain the same order as the original document.
        separated_document_asts[operation_name] = DocumentNode(
            definitions=[
                node
                for node in document_ast.definitions
                if node is operation
                or (
                    isinstance(node, FragmentDefinitionNode)
                    and node.name.value in dependencies
                )
            ]
        )

    return separated_document_asts


def collect_transitive_dependencies(
    collected: Set[str], dep_graph: DepGraph, from_name: str
) -> None:
    """Collect transitive dependencies.

    From a dependency graph, collects a list of transitive dependencies by recursing
    through a dependency graph.
    """
    if from_name not in collected:
        collected.add(from_name)

        immediate_deps = dep_graph.get(from_name)
        if immediate_deps is not None:
            for to_name in immediate_deps:
                collect_transitive_dependencies(collected, dep_graph, to_name)


class DependencyCollector(Visitor):
    dependencies: List[str]

    def __init__(self) -> None:
        super().__init__()
        self.dependencies = []
        self.add_dependency = self.dependencies.append

    def enter_fragment_spread(self, node: FragmentSpreadNode, *_args: Any) -> None:
        self.add_dependency(node.name.value)


def collect_dependencies(selection_set: SelectionSetNode) -> List[str]:
    collector = DependencyCollector()
    visit(selection_set, collector)
    return collector.dependencies
