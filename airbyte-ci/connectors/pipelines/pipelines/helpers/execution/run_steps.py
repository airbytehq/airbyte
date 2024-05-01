#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""The actions package is made to declare reusable pipeline components."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Set, Tuple, Union

import anyio
import asyncer
import dpath
from pipelines import main_logger
from pipelines.models.steps import StepStatus

if TYPE_CHECKING:
    from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
    from pipelines.models.steps import STEP_PARAMS, Step, StepResult

    RESULTS_DICT = Dict[str, StepResult]
    ARGS_TYPE = Union[Dict, Callable[[RESULTS_DICT], Dict], Awaitable[Dict]]


class InvalidStepConfiguration(Exception):
    pass


def _get_dependency_graph(steps: STEP_TREE) -> Dict[str, List[str]]:
    """
    Get the dependency graph of a step tree.
    """
    dependency_graph: Dict[str, List[str]] = {}
    for step in steps:
        if isinstance(step, StepToRun):
            dependency_graph[step.id] = step.depends_on
        elif isinstance(step, list):
            nested_dependency_graph = _get_dependency_graph(list(step))
            dependency_graph = {**dependency_graph, **nested_dependency_graph}
        else:
            raise Exception(f"Unexpected step type: {type(step)}")

    return dependency_graph


def _get_transitive_dependencies_for_step_id(
    dependency_graph: Dict[str, List[str]], step_id: str, visited: Optional[Set[str]] = None
) -> List[str]:
    """Get the transitive dependencies for a step id.

    Args:
        dependency_graph (Dict[str, str]): The dependency graph to use.
        step_id (str): The step id to get the transitive dependencies for.
        visited (Optional[Set[str]], optional): The set of visited step ids. Defaults to None.

    Returns:
        List[str]: List of transitive dependencies as step ids.
    """
    if visited is None:
        visited = set()

    if step_id not in visited:
        visited.add(step_id)

        dependencies: List[str] = dependency_graph.get(step_id, [])
        for dependency in dependencies:
            dependencies.extend(_get_transitive_dependencies_for_step_id(dependency_graph, dependency, visited))

        return dependencies
    else:
        return []


@dataclass
class RunStepOptions:
    """Options for the run_step function."""

    fail_fast: bool = True
    skip_steps: List[str] = field(default_factory=list)
    keep_steps: List[str] = field(default_factory=list)
    log_step_tree: bool = True
    concurrency: int = 10
    step_params: Dict[CONNECTOR_TEST_STEP_ID, STEP_PARAMS] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.skip_steps and self.keep_steps:
            raise ValueError("Cannot use both skip_steps and keep_steps at the same time")

    def get_step_ids_to_skip(self, runnables: STEP_TREE) -> List[str]:
        if self.skip_steps:
            return self.skip_steps
        if self.keep_steps:
            step_ids_to_keep = set(self.keep_steps)
            dependency_graph = _get_dependency_graph(runnables)
            all_step_ids = set(dependency_graph.keys())
            for step_id in self.keep_steps:
                step_ids_to_keep.update(_get_transitive_dependencies_for_step_id(dependency_graph, step_id))
            return list(all_step_ids - step_ids_to_keep)
        return []

    @staticmethod
    def get_item_or_default(options: Dict[str, List[Any]], key: str, default: Any) -> Any:  # noqa: ANN401
        try:
            item = dpath.util.get(options, key, separator="/")
        except KeyError:
            return default

        if not isinstance(item, List):
            return item
        if len(item) > 1:
            raise ValueError(f"Only one value for {key} is allowed. Got {len(item)}")
        return item[0] if item else default


@dataclass(frozen=True)
class StepToRun:
    """
    A class to wrap a Step with its id and args.

    Used to coordinate the execution of multiple steps inside a pipeline.
    """

    id: CONNECTOR_TEST_STEP_ID
    step: Step
    args: ARGS_TYPE = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)


STEP_TREE = List[StepToRun | List[StepToRun]]


async def evaluate_run_args(args: ARGS_TYPE, results: RESULTS_DICT) -> Dict:
    """
    Evaluate the args of a StepToRun using the results of previous steps.
    """
    if inspect.iscoroutinefunction(args):
        return await args(results)
    elif callable(args):
        return args(results)
    elif isinstance(args, dict):
        return args

    raise TypeError(f"Unexpected args type: {type(args)}")


def _skip_remaining_steps(remaining_steps: STEP_TREE) -> RESULTS_DICT:
    """
    Skip all remaining steps.
    """
    skipped_results: Dict[str, StepResult] = {}
    for runnable_step in remaining_steps:
        if isinstance(runnable_step, StepToRun):
            skipped_results[runnable_step.id] = runnable_step.step.skip()
        elif isinstance(runnable_step, list):
            nested_skipped_results = _skip_remaining_steps(list(runnable_step))
            skipped_results = {**skipped_results, **nested_skipped_results}
        else:
            raise Exception(f"Unexpected step type: {type(runnable_step)}")

    return skipped_results


def _step_dependencies_succeeded(step_to_eval: StepToRun, results: RESULTS_DICT) -> bool:
    """
    Check if all dependencies of a step have succeeded.
    """
    main_logger.info(f"Checking if dependencies {step_to_eval.depends_on} have succeeded")

    # Check if all depends_on keys are in the results dict
    # If not, that means a step has not been run yet
    # Implying that the order of the steps are not correct
    for step_id in step_to_eval.depends_on:
        if step_id not in results:
            raise InvalidStepConfiguration(
                f"Step {step_to_eval.id} depends on {step_id} which has not been run yet. This implies that the order of the steps is not correct. Please check that the steps are in the correct order."
            )

    return all(results[step_id] and results[step_id].status is StepStatus.SUCCESS for step_id in step_to_eval.depends_on)


