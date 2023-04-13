#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pathlib import Path
from typing import Optional, Set

import dagger
from ci_connector_ops.pipelines.actions.environments import with_poetry_module
from ci_connector_ops.pipelines.bases import Step, StepStatus, TestReport
from ci_connector_ops.pipelines.contexts import PipelineContext
from ci_connector_ops.pipelines.utils import DAGGER_CONFIG, execute_concurrently

METADATA_DIR = "airbyte-ci/connectors/metadata_service"
METADATA_LIB_MODULE_PATH = "lib"
METADATA_ORCHESTRATOR_MODULE_PATH = "orchestrator"


class PoetryRun(Step):
    def __init__(self, context: PipelineContext, title: str, parent_dir_path: str, module_path: str):
        self.title = title
        super().__init__(context)
        self.parent_dir = self.context.get_repo_dir(parent_dir_path)
        self.module_path = module_path
        self.poetry_run_container = with_poetry_module(self.context, self.parent_dir, self.module_path).with_entrypoint(["poetry", "run"])

    async def _run(self, poetry_run_args: list) -> StepStatus:
        poetry_run_exec = self.poetry_run_container.with_exec(poetry_run_args)
        return await self.get_step_result(poetry_run_exec)


class MetadataValidation(PoetryRun):
    def __init__(self, context: PipelineContext, metadata_file_path: Path):
        super().__init__(context, f"Validate {metadata_file_path}", METADATA_DIR, METADATA_LIB_MODULE_PATH)
        self.metadata_file = self.context.get_repo_dir(str(metadata_file_path), include=["metadata.yaml"]).file("metadata.yaml")
        self.poetry_run_container = self.poetry_run_container.with_mounted_file("metadata.yaml", self.metadata_file)

    async def _run(self) -> StepStatus:
        return await super()._run(["metadata_service", "validate", "metadata.yaml"])


async def run_metadata_validation_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
    metadata_source_paths: Set[Path],
) -> bool:
    metadata_pipeline_context = PipelineContext(
        pipeline_name="Metadata Service Validation Pipeline",
        is_local=is_local,
        git_branch=git_branch,
        git_revision=git_revision,
        gha_workflow_run_url=gha_workflow_run_url,
        pipeline_start_timestamp=pipeline_start_timestamp,
        ci_context=ci_context,
    )

    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        metadata_pipeline_context.dagger_client = dagger_client.pipeline(metadata_pipeline_context.pipeline_name)
        async with metadata_pipeline_context:
            validation_steps = [MetadataValidation(metadata_pipeline_context, metadata_path).run for metadata_path in metadata_source_paths]

            results = await execute_concurrently(validation_steps, concurrency=len(validation_steps))
            metadata_pipeline_context.test_report = TestReport(pipeline_context=metadata_pipeline_context, steps_results=results)

        return metadata_pipeline_context.test_report.success


async def run_metadata_lib_test_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
) -> bool:
    metadata_pipeline_context = PipelineContext(
        pipeline_name="Metadata Service Lib Unit Test Pipeline",
        is_local=is_local,
        git_branch=git_branch,
        git_revision=git_revision,
        gha_workflow_run_url=gha_workflow_run_url,
        pipeline_start_timestamp=pipeline_start_timestamp,
        ci_context=ci_context,
    )

    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        metadata_pipeline_context.dagger_client = dagger_client.pipeline(metadata_pipeline_context.pipeline_name)
        async with metadata_pipeline_context:
            test_lib_step = PoetryRun(
                context=metadata_pipeline_context,
                title="Test Metadata Service Lib",
                parent_dir_path=METADATA_DIR,
                module_path=METADATA_LIB_MODULE_PATH,
            )
            result = await test_lib_step.run(["pytest"])
            metadata_pipeline_context.test_report = TestReport(pipeline_context=metadata_pipeline_context, steps_results=[result])

    return metadata_pipeline_context.test_report.success


async def run_metadata_orchestrator_test_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
) -> bool:
    metadata_pipeline_context = PipelineContext(
        pipeline_name="Metadata Service Orchestrator Unit Test Pipeline",
        is_local=is_local,
        git_branch=git_branch,
        git_revision=git_revision,
        gha_workflow_run_url=gha_workflow_run_url,
        pipeline_start_timestamp=pipeline_start_timestamp,
        ci_context=ci_context,
    )

    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        metadata_pipeline_context.dagger_client = dagger_client.pipeline(metadata_pipeline_context.pipeline_name)
        async with metadata_pipeline_context:
            test_orch_step = PoetryRun(
                context=metadata_pipeline_context,
                title="Test Metadata Service Orchestrator",
                parent_dir_path=METADATA_DIR,
                module_path=METADATA_ORCHESTRATOR_MODULE_PATH,
            )
            result = await test_orch_step.run(["pytest"])
            metadata_pipeline_context.test_report = TestReport(pipeline_context=metadata_pipeline_context, steps_results=[result])

    return metadata_pipeline_context.test_report.success
