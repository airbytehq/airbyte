#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List

from pipelines.dagger.actions.python.poetry import with_poetry_module
from pipelines.models.contexts.pipeline_context import PipelineContext
from pipelines.models.steps import Step, StepResult


class PoetryRunStep(Step):
    def __init__(self, context: PipelineContext, title: str, parent_dir_path: str, module_path: str, poetry_run_args: List[str]) -> None:
        """A simple step that runs a given command inside a poetry project.

        Args:
            context (PipelineContext): context of the step
            title (str): name of the step
            parent_dir_path (str): The path to the parent directory of the poetry project
            module_path (str): The path to the poetry project
            poetry_run_args (List[str]): The arguments to pass to the poetry run command
        """
        self._title = title
        super().__init__(context)

        parent_dir = self.context.get_repo_dir(parent_dir_path)
        module_path = module_path
        self.poetry_run_args = poetry_run_args
        self.poetry_run_container = with_poetry_module(self.context, parent_dir, module_path).with_entrypoint(["poetry", "run"])

    @property
    def title(self) -> str:
        return self._title

    async def _run(self) -> StepResult:
        poetry_run_exec = self.poetry_run_container.with_exec(self.poetry_run_args)
        return await self.get_step_result(poetry_run_exec)
