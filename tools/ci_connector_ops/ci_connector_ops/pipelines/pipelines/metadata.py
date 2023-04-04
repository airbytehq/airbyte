import dagger
from typing import Optional, Set, List

from ci_connector_ops.pipelines.bases import Step, StepStatus, TestReport
from ci_connector_ops.pipelines.actions.environments import with_poetry_module,with_pipx_module, DEFAULT_PYTHON_EXCLUDE
from ci_connector_ops.pipelines.contexts import PipelineContext
from ci_connector_ops.pipelines.utils import (
    DAGGER_CONFIG,
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
    def __init__(self, context: PipelineContext, title: str, args: List[str]):
        self.title = title
        self.args = args
        super().__init__(context)

    async def _run(self) -> StepStatus:
        print("HI!!!")
        print(self.args)
        run_test = self.context.dagger_client.with_exec(self.args)
        return await self.get_step_result(run_test)

def path_to_metadata_validation_step(metadata_pipeline_context: PipelineContext, metadata_path: str) -> Step:
    return SimpleExecStep(
                context=metadata_pipeline_context,
                title=f"Validate Connector Metadata Manifest: {metadata_path}",
                args=["metadata_service", "validate", str(metadata_path)]
            )

async def run_metadata_validation_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
    metadata_source_paths: Set[str] # TODO actually a Path
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

        # TODO refactor the environemnts to use containers not contexts
        metadata_pipeline_context.dagger_client = dagger_client.pipeline(metadata_pipeline_context.pipeline_name)
        updated_client = with_pipx_module(
            metadata_pipeline_context,
            ".",
            f"{METADATA_DIR}/{METADATA_LIB_MODULE_PATH}",
            include=["airbyte-integrations/connectors/*"])

        metadata_pipeline_context.dagger_client = updated_client

        async with metadata_pipeline_context:
            validation_steps = [
                path_to_metadata_validation_step(metadata_pipeline_context, metadata_path)
                for metadata_path in metadata_source_paths
            ]
            results = []
            for validation_step in validation_steps:
                result = await validation_step.run()
                results.append(result)

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
