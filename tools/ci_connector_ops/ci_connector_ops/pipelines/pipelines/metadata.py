#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import uuid
from pathlib import Path
from typing import Optional, Set

import dagger
from ci_connector_ops.pipelines.actions.environments import with_pip_packages, with_poetry_module, with_python_base
from ci_connector_ops.pipelines.bases import Report, Step, StepResult
from ci_connector_ops.pipelines.contexts import PipelineContext
from ci_connector_ops.pipelines.helpers.steps import run_steps
from ci_connector_ops.pipelines.utils import DAGGER_CONFIG, METADATA_FILE_NAME, METADATA_ICON_FILE_NAME, execute_concurrently

METADATA_DIR = "airbyte-ci/connectors/metadata_service"
METADATA_LIB_MODULE_PATH = "lib"
METADATA_ORCHESTRATOR_MODULE_PATH = "orchestrator"

# HELPERS


def get_metadata_file_from_path(context: PipelineContext, metadata_path: Path) -> dagger.File:
    if metadata_path.is_file() and metadata_path.name != METADATA_FILE_NAME:
        raise ValueError(f"The metadata file name is not {METADATA_FILE_NAME}, it is {metadata_path.name} .")
    if metadata_path.is_dir():
        metadata_path = metadata_path / METADATA_FILE_NAME
    if not metadata_path.exists():
        raise FileNotFoundError(f"{str(metadata_path)} does not exist.")
    return context.get_repo_dir(str(metadata_path.parent), include=[METADATA_FILE_NAME]).file(METADATA_FILE_NAME)


def get_metadata_icon_file_from_path(context: PipelineContext, metadata_icon_path: Path) -> dagger.File:
    return context.get_repo_dir(str(metadata_icon_path.parent), include=[METADATA_ICON_FILE_NAME]).file(METADATA_ICON_FILE_NAME)


# STEPS


class PoetryRun(Step):
    def __init__(self, context: PipelineContext, title: str, parent_dir_path: str, module_path: str):
        self.title = title
        super().__init__(context)
        self.parent_dir = self.context.get_repo_dir(parent_dir_path)
        self.module_path = module_path
        self.poetry_run_container = with_poetry_module(self.context, self.parent_dir, self.module_path).with_entrypoint(["poetry", "run"])

    async def _run(self, poetry_run_args: list) -> StepResult:
        poetry_run_exec = self.poetry_run_container.with_exec(poetry_run_args)
        return await self.get_step_result(poetry_run_exec)


class MetadataValidation(PoetryRun):
    def __init__(self, context: PipelineContext, metadata_path: Path):
        title = f"Validate {metadata_path}"
        super().__init__(context, title, METADATA_DIR, METADATA_LIB_MODULE_PATH)
        self.poetry_run_container = self.poetry_run_container.with_mounted_file(
            METADATA_FILE_NAME, get_metadata_file_from_path(context, metadata_path)
        )

    async def _run(self) -> StepResult:
        return await super()._run(["metadata_service", "validate", METADATA_FILE_NAME])


class MetadataUpload(PoetryRun):
    def __init__(
        self,
        context: PipelineContext,
        metadata_path: Path,
        metadata_bucket_name: str,
        metadata_service_gcs_credentials_secret: dagger.Secret,
        docker_hub_username_secret: dagger.Secret,
        docker_hub_password_secret: dagger.Secret,
    ):
        title = f"Upload {metadata_path}"
        self.gcs_bucket_name = metadata_bucket_name
        super().__init__(context, title, METADATA_DIR, METADATA_LIB_MODULE_PATH)

        # Ensure the icon file is included in the upload
        base_container = self.poetry_run_container.with_file(METADATA_FILE_NAME, get_metadata_file_from_path(context, metadata_path))
        metadata_icon_path = metadata_path.parent / METADATA_ICON_FILE_NAME
        if metadata_icon_path.exists():
            base_container = base_container.with_file(
                METADATA_ICON_FILE_NAME, get_metadata_icon_file_from_path(context, metadata_icon_path)
            )

        self.poetry_run_container = (
            base_container.with_secret_variable("DOCKER_HUB_USERNAME", docker_hub_username_secret)
            .with_secret_variable("DOCKER_HUB_PASSWORD", docker_hub_password_secret)
            .with_secret_variable("GCS_CREDENTIALS", metadata_service_gcs_credentials_secret)
            # The cache buster ensures we always run the upload command (in case of remote bucket change)
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
        )

    async def _run(self) -> StepResult:
        return await super()._run(
            [
                "metadata_service",
                "upload",
                METADATA_FILE_NAME,
                self.gcs_bucket_name,
            ]
        )


