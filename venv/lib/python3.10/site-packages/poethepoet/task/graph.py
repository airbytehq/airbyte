from typing import TYPE_CHECKING, Dict, List, Set, Tuple

from ..exceptions import CyclicDependencyError

if TYPE_CHECKING:
    from ..context import RunContext
    from .base import PoeTask


class TaskExecutionNode:
    task: "PoeTask"
    direct_dependants: List["TaskExecutionNode"]
    direct_dependencies: Set[Tuple[str, ...]]
    path_dependants: Tuple[str, ...]
    capture_stdout: bool

    def __init__(
        self,
        task: "PoeTask",
        direct_dependants: List["TaskExecutionNode"],
        path_dependants: Tuple[str, ...],
        capture_stdout: bool = False,
    ):
        self.task = task
        self.direct_dependants = direct_dependants
        self.direct_dependencies = set()
        self.path_dependants = (task.name, *path_dependants)
        self.capture_stdout = capture_stdout

    def is_source(self):
        return not self.task.has_deps()

    @property
    def identifier(self) -> Tuple[str, ...]:
        return self.task.invocation


class TaskExecutionGraph:
    """
    A directed-acyclic execution graph of tasks, with a single sink node, and any number
    of source nodes. Non-source nodes may have multiple upstream nodes, and non-sink
    nodes may have multiple downstream nodes.

    A task/node may appear twice in the graph, if one instance has captured output, and
    one does not. Nodes are deduplicated to enforce this.
    """

    _context: "RunContext"
    sink: TaskExecutionNode
    sources: List[TaskExecutionNode]
    captured_tasks: Dict[Tuple[str, ...], TaskExecutionNode]
    uncaptured_tasks: Dict[Tuple[str, ...], TaskExecutionNode]

    def __init__(
        self,
        sink_task: "PoeTask",
        context: "RunContext",
    ):
        self._context = context
        self.sink = TaskExecutionNode(sink_task, [], tuple())
        self.sources = []
        self.captured_tasks = {}
        self.uncaptured_tasks = {}

        # Build graph
        self._resolve_node_deps(self.sink)

    def get_execution_plan(self) -> List[List["PoeTask"]]:
        """
        Derive an execution plan from the DAG in terms of stages consisting of tasks
        that could theoretically be parallelized.
        """
        # TODO: if we parallelize tasks then this should be modified to support lazy
        #       scheduling

        stages: List[List[TaskExecutionNode]] = [self.sources]
        visited = {source.identifier for source in self.sources}

        while True:
            next_stage = []
            for node in stages[-1]:
                for dep_node in node.direct_dependants:
                    if (
                        dep_node.identifier in visited
                        or not dep_node.direct_dependencies.issubset(visited)
                    ):
                        # We've already added this node OR some dependencies of dep_node
                        # have not been added so we can't add it yet
                        continue

                    next_stage.append(dep_node)
                    visited.add(dep_node.identifier)

            if not next_stage:
                break

            stages.append(next_stage)

        return [[node.task for node in stage] for stage in stages]

    def _resolve_node_deps(self, node: TaskExecutionNode):
        """
        Build a DAG of tasks by depth-first traversal of the dependency tree starting
        from the sink node.
        """
        for key, task in node.task.iter_upstream_tasks(self._context):
            node.direct_dependencies.add(task.invocation)

            if task.invocation in node.path_dependants:
                raise CyclicDependencyError(
                    f"Encountered cyclic task dependency with task: {task.name!r}"
                )

            # a non empty key indicates output is captured
            capture_stdout = bool(key)

            # Check if a node already exists for this task
            if capture_stdout:
                if task.invocation in self.captured_tasks:
                    # reuse instance of task with captured output
                    self.captured_tasks[task.invocation].direct_dependants.append(node)
                    continue
            elif task.invocation in self.uncaptured_tasks:
                # reuse instance of task with uncaptured output
                self.uncaptured_tasks[task.invocation].direct_dependants.append(node)
                continue

            # This task has not been encountered before via another path
            new_node = TaskExecutionNode(
                task, [node], node.path_dependants, capture_stdout
            )

            # Keep track of this task/node so it can be found by other dependants
            if capture_stdout:
                self.captured_tasks[task.invocation] = new_node
            else:
                self.uncaptured_tasks[task.invocation] = new_node

            if new_node.is_source():
                # Track this node as having no dependencies
                self.sources.append(new_node)
            else:
                # Recurse immediately for DFS
                self._resolve_node_deps(new_node)
