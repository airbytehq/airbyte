import dagger
from typing import Optional

from ci_connector_ops.pipelines.bases import Step, StepStatus, TestReport
from ci_connector_ops.pipelines.actions.environments import with_poetry_module
from ci_connector_ops.pipelines.contexts import PipelineContext
from ci_connector_ops.pipelines.utils import (
    DAGGER_CONFIG,
)

METADATA_DIR = "airbyte-ci/connectors/metadata_service"
METADATA_LIB_MODULE_PATH = "lib"
METADATA_ORCHESTRATOR_MODULE_PATH = "orchestrator"


class TestPoetryModule(Step):
    def __init__(self, context: PipelineContext, title: str, parent_dir: str, module_path: str):
        self.title = title
        self.parent_dir = parent_dir
        self.module_path = module_path
        super().__init__(context)

    async def _run(self) -> StepStatus:
        metadata_lib_module = with_poetry_module(self.context, self.parent_dir, self.module_path)
        run_test = metadata_lib_module.with_exec(["poetry", "run", "pytest"])
        return await self.get_step_result(run_test)


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
                parent_dir=METADATA_DIR,
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
                parent_dir=METADATA_DIR,
                module_path=METADATA_ORCHESTRATOR_MODULE_PATH,
            )
            result = await test_orch_step.run()
            metadata_pipeline_context.test_report = TestReport(pipeline_context=metadata_pipeline_context, steps_results=[result])

    return metadata_pipeline_context.test_report.success
