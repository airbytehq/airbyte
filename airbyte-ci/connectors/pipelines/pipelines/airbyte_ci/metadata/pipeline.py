#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import uuid
from typing import Optional

import dagger
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.steps.docker import SimpleDockerStep
from pipelines.airbyte_ci.steps.poetry import PoetryRunStep
from pipelines.consts import DOCS_DIRECTORY_ROOT_PATH, INTERNAL_TOOL_PATHS
from pipelines.dagger.actions.python.common import with_pip_packages
from pipelines.dagger.containers.python import with_python_base
from pipelines.helpers.steps import run_steps
from pipelines.helpers.utils import DAGGER_CONFIG, get_secret_host_variable
from pipelines.models.reports import Report
from pipelines.models.steps import MountPath, Step, StepResult

# STEPS


class MetadataValidation(SimpleDockerStep):
    def __init__(self, context: ConnectorContext):
        super().__init__(
            title=f"Validate metadata for {context.connector.technical_name}",
            context=context,
            paths_to_mount=[
                MountPath(context.connector.metadata_file_path),
                MountPath(DOCS_DIRECTORY_ROOT_PATH),
                MountPath(context.connector.icon_path, optional=True),
            ],
            internal_tools=[
                MountPath(INTERNAL_TOOL_PATHS.METADATA_SERVICE.value),
            ],
            command=[
                "metadata_service",
                "validate",
                str(context.connector.metadata_file_path),
                DOCS_DIRECTORY_ROOT_PATH,
            ],
        )


class MetadataUpload(SimpleDockerStep):
    # When the metadata service exits with this code, it means the metadata is valid but the upload was skipped because the metadata is already uploaded
    skipped_exit_code = 5

    def __init__(
        self,
        context: ConnectorContext,
        metadata_bucket_name: str,
        metadata_service_gcs_credentials_secret: dagger.Secret,
        docker_hub_username_secret: dagger.Secret,
        docker_hub_password_secret: dagger.Secret,
        pre_release: bool = False,
        pre_release_tag: Optional[str] = None,
    ):
        title = f"Upload metadata for {context.connector.technical_name} v{context.connector.version}"
        command_to_run = [
            "metadata_service",
            "upload",
            str(context.connector.metadata_file_path),
            DOCS_DIRECTORY_ROOT_PATH,
            metadata_bucket_name,
        ]

        if pre_release:
            command_to_run += ["--prerelease", pre_release_tag]

        super().__init__(
            title=title,
            context=context,
            paths_to_mount=[
                MountPath(context.connector.metadata_file_path),
                MountPath(DOCS_DIRECTORY_ROOT_PATH),
                MountPath(context.connector.icon_path, optional=True),
            ],
            internal_tools=[
                MountPath(INTERNAL_TOOL_PATHS.METADATA_SERVICE.value),
            ],
            secrets={
                "DOCKER_HUB_USERNAME": docker_hub_username_secret,
                "DOCKER_HUB_PASSWORD": docker_hub_password_secret,
                "GCS_CREDENTIALS": metadata_service_gcs_credentials_secret,
            },
            env_variables={
                # The cache buster ensures we always run the upload command (in case of remote bucket change)
                "CACHEBUSTER": str(uuid.uuid4()),
            },
            command=command_to_run,
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
        # mount metadata_service/lib and metadata_service/orchestrator
        parent_dir = self.context.get_repo_dir("airbyte-ci/connectors/metadata_service")
        python_base = with_python_base(self.context, "3.9")
        python_with_dependencies = with_pip_packages(python_base, ["dagster-cloud==1.2.6", "pydantic==1.10.6", "poetry2setup==1.1.0"])
        dagster_cloud_api_token_secret: dagger.Secret = get_secret_host_variable(
            self.context.dagger_client, "DAGSTER_CLOUD_METADATA_API_TOKEN"
        )

        container_to_run = (
            python_with_dependencies.with_mounted_directory("/src", parent_dir)
            .with_secret_variable("DAGSTER_CLOUD_API_TOKEN", dagster_cloud_api_token_secret)
            .with_workdir(f"/src/orchestrator")
            .with_exec(["/bin/sh", "-c", "poetry2setup >> setup.py"])
            .with_exec(self.deploy_dagster_command)
        )
        return await self.get_step_result(container_to_run)


class TestOrchestrator(PoetryRunStep):
    def __init__(self, context: PipelineContext):
        super().__init__(
            context=context,
            title="Test Metadata Orchestrator",
            parent_dir_path="airbyte-ci/connectors/metadata_service",
            module_path="orchestrator",
        )

    async def _run(self) -> StepResult:
        return await super()._run(["pytest"])


# PIPELINES


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
