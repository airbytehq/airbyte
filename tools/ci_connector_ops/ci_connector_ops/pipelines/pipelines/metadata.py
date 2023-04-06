import dagger
from typing import Optional, Set, List
from pathlib import Path

from ci_connector_ops.pipelines.bases import Step, StepStatus, TestReport
from ci_connector_ops.pipelines.actions.environments import with_poetry_module, with_pipx_module, DEFAULT_PYTHON_EXCLUDE
from ci_connector_ops.pipelines.contexts import PipelineContext
from ci_connector_ops.pipelines.utils import (
    DAGGER_CONFIG,
    execute_concurrently,
)

METADATA_DIR = "airbyte-ci/connectors/metadata_service"
METADATA_LIB_MODULE_PATH = "lib"
METADATA_ORCHESTRATOR_MODULE_PATH = "orchestrator"


class TestPoetryModule(Step):
    def __init__(self, context: PipelineContext, title: str, parent_dir_path: str, module_path: str):
        self.title = title
        self.parent_dir_path = parent_dir_path
        self.module_path = module_path
        super().__init__(context)

    async def _run(self) -> StepStatus:
        # TODO (ben): Use the GlobalExclusion when merged (https://github.com/airbytehq/airbyte/pull/24225/files#diff-c86417158894333350d986efd59ffada645270c1c65b4eec7645a0b63ac2d915R46)
        parent_dir = self.context.get_repo_dir(self.parent_dir_path, exclude=DEFAULT_PYTHON_EXCLUDE)
        metadata_lib_module = with_poetry_module(self.context, parent_dir, self.module_path)
        run_test = metadata_lib_module.with_exec(["poetry", "run", "pytest"])
        return await self.get_step_result(run_test)


class SimpleExecStep(Step):
    def __init__(self, context: PipelineContext, title: str, args: List[str], parent_container: dagger.Container):
        self.title = title
        self.args = args
        self.parent_container = parent_container
        super().__init__(context)

    async def _run(self) -> StepStatus:
        run_command = self.parent_container.with_exec(self.args)
        return await self.get_step_result(run_command)


def metadata_validation_step(metadata_pipeline_context: PipelineContext, metadata_path: Path, parent_container: dagger.Container) -> Step:
    return SimpleExecStep(
        context=metadata_pipeline_context,
        title=f"Validate Connector Metadata Manifest: {metadata_path}",
        args=["metadata_service", "validate", str(metadata_path)],
        parent_container=parent_container,
    )


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
            parent_container = with_pipx_module(
                metadata_pipeline_context,
                ".",
                f"{METADATA_DIR}/{METADATA_LIB_MODULE_PATH}",
                include=["airbyte-integrations/connectors/*"],
            )

            validation_steps = [
                metadata_validation_step(metadata_pipeline_context, metadata_path, parent_container).run
                for metadata_path in metadata_source_paths
            ]

            results = await execute_concurrently(validation_steps)
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
            test_lib_step = TestPoetryModule(
                context=metadata_pipeline_context,
                title="Test Metadata Service Lib",
                parent_dir_path=METADATA_DIR,
                module_path=METADATA_LIB_MODULE_PATH,
            )
            result = await test_lib_step.run()
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
            test_orch_step = TestPoetryModule(
                context=metadata_pipeline_context,
                title="Test Metadata Service Orchestrator",
                parent_dir_path=METADATA_DIR,
                module_path=METADATA_ORCHESTRATOR_MODULE_PATH,
            )
            result = await test_orch_step.run()
            metadata_pipeline_context.test_report = TestReport(pipeline_context=metadata_pipeline_context, steps_results=[result])

    return metadata_pipeline_context.test_report.success
