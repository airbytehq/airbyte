#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Module declaring context related classes."""

from typing import Optional

import asyncclick as click
from github import PullRequest
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.consts import ContextState
from pipelines.helpers.connectors.modifed import ConnectorWithModifiedFiles
from pipelines.helpers.utils import format_duration
from pipelines.models.secrets import Secret


class PublishConnectorContext(ConnectorContext):
    def __init__(
        self,
        connector: ConnectorWithModifiedFiles,
        pre_release: bool,
        spec_cache_gcs_credentials: Secret,
        spec_cache_bucket_name: str,
        metadata_service_gcs_credentials: Secret,
        metadata_bucket_name: str,
        docker_hub_username: Secret,
        docker_hub_password: Secret,
        ci_gcp_credentials: Secret,
        slack_webhook: str,
        reporting_slack_channel: str,
        ci_report_bucket: str,
        report_output_prefix: str,
        is_local: bool,
        git_branch: str,
        git_revision: str,
        diffed_branch: str,
        git_repo_url: str,
        python_registry_url: str,
        python_registry_check_url: str,
        gha_workflow_run_url: Optional[str] = None,
        dagger_logs_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
        pull_request: Optional[PullRequest.PullRequest] = None,
        s3_build_cache_access_key_id: Optional[Secret] = None,
        s3_build_cache_secret_key: Optional[Secret] = None,
        use_local_cdk: bool = False,
        python_registry_token: Optional[Secret] = None,
    ) -> None:
        self.pre_release = pre_release
        self.spec_cache_bucket_name = spec_cache_bucket_name
        self.metadata_bucket_name = metadata_bucket_name
        self.spec_cache_gcs_credentials = spec_cache_gcs_credentials
        self.metadata_service_gcs_credentials = metadata_service_gcs_credentials
        self.python_registry_token = python_registry_token
        self.python_registry_url = python_registry_url
        self.python_registry_check_url = python_registry_check_url
        pipeline_name = f"Publish {connector.technical_name}"
        pipeline_name = pipeline_name + " (pre-release)" if pre_release else pipeline_name

        if use_local_cdk and not self.pre_release:
            raise click.UsageError("Publishing with the local CDK is only supported for pre-release publishing.")

        super().__init__(
            pipeline_name=pipeline_name,
            connector=connector,
            report_output_prefix=report_output_prefix,
            ci_report_bucket=ci_report_bucket,
            is_local=is_local,
            git_branch=git_branch,
            git_revision=git_revision,
            diffed_branch=diffed_branch,
            git_repo_url=git_repo_url,
            gha_workflow_run_url=gha_workflow_run_url,
            dagger_logs_url=dagger_logs_url,
            pipeline_start_timestamp=pipeline_start_timestamp,
            ci_context=ci_context,
            slack_webhook=slack_webhook,
            reporting_slack_channel=reporting_slack_channel,
            ci_gcp_credentials=ci_gcp_credentials,
            should_save_report=True,
            use_local_cdk=use_local_cdk,
            docker_hub_username=docker_hub_username,
            docker_hub_password=docker_hub_password,
            s3_build_cache_access_key_id=s3_build_cache_access_key_id,
            s3_build_cache_secret_key=s3_build_cache_secret_key,
        )

        # Reassigning current class required instance attribute
        # Which are optional in the super class
        # for type checking
        self.docker_hub_username: Secret = docker_hub_username
        self.docker_hub_password: Secret = docker_hub_password
        self.ci_gcp_credentials: Secret = ci_gcp_credentials

    @property
    def pre_release_suffix(self) -> str:
        return self.git_revision[:10]

    @property
    def docker_image_tag(self) -> str:
        # get the docker image tag from the parent class
        metadata_tag = super().docker_image_tag
        if self.pre_release:
            return f"{metadata_tag}-dev.{self.pre_release_suffix}"
        else:
            return metadata_tag

    def create_slack_message(self) -> str:

        docker_hub_url = f"https://hub.docker.com/r/{self.connector.metadata['dockerRepository']}/tags"
        message = f"*Publish <{docker_hub_url}|{self.docker_image}>*\n"
        if self.is_ci:
            message += f"🤖 <{self.gha_workflow_run_url}|GitHub Action workflow>\n"
        else:
            message += "🧑‍💻 Local run\n"
        message += f"*Connector:* {self.connector.technical_name}\n"
        message += f"*Version:* {self.connector.version}\n"
        branch_url = f"https://github.com/airbytehq/airbyte/tree/{self.git_branch}"
        message += f"*Branch:* <{branch_url}|{self.git_branch}>\n"
        commit_url = f"https://github.com/airbytehq/airbyte/commit/{self.git_revision}"
        message += f"*Commit:* <{commit_url}|{self.git_revision[:10]}>\n"
        if self.state in [ContextState.INITIALIZED, ContextState.RUNNING]:
            message += "🟠"
        if self.state is ContextState.SUCCESSFUL:
            message += "🟢"
        if self.state in [ContextState.FAILURE, ContextState.ERROR]:
            message += "🔴"
        message += f" {self.state.value['description']}\n"
        if self.state is ContextState.SUCCESSFUL:
            assert self.report is not None, "Report should be set when state is successful"
            message += f"⏲️ Run duration: {format_duration(self.report.run_duration)}\n"
        if self.state is ContextState.FAILURE:
            message += "\ncc. <!subteam^S03BQLNTFNC>"
        return message
