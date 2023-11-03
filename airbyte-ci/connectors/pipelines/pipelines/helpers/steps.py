#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""The actions package is made to declare reusable pipeline components."""

from __future__ import annotations
from dataclasses import dataclass, field

from typing import TYPE_CHECKING, Callable, Dict, List, Tuple, Union

import asyncer
from pipelines.models.steps import Step, StepStatus

if TYPE_CHECKING:
    from pipelines.models.steps import StepResult

@dataclass
class Runnable:
    id: str
    step: Step
    # Dict or a function that takes a list of step results and returns a dict
    args: Union[Dict, Callable[[Dict[str, StepResult]], Dict]] = field(default_factory=dict)

def evaluate_run_args(args: Union[Dict, Callable[[Dict[str, StepResult]], Dict]], results: Dict[str, StepResult]) -> Dict:
    if callable(args):
        return args(results)
    return args

async def new_run_steps(
    runnables: List[Runnable], results: Dict[str, StepResult] = {}
) -> Dict[str, StepResult]:
    """Run multiple steps sequentially, or in parallel if steps are wrapped into a sublist.

    Args:
        runnables (List[Runnable]): List of steps to run.
        results (Dict[str, StepResult], optional): Dictionary of step results, used for recursion.

    Returns:
        Dict[str, StepResult]: Dictionary of step results.
    """
    # If there are no steps to run, return the results
    if not runnables:
        return results

    # If any of the previous steps failed, skip the remaining steps
    if any(result.status is StepStatus.FAILURE for result in results.values()):
        skipped_results = {}
        for runnable_step in runnables:
            skipped_results[runnable_step.id] = runnable_step.step.skip()
        return {**results, **skipped_results}

    # Pop the next step to run
    steps_to_run, remaining_steps = runnables[0], runnables[1:]

    # wrap the step in a list if it is not already (allows for parallel steps)
    if not isinstance(steps_to_run, list):
        steps_to_run = [steps_to_run]

    async with asyncer.create_task_group() as task_group:
        tasks = []
        for step_to_run in steps_to_run:
            args = evaluate_run_args(step_to_run.args, results)
            tasks.append(task_group.soonify(step_to_run.step.run)(*args))

    new_results = {steps_to_run[i].id: task.value for i, task in enumerate(tasks)}

    return await new_run_steps(remaining_steps, {**results, **new_results})



async def run_steps(
    steps_and_run_args: List[Union[Step, Tuple[Step, Tuple]] | List[Union[Step, Tuple[Step, Tuple]]]], results: List[StepResult] = []
) -> List[StepResult]:
    """Run multiple steps sequentially, or in parallel if steps are wrapped into a sublist.

    Args:
        steps_and_run_args (List[Union[Step, Tuple[Step, Tuple]] | List[Union[Step, Tuple[Step, Tuple]]]]): List of steps to run, if steps are wrapped in a sublist they will be executed in parallel. run function arguments can be passed as a tuple along the Step instance.
        results (List[StepResult], optional): List of step results, used for recursion.

    Returns:
        List[StepResult]: List of step results.
    """
    # If there are no steps to run, return the results
    if not steps_and_run_args:
        return results

    # If any of the previous steps failed, skip the remaining steps
    if any(result.status is StepStatus.FAILURE for result in results):
        skipped_results = []
        for step_and_run_args in steps_and_run_args:
            if isinstance(step_and_run_args, Tuple):
                skipped_results.append(step_and_run_args[0].skip())
            else:
                skipped_results.append(step_and_run_args.skip())
        return results + skipped_results

    # Pop the next step to run
    steps_to_run, remaining_steps = steps_and_run_args[0], steps_and_run_args[1:]

    # wrap the step in a list if it is not already (allows for parallel steps)
    if not isinstance(steps_to_run, list):
        steps_to_run = [steps_to_run]

    async with asyncer.create_task_group() as task_group:
        tasks = []
        for step in steps_to_run:
            if isinstance(step, Step):
                tasks.append(task_group.soonify(step.run)())
            elif isinstance(step, Tuple) and isinstance(step[0], Step) and isinstance(step[1], Tuple):
                step, run_args = step
                tasks.append(task_group.soonify(step.run)(*run_args))

    new_results = [task.value for task in tasks]

    return await run_steps(remaining_steps, results + new_results)