class DeployOrchestrator(Step):
    title = "Deploy Metadata Orchestrator to Dagster Cloud"
    deploy_dagster_command = [
        "dagster-cloud",
        "serverless",
        "deploy-python-executable",
        "--location-name",
        "metadata_service_orchestrator",
        "--location-file",
        "dagster_cloud.yaml",
        "--organization",
        "airbyte-connectors",
        "--deployment",
        "prod",
        "--python-version",
        "3.9",
    ]

    async def _run(self) -> StepResult:
        parent_dir = self.context.get_repo_dir(METADATA_DIR)
        python_base = with_python_base(self.context)
        python_with_dependencies = with_pip_packages(python_base, ["dagster-cloud==1.2.6", "poetry2setup==1.1.0"])
        dagster_cloud_api_token_secret: dagger.Secret = (
            self.context.dagger_client.host().env_variable("DAGSTER_CLOUD_METADATA_API_TOKEN").secret()
        )

        container_to_run = (
            python_with_dependencies.with_mounted_directory("/src", parent_dir)
            .with_secret_variable("DAGSTER_CLOUD_API_TOKEN", dagster_cloud_api_token_secret)
            .with_workdir(f"/src/{METADATA_ORCHESTRATOR_MODULE_PATH}")
            .with_exec(["/bin/sh", "-c", "poetry2setup >> setup.py"])
            .with_exec(self.deploy_dagster_command)
        )
        return await self.get_step_result(container_to_run)


class TestOrchestrator(PoetryRun):
    def __init__(self, context: PipelineContext):
        super().__init__(
            context=context,
            title="Test Metadata Orchestrator",
            parent_dir_path=METADATA_DIR,
            module_path=METADATA_ORCHESTRATOR_MODULE_PATH,
        )

    async def _run(self) -> StepResult:
        return await super()._run(["pytest"])


# PIPELINES


async def run_metadata_validation_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    dagger_logs_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
    metadata_to_validate: Set[Path],
) -> bool:
    metadata_pipeline_context = PipelineContext(
        pipeline_name="Validate metadata.yaml files",
        is_local=is_local,
        git_branch=git_branch,
        git_revision=git_revision,
        gha_workflow_run_url=gha_workflow_run_url,
        dagger_logs_url=dagger_logs_url,
        pipeline_start_timestamp=pipeline_start_timestamp,
        ci_context=ci_context,
    )

    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        metadata_pipeline_context.dagger_client = dagger_client.pipeline(metadata_pipeline_context.pipeline_name)
        async with metadata_pipeline_context:
            validation_steps = [MetadataValidation(metadata_pipeline_context, metadata_path).run for metadata_path in metadata_to_validate]

            results = await execute_concurrently(validation_steps, concurrency=10)
            metadata_pipeline_context.report = Report(
                pipeline_context=metadata_pipeline_context, steps_results=results, name="METADATA VALIDATION RESULTS"
            )

        return metadata_pipeline_context.report.success


