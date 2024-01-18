#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from datetime import datetime
from typing import Optional

from pipelines.airbyte_ci.connectors.context import PipelineContext
from pipelines.airbyte_ci.connectors.publish.context import PublishConnectorContext


class PyPIPublishContext(PipelineContext):
    def __init__(
        self,
        pypi_token: str,
        package_path: str,
        ci_report_bucket: str,
        report_output_prefix: str,
        is_local: bool,
        git_branch: bool,
        git_revision: bool,
        registry: Optional[str] = None,
        gha_workflow_run_url: Optional[str] = None,
        dagger_logs_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
        ci_gcs_credentials: str = None,
        package_name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> None:
        self.pypi_token = pypi_token
        self.registry = registry or "https://pypi.org/simple"
        self.package_path = package_path
        self.package_name = package_name
        self.version = version

        pipeline_name = f"Publish PyPI {package_path}"

        super().__init__(
            pipeline_name=pipeline_name,
            report_output_prefix=report_output_prefix,
            ci_report_bucket=ci_report_bucket,
            is_local=is_local,
            git_branch=git_branch,
            git_revision=git_revision,
            gha_workflow_run_url=gha_workflow_run_url,
            dagger_logs_url=dagger_logs_url,
            pipeline_start_timestamp=pipeline_start_timestamp,
            ci_context=ci_context,
            ci_gcs_credentials=ci_gcs_credentials,
        )

    @staticmethod
    async def from_publish_connector_context(connector_context: PublishConnectorContext) -> Optional["PyPIPublishContext"]:
        """
        Create a PyPIPublishContext from a ConnectorContext.

        The metadata of the connector is read from the current workdir to capture changes that are not yet published.
        If pypi is not enabled, this will return None.
        """

        current_metadata = connector_context.connector.metadata
        if (
            "remoteRegistries" not in current_metadata
            or "pypi" not in current_metadata["remoteRegistries"]
            or not current_metadata["remoteRegistries"]["pypi"]["enabled"]
        ):
            return None

        version = current_metadata["dockerImageTag"]
        if connector_context.pre_release:
            # use current date as pre-release version
            rc_tag = datetime.now().strftime("%Y%m%d%H%M")
            version = f"{version}.dev{rc_tag}"

        pypi_context = PyPIPublishContext(
            pypi_token=os.environ["PYPI_TOKEN"],
            registry="https://test.pypi.org/legacy/",  # TODO: go live
            package_path=str(connector_context.connector.code_directory),
            package_name=current_metadata["remoteRegistries"]["pypi"]["packageName"],
            version=version,
            ci_report_bucket=connector_context.ci_report_bucket,
            report_output_prefix=connector_context.report_output_prefix,
            is_local=connector_context.is_local,
            git_branch=connector_context.git_branch,
            git_revision=connector_context.git_revision,
            gha_workflow_run_url=connector_context.gha_workflow_run_url,
            dagger_logs_url=connector_context.dagger_logs_url,
            pipeline_start_timestamp=connector_context.pipeline_start_timestamp,
            ci_context=connector_context.ci_context,
            ci_gcs_credentials=connector_context.ci_gcs_credentials,
        )
        pypi_context.dagger_client = connector_context.dagger_client
        return pypi_context
