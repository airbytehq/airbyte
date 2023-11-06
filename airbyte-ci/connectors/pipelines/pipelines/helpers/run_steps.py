#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""The actions package is made to declare reusable pipeline components."""

from __future__ import annotations
from dataclasses import dataclass, field
import inspect
from pipelines import main_logger

from typing import TYPE_CHECKING, Callable, Dict, List, Tuple, Union

import asyncer
from pipelines.models.steps import StepStatus

if TYPE_CHECKING:
    from pipelines.models.steps import Step, StepResult
    # dict, function that returns a dict, or a coroutine that returns a dict
    ARGS_TYPE = Union[Dict, Callable[[Dict[str, StepResult]], Dict]]


@dataclass(frozen=True)
class RunStepOptions:
    """Options for the run_step function."""

    # If true, the step will be skipped if any of the previous steps failed
    fail_fast: bool = True
    skip_steps: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class StepToRun:
    id: str
    step: Step
    args: ARGS_TYPE = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)

STEP_TREE = List[StepToRun | List[StepToRun]]


async def evaluate_run_args(args: ARGS_TYPE, results: Dict[str, StepResult]) -> Dict:
    if inspect.iscoroutinefunction(args):
        return await args(results)
    elif callable(args):
        return args(results)

    return args

def _skip_remaining_steps(remaining_steps: STEP_TREE) -> bool:
    skipped_results = {}
    for runnable_step in remaining_steps:
        if isinstance(runnable_step, StepToRun):
            skipped_results[runnable_step.id] = runnable_step.step.skip()
        elif isinstance(runnable_step, list):
            nested_skipped_results = _skip_remaining_steps(runnable_step)
            skipped_results = {**skipped_results, **nested_skipped_results}
        else:
            raise Exception(f"Unexpected step type: {type(runnable_step)}")

    return skipped_results

def _step_dependencies_succeeded(depends_on: List[str], results: Dict[str, StepResult]) -> bool:
    return all(results[step_id].status is StepStatus.SUCCESS for step_id in depends_on)

def _filter_skipped_steps(steps_to_evaluate: STEP_TREE, skip_steps: List[str], results: Dict[str, StepResult]) -> Tuple[STEP_TREE, Dict[str, StepResult]]:
    steps_to_run = []
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
        elif not _step_dependencies_succeeded(step_to_eval.depends_on, results):
            main_logger.info(f"Skipping step {step_to_eval.id} because one of the dependencies have not been met: {step_to_eval.depends_on}")
            results[step_to_eval.id] = step_to_eval.step.skip("Skipped because a dependency was not met")

        else:
            steps_to_run.append(step_to_eval)

    return steps_to_run, results

def _get_next_step_group(steps: STEP_TREE) -> Tuple[STEP_TREE, STEP_TREE]:
    if not steps:
        return [], []

    if isinstance(steps[0], list):
        return steps[0], steps[1:]
    else:
        return steps, []

async def run_steps(
    runnables: STEP_TREE,
    results: Dict[str, StepResult] = {},
    options: RunStepOptions = RunStepOptions(),
) -> Dict[str, StepResult]:
    """Run multiple steps sequentially, or in parallel if steps are wrapped into a sublist.

    Examples
    --------
    >>> from pipelines.models.steps import Step, StepResult, StepStatus
    >>> class TestStep(Step):
    ...     async def _run(self) -> StepResult:
    ...         return StepResult(self, StepStatus.SUCCESS)
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
        results (Dict[str, StepResult], optional): Dictionary of step results, used for recursion.

    Returns:
        Dict[str, StepResult]: Dictionary of step results.
    """
    # If there are no steps to run, return the results
    if not runnables:
        return results

    # If any of the previous steps failed, skip the remaining steps
    if options.fail_fast and any(result.status is StepStatus.FAILURE for result in results.values()):
        skipped_results = _skip_remaining_steps(runnables)
        return {**results, **skipped_results}

    # Pop the next step to run
    steps_to_evaluate, remaining_steps = _get_next_step_group(runnables)

    # Remove any skipped steps
    steps_to_run, results = _filter_skipped_steps(steps_to_evaluate, options.skip_steps, results)

    # Run all steps in list concurrently
    async with asyncer.create_task_group() as task_group:
        tasks = []
        for step_to_run in steps_to_run:
            # if the step to run is a list, run it in parallel
            if isinstance(step_to_run, list):
                tasks.append(task_group.soonify(run_steps)(step_to_run, results, options))
            else:
                step_args = await evaluate_run_args(step_to_run.args, results)
                main_logger.info(f"QUEUING STEP {step_to_run.id}")
                tasks.append(task_group.soonify(step_to_run.step.run)(**step_args))

    # apply new results
    new_results = {}
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
