#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Type

from pipelines.airbyte_ci.connectors.context import PipelineContext
from pipelines.airbyte_ci.connectors.publish.context import PublishConnectorContext
from pipelines.consts import DEFAULT_PYTHON_PACKAGE_REGISTRY_URL
from pipelines.models.secrets import Secret


@dataclass
class PythonPackageMetadata:
    name: Optional[str]
    version: Optional[str]


class PythonRegistryPublishContext(PipelineContext):
    def __init__(
        self,
        python_registry_token: Secret,
        registry_check_url: str,
        package_path: str,
        report_output_prefix: str,
        is_local: bool,
        git_branch: str,
        git_revision: str,
        diffed_branch: str,
        git_repo_url: str,
        ci_report_bucket: Optional[str] = None,
        registry: str = DEFAULT_PYTHON_PACKAGE_REGISTRY_URL,
        gha_workflow_run_url: Optional[str] = None,
        dagger_logs_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
        ci_gcp_credentials: Optional[Secret] = None,
        package_name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> None:
        self.python_registry_token = python_registry_token
        self.registry = registry
        self.registry_check_url = registry_check_url
        self.package_path = package_path
        self.package_metadata = PythonPackageMetadata(package_name, version)

        pipeline_name = f"Publish PyPI {package_path}"

        super().__init__(
            pipeline_name=pipeline_name,
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
            ci_gcp_credentials=ci_gcp_credentials,
        )

    @classmethod
    async def from_publish_connector_context(
        cls: Type["PythonRegistryPublishContext"], connector_context: PublishConnectorContext
    ) -> Optional["PythonRegistryPublishContext"]:
        """
        Create a PythonRegistryPublishContext from a ConnectorContext.

        The metadata of the connector is read from the current workdir to capture changes that are not yet published.
        If pypi is not enabled, this will return None.
        """

        current_metadata = connector_context.connector.metadata
        connector_context.logger.info(f"Current metadata: {str(current_metadata)}")
        if (
            "remoteRegistries" not in current_metadata
            or "pypi" not in current_metadata["remoteRegistries"]
            or not current_metadata["remoteRegistries"]["pypi"]["enabled"]
        ):
            return None

        version = current_metadata["dockerImageTag"]
        if connector_context.pre_release:
            # use current date as pre-release version
            # we can't use the git revision because not all python registries allow local version identifiers. Public version identifiers must conform to PEP 440 and only allow digits.
            release_candidate_tag = datetime.now().strftime("%Y%m%d%H%M")
            version = f"{version}.dev{release_candidate_tag}"

        assert connector_context.python_registry_token is not None, "The connector context must have python_registry_token Secret attribute"
        pypi_context = cls(
            python_registry_token=connector_context.python_registry_token,
            registry=str(connector_context.python_registry_url),
            registry_check_url=str(connector_context.python_registry_check_url),
            package_path=str(connector_context.connector.code_directory),
            package_name=current_metadata["remoteRegistries"]["pypi"]["packageName"],
            version=version,
            ci_report_bucket=connector_context.ci_report_bucket,
            report_output_prefix=connector_context.report_output_prefix,
            is_local=connector_context.is_local,
            git_branch=connector_context.git_branch,
            git_revision=connector_context.git_revision,
            diffed_branch=connector_context.diffed_branch,
            git_repo_url=connector_context.git_repo_url,
            gha_workflow_run_url=connector_context.gha_workflow_run_url,
            dagger_logs_url=connector_context.dagger_logs_url,
            pipeline_start_timestamp=connector_context.pipeline_start_timestamp,
            ci_context=connector_context.ci_context,
            ci_gcp_credentials=connector_context.ci_gcp_credentials,
        )
        pypi_context.dagger_client = connector_context.dagger_client
        return pypi_context
