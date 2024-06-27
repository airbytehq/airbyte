#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import uuid
from typing import Optional

import asyncclick as click
import dagger
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.steps.docker import SimpleDockerStep
from pipelines.airbyte_ci.steps.poetry import PoetryRunStep
from pipelines.consts import DOCS_DIRECTORY_ROOT_PATH, GIT_DIRECTORY_ROOT_PATH, INTERNAL_TOOL_PATHS
from pipelines.dagger.actions.python.common import with_pip_packages
from pipelines.dagger.containers.python import with_python_base
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun, run_steps
from pipelines.helpers.utils import DAGGER_CONFIG, get_secret_host_variable
from pipelines.models.reports import Report
from pipelines.models.secrets import Secret
from pipelines.models.steps import MountPath, Step, StepResult

# STEPS


class MetadataValidation(SimpleDockerStep):
    def __init__(self, context: ConnectorContext) -> None:
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
            secret_env_variables={"DOCKER_HUB_USERNAME": context.docker_hub_username, "DOCKER_HUB_PASSWORD": context.docker_hub_password}
            if context.docker_hub_username and context.docker_hub_password
            else None,
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
        metadata_service_gcs_credentials: Secret,
        docker_hub_username: Secret,
        docker_hub_password: Secret,
        pre_release: bool = False,
        pre_release_tag: Optional[str] = None,
    ) -> None:
        title = f"Upload metadata for {context.connector.technical_name} v{context.connector.version}"
        command_to_run = [
            "metadata_service",
            "upload",
            str(context.connector.metadata_file_path),
            DOCS_DIRECTORY_ROOT_PATH,
            metadata_bucket_name,
        ]

        if pre_release and pre_release_tag:
            command_to_run += ["--prerelease", pre_release_tag]

        super().__init__(
            title=title,
            context=context,
            paths_to_mount=[
                MountPath(GIT_DIRECTORY_ROOT_PATH),
                MountPath(context.connector.metadata_file_path),
                MountPath(DOCS_DIRECTORY_ROOT_PATH),
                MountPath(context.connector.icon_path, optional=True),
            ],
            internal_tools=[
                MountPath(INTERNAL_TOOL_PATHS.METADATA_SERVICE.value),
            ],
            secret_env_variables={
                "DOCKER_HUB_USERNAME": docker_hub_username,
                "DOCKER_HUB_PASSWORD": docker_hub_password,
                "GCS_CREDENTIALS": metadata_service_gcs_credentials,
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
        "--python-version",
        "3.10",
    ]

    async def _run(self) -> StepResult:
        # mount metadata_service/lib and metadata_service/orchestrator
        parent_dir = self.context.get_repo_dir("airbyte-ci/connectors/metadata_service")
        python_base = with_python_base(self.context, "3.10")
        python_with_dependencies = with_pip_packages(python_base, ["dagster-cloud[serverless]==1.5.14", "poetry2setup==1.1.0"])
        dagster_cloud_api_token_secret: dagger.Secret = get_secret_host_variable(
            self.context.dagger_client, "DAGSTER_CLOUD_METADATA_API_TOKEN"
        )

        # get env var DAGSTER_CLOUD_DEPLOYMENT default to dev
        target_deployment = os.getenv("DAGSTER_CLOUD_DEPLOYMENT", "dev")

        self.context.logger.info(f"Deploying to deployment: {target_deployment}")

        container_to_run = (
            python_with_dependencies.with_mounted_directory("/src", parent_dir)
            .with_secret_variable("DAGSTER_CLOUD_API_TOKEN", dagster_cloud_api_token_secret)
            .with_env_variable("DAGSTER_CLOUD_DEPLOYMENT", target_deployment)
            .with_workdir("/src/orchestrator")
            .with_exec(["/bin/sh", "-c", "poetry2setup >> setup.py"])
            .with_exec(["/bin/sh", "-c", "cat setup.py"])
            .with_exec(self.deploy_dagster_command)
        )
        return await self.get_step_result(container_to_run)


class TestOrchestrator(PoetryRunStep):
    def __init__(self, context: PipelineContext) -> None:
        super().__init__(
            context=context,
            title="Test Metadata Orchestrator",
            parent_dir_path="airbyte-ci/connectors/metadata_service",
            module_path="orchestrator",
            poetry_run_args=["pytest"],
        )


# PIPELINES


async def run_metadata_orchestrator_deploy_pipeline(
    ctx: click.Context,
    is_local: bool,
    git_branch: str,
    git_revision: str,
    diffed_branch: str,
    git_repo_url: str,
    report_output_prefix: str,
    gha_workflow_run_url: Optional[str],
    dagger_logs_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
) -> bool:
    success: bool = False

    metadata_pipeline_context = PipelineContext(
        pipeline_name="Metadata Service Orchestrator Deploy Pipeline",
        is_local=is_local,
        git_branch=git_branch,
        git_revision=git_revision,
        diffed_branch=diffed_branch,
        git_repo_url=git_repo_url,
        report_output_prefix=report_output_prefix,
        gha_workflow_run_url=gha_workflow_run_url,
        dagger_logs_url=dagger_logs_url,
        pipeline_start_timestamp=pipeline_start_timestamp,
        ci_context=ci_context,
    )
    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        metadata_pipeline_context.dagger_client = dagger_client.pipeline(metadata_pipeline_context.pipeline_name)

        async with metadata_pipeline_context:
            steps: STEP_TREE = [
                [
                    StepToRun(
                        id=CONNECTOR_TEST_STEP_ID.TEST_ORCHESTRATOR,
                        step=TestOrchestrator(context=metadata_pipeline_context),
                    )
                ],
                [
                    StepToRun(
                        id=CONNECTOR_TEST_STEP_ID.DEPLOY_ORCHESTRATOR,
                        step=DeployOrchestrator(context=metadata_pipeline_context),
                        depends_on=[CONNECTOR_TEST_STEP_ID.TEST_ORCHESTRATOR],
                    )
                ],
            ]
            steps_results = await run_steps(steps)
            report = Report(
                pipeline_context=metadata_pipeline_context,
                steps_results=list(steps_results.values()),
                name="METADATA ORCHESTRATOR DEPLOY RESULTS",
            )
            metadata_pipeline_context.report = report
            success = report.success
    return success