async def run_metadata_lib_test_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    dagger_logs_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
) -> bool:
    metadata_pipeline_context = PipelineContext(
        pipeline_name="Metadata Service Lib Unit Test Pipeline",
        is_local=is_local,
        git_branch=git_branch,
        git_revision=git_revision,
        gha_workflow_run_url=gha_workflow_run_url,
        dagger_logs_url=dagger_logs_url,
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
            metadata_pipeline_context.report = Report(
                pipeline_context=metadata_pipeline_context, steps_results=[result], name="METADATA LIB TEST RESULTS"
            )

    return metadata_pipeline_context.report.success


async def run_metadata_orchestrator_test_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    dagger_logs_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
) -> bool:
    metadata_pipeline_context = PipelineContext(
        pipeline_name="Metadata Service Orchestrator Unit Test Pipeline",
        is_local=is_local,
        git_branch=git_branch,
        git_revision=git_revision,
        gha_workflow_run_url=gha_workflow_run_url,
        dagger_logs_url=dagger_logs_url,
        pipeline_start_timestamp=pipeline_start_timestamp,
        ci_context=ci_context,
    )

    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        metadata_pipeline_context.dagger_client = dagger_client.pipeline(metadata_pipeline_context.pipeline_name)
        async with metadata_pipeline_context:
            test_orch_step = TestOrchestrator(context=metadata_pipeline_context)
            result = await test_orch_step.run()
            metadata_pipeline_context.report = Report(
                pipeline_context=metadata_pipeline_context, steps_results=[result], name="METADATA ORCHESTRATOR TEST RESULTS"
            )

    return metadata_pipeline_context.report.success


async def run_metadata_upload_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    dagger_logs_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
    metadata_to_upload: Set[Path],
    gcs_bucket_name: str,
) -> bool:
    pipeline_context = PipelineContext(
        pipeline_name="Metadata Upload Pipeline",
        is_local=is_local,
        git_branch=git_branch,
        git_revision=git_revision,
        gha_workflow_run_url=gha_workflow_run_url,
        dagger_logs_url=dagger_logs_url,
        pipeline_start_timestamp=pipeline_start_timestamp,
        ci_context=ci_context,
    )

    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        pipeline_context.dagger_client = dagger_client.pipeline(pipeline_context.pipeline_name)
        async with pipeline_context:
            gcs_credentials_secret: dagger.Secret = pipeline_context.dagger_client.host().env_variable("GCS_CREDENTIALS").secret()
            docker_hub_username_secret: dagger.Secret = pipeline_context.dagger_client.host().env_variable("DOCKER_HUB_USERNAME").secret()
            docker_hub_password_secret: dagger.Secret = pipeline_context.dagger_client.host().env_variable("DOCKER_HUB_PASSWORD").secret()

            results = await execute_concurrently(
                [
                    MetadataUpload(
                        context=pipeline_context,
                        metadata_service_gcs_credentials_secret=gcs_credentials_secret,
                        docker_hub_username_secret=docker_hub_username_secret,
                        docker_hub_password_secret=docker_hub_password_secret,
                        metadata_bucket_name=gcs_bucket_name,
                        metadata_path=metadata_path,
                    ).run
                    for metadata_path in metadata_to_upload
                ]
            )
            pipeline_context.report = Report(pipeline_context, results, name="METADATA UPLOAD RESULTS")

        return pipeline_context.report.success


async def run_metadata_orchestrator_deploy_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    dagger_logs_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
) -> bool:
    metadata_pipeline_context = PipelineContext(
        pipeline_name="Metadata Service Orchestrator Unit Test Pipeline",
        is_local=is_local,
        git_branch=git_branch,
        git_revision=git_revision,
        gha_workflow_run_url=gha_workflow_run_url,
        dagger_logs_url=dagger_logs_url,
        pipeline_start_timestamp=pipeline_start_timestamp,
        ci_context=ci_context,
    )

    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        metadata_pipeline_context.dagger_client = dagger_client.pipeline(metadata_pipeline_context.pipeline_name)

        async with metadata_pipeline_context:
            steps = [TestOrchestrator(context=metadata_pipeline_context), DeployOrchestrator(context=metadata_pipeline_context)]
            steps_results = await run_steps(steps)
            metadata_pipeline_context.report = Report(
                pipeline_context=metadata_pipeline_context, steps_results=steps_results, name="METADATA ORCHESTRATOR DEPLOY RESULTS"
            )
    return metadata_pipeline_context.report.success
