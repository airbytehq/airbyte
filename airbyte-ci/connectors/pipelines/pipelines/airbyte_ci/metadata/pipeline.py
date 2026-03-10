#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import uuid
from typing import Optional

import dagger

from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.steps.docker import SimpleDockerStep
from pipelines.consts import DOCS_DIRECTORY_ROOT_PATH, GIT_DIRECTORY_ROOT_PATH, INTERNAL_TOOL_PATHS
from pipelines.models.secrets import Secret
from pipelines.models.steps import MountPath

# STEPS


class MetadataValidation(SimpleDockerStep):
    def __init__(self, context: ConnectorContext) -> None:
        super().__init__(
            title=f"Validate metadata for {context.connector.technical_name}",
            context=context,
            paths_to_mount=[
                MountPath(context.connector.code_directory),
                MountPath(DOCS_DIRECTORY_ROOT_PATH),
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
                MountPath(DOCS_DIRECTORY_ROOT_PATH),
                MountPath(context.connector.code_directory),
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


class MetadataRollbackReleaseCandidate(SimpleDockerStep):
    def __init__(
        self,
        context: ConnectorContext,
        metadata_bucket_name: str,
        metadata_service_gcs_credentials: Secret,
    ) -> None:
        docker_repository = context.connector.metadata["dockerRepository"]
        version = context.connector.metadata["dockerImageTag"]
        title = f"Rollback release candidate for {docker_repository} v{version}"
        command_to_run = [
            "metadata_service",
            "rollback-release-candidate",
            docker_repository,
            version,
            metadata_bucket_name,
        ]

        super().__init__(
            title=title,
            context=context,
            internal_tools=[
                MountPath(INTERNAL_TOOL_PATHS.METADATA_SERVICE.value),
            ],
            secret_env_variables={
                "GCS_CREDENTIALS": metadata_service_gcs_credentials,
            },
            env_variables={
                # The cache buster ensures we always run the rollback command (in case of remote bucket change)
                "CACHEBUSTER": str(uuid.uuid4()),
            },
            command=command_to_run,
        )


class MetadataPromoteReleaseCandidate(SimpleDockerStep):
    def __init__(
        self,
        context: ConnectorContext,
        metadata_bucket_name: str,
        metadata_service_gcs_credentials: Secret,
    ) -> None:
        docker_repository = context.connector.metadata["dockerRepository"]
        version = context.connector.metadata["dockerImageTag"]
        title = f"Promote release candidate for {docker_repository} v{version}"
        command_to_run = [
            "metadata_service",
            "promote-release-candidate",
            docker_repository,
            version,
            metadata_bucket_name,
        ]

        super().__init__(
            title=title,
            context=context,
            internal_tools=[
                MountPath(INTERNAL_TOOL_PATHS.METADATA_SERVICE.value),
            ],
            secret_env_variables={
                "GCS_CREDENTIALS": metadata_service_gcs_credentials,
            },
            env_variables={
                # The cache buster ensures we always run the rollback command (in case of remote bucket change)
                "CACHEBUSTER": str(uuid.uuid4()),
            },
            command=command_to_run,
        )