def _filter_skipped_steps(steps_to_evaluate: STEP_TREE, skip_steps: List[str], results: RESULTS_DICT) -> Tuple[STEP_TREE, RESULTS_DICT]:
    """
    Filter out steps that should be skipped.

    Either because they are in the skip list or because one of their dependencies failed.
    """
    steps_to_run: STEP_TREE = []
    for step_to_eval in steps_to_evaluate:

        # ignore nested steps
        if isinstance(step_to_eval, list):
            steps_to_run.append(step_to_eval)
            continue

        # skip step if its id is in the skip list
        if step_to_eval.id in skip_steps:
            main_logger.info(f"Skipping step {step_to_eval.id}")
            results[step_to_eval.id] = step_to_eval.step.skip("Skipped by user")

        # skip step if a dependency failed
        elif not _step_dependencies_succeeded(step_to_eval, results):
            main_logger.info(
                f"Skipping step {step_to_eval.id} because one of the dependencies have not been met: {step_to_eval.depends_on}"
            )
            results[step_to_eval.id] = step_to_eval.step.skip("Skipped because a dependency was not met")

        else:
            steps_to_run.append(step_to_eval)

    return steps_to_run, results


def _get_next_step_group(steps: STEP_TREE) -> Tuple[STEP_TREE, STEP_TREE]:
    """
    Get the next group of steps to run concurrently.
    """
    if not steps:
        return [], []

    if isinstance(steps[0], list):
        return list(steps[0]), list(steps[1:])
    else:
        # Termination case: if the next step is not a list that means we have reached the max depth
        return steps, []


def _log_step_tree(step_tree: STEP_TREE, options: RunStepOptions, depth: int = 0) -> None:
    """
    Log the step tree to the console.

    e.g.
    Step tree
    - step1
    - step2
        - step3
        - step4 (skip)
            - step5
    - step6
    """
    indent = "    "
    for steps in step_tree:
        if isinstance(steps, list):
            _log_step_tree(list(steps), options, depth + 1)
        else:
            if steps.id in options.skip_steps:
                main_logger.info(f"{indent * depth}- {steps.id} (skip)")
            else:
                main_logger.info(f"{indent * depth}- {steps.id}")


async def run_steps(
    runnables: STEP_TREE,
    results: RESULTS_DICT = {},
    options: RunStepOptions = RunStepOptions(),
) -> RESULTS_DICT:
    """Run multiple steps sequentially, or in parallel if steps are wrapped into a sublist.

    Examples
    --------
    >>> from pipelines.models.steps import Step, StepResult, StepStatus
    >>> class TestStep(Step):
    ...     async def _run(self) -> StepResult:
    ...         return StepResult(step=self, status=StepStatus.SUCCESS)
    >>> steps = [
    ...     StepToRun(id="step1", step=TestStep()),
    ...     [
    ...         StepToRun(id="step2", step=TestStep()),
    ...         StepToRun(id="step3", step=TestStep()),
    ...     ],
    ...     StepToRun(id="step4", step=TestStep()),
    ... ]
    >>> results = await run_steps(steps)
    >>> results["step1"].status
    <StepStatus.SUCCESS: 1>
    >>> results["step2"].status
    <StepStatus.SUCCESS: 1>
    >>> results["step3"].status
    <StepStatus.SUCCESS: 1>
    >>> results["step4"].status
    <StepStatus.SUCCESS: 1>


    Args:
        runnables (List[StepToRun]): List of steps to run.
        results (RESULTS_DICT, optional): Dictionary of step results, used for recursion.

    Returns:
        RESULTS_DICT: Dictionary of step results.
    """
    # If there are no steps to run, return the results
    if not runnables:
        return results

    step_ids_to_skip = options.get_step_ids_to_skip(runnables)
    # Log the step tree
    if options.log_step_tree:
        main_logger.info(f"STEP TREE: {runnables}")
        _log_step_tree(runnables, options)
        options.log_step_tree = False

    # If any of the previous steps failed, skip the remaining steps
    if options.fail_fast and any(result.status is StepStatus.FAILURE for result in results.values()):
        skipped_results = _skip_remaining_steps(runnables)
        return {**results, **skipped_results}

    # Pop the next step to run
    steps_to_evaluate, remaining_steps = _get_next_step_group(runnables)

    # Remove any skipped steps
    steps_to_run, results = _filter_skipped_steps(steps_to_evaluate, step_ids_to_skip, results)

    # Run all steps in list concurrently
    semaphore = anyio.Semaphore(options.concurrency)
    async with semaphore:
        async with asyncer.create_task_group() as task_group:
            tasks = []
            for step_to_run in steps_to_run:
                # if the step to run is a list, run it in parallel
                if isinstance(step_to_run, list):
                    tasks.append(task_group.soonify(run_steps)(list(step_to_run), results, options))
                else:
                    step_args = await evaluate_run_args(step_to_run.args, results)
                    step_to_run.step.extra_params = options.step_params.get(step_to_run.id, {})
                    main_logger.info(f"QUEUING STEP {step_to_run.id}")
                    tasks.append(task_group.soonify(step_to_run.step.run)(**step_args))

    # Apply new results
    new_results: Dict[str, Any] = {}
    for i, task in enumerate(tasks):
        step_to_run = steps_to_run[i]
        if isinstance(step_to_run, list):
            new_results = {**new_results, **task.value}
        else:
            new_results[step_to_run.id] = task.value

    return await run_steps(
        runnables=remaining_steps,
        results={**results, **new_results},
        options=options,
    )
