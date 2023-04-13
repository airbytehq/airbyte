#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import uuid
from pathlib import Path
from typing import Optional, Set

import dagger
from ci_connector_ops.pipelines.actions.environments import with_poetry_module
from ci_connector_ops.pipelines.bases import Step, StepStatus, TestReport
from ci_connector_ops.pipelines.contexts import PipelineContext
from ci_connector_ops.pipelines.utils import DAGGER_CONFIG, METADATA_FILE_NAME, execute_concurrently

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


def get_metadata_file_from_path(context: PipelineContext, metadata_path: Path) -> dagger.File:
    if metadata_path.is_file() and metadata_path.name != METADATA_FILE_NAME:
        breakpoint()
        raise ValueError(f"The metadata file name is not {METADATA_FILE_NAME}, it is {metadata_path.name} .")
    if metadata_path.is_dir():
        metadata_path = metadata_path / METADATA_FILE_NAME
    if not metadata_path.exists():
        raise FileNotFoundError(f"{str(metadata_path)} does not exist.")
    return context.get_repo_dir(str(metadata_path.parent), include=[METADATA_FILE_NAME]).file(METADATA_FILE_NAME)


class MetadataValidation(PoetryRun):
    def __init__(self, context: PipelineContext, metadata_path: Path):
        title = f"Validate {metadata_path}"
        super().__init__(context, title, METADATA_DIR, METADATA_LIB_MODULE_PATH)
        self.poetry_run_container = self.poetry_run_container.with_mounted_file(
            METADATA_FILE_NAME, get_metadata_file_from_path(context, metadata_path)
        )

    async def _run(self) -> StepStatus:
        return await super()._run(["metadata_service", "validate", METADATA_FILE_NAME])


class MetadataUpload(PoetryRun):

    GCS_CREDENTIALS_CONTAINER_PATH = "gcs_credentials.json"

    def __init__(self, context: PipelineContext, metadata_path: Path, gcs_bucket_name: str, gcs_credentials: str):
        title = f"Upload {metadata_path}"
        self.gcs_bucket_name = gcs_bucket_name
        super().__init__(context, title, METADATA_DIR, METADATA_LIB_MODULE_PATH)
        self.poetry_run_container = (
            self.poetry_run_container.with_file(METADATA_FILE_NAME, get_metadata_file_from_path(context, metadata_path)).with_new_file(
                self.GCS_CREDENTIALS_CONTAINER_PATH, gcs_credentials
            )
            # The cache buster ensures we always run the upload command (in case of remote bucket change)
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
        )

    async def _run(self) -> StepStatus:
        return await super()._run(
            [
                "metadata_service",
                "upload",
                METADATA_FILE_NAME,
                self.gcs_bucket_name,
                "--service-account-file-path",
                self.GCS_CREDENTIALS_CONTAINER_PATH,
            ]
        )


async def run_metadata_validation_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
    metadata_to_validate: Set[Path],
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
            validation_steps = [MetadataValidation(metadata_pipeline_context, metadata_path).run for metadata_path in metadata_to_validate]

            results = await execute_concurrently(validation_steps, concurrency=10)
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


async def run_metadata_upload_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
    metadata_to_upload: Set[Path],
    gcs_bucket_name: str,
    gcs_credentials: str,
) -> bool:
    pipeline_context = PipelineContext(
        pipeline_name="Metadata Upload Pipeline",
        is_local=is_local,
        git_branch=git_branch,
        git_revision=git_revision,
        gha_workflow_run_url=gha_workflow_run_url,
        pipeline_start_timestamp=pipeline_start_timestamp,
        ci_context=ci_context,
    )

    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        pipeline_context.dagger_client = dagger_client.pipeline(pipeline_context.pipeline_name)

        async with pipeline_context:

            results = await execute_concurrently(
                [
                    MetadataUpload(pipeline_context, metadata_path, gcs_bucket_name, gcs_credentials).run
                    for metadata_path in metadata_to_upload
                ]
            )
            pipeline_context.test_report = TestReport(pipeline_context, results)

        return pipeline_context.test_report.success
