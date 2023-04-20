#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Tuple

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.utils import Connector
from dagger import Container


class BuildOrPullNormalization(Step):
    """A step to build or pull the normalization image for a connector according to the image name."""

    DESTINATION_SPECIFIC_NORMALIZATION_DOCKERFILE_MAPPING = {
        Connector("destination-clickhouse"): "clickhouse.Dockerfile",
        Connector("destination-duckdb"): "duckdb.Dockerfile",
        Connector("destination-mssql"): "mssql.Dockerfile",
        Connector("destination-mysql"): "mysql.Dockerfile",
        Connector("destination-oracle"): "oracle.Dockerfile",
        Connector("destination-redshift"): "redshift.Dockerfile",
        Connector("destination-snowflake"): "snowflake.Dockerfile",
        Connector("destination-tidb"): "tidb.Dockerfile",
    }

    def __init__(self, context: ConnectorContext, normalization_image: str) -> None:
        """Initialize the step to build or pull the normalization image.

        Args:
            context (ConnectorContext): The current connector context.
            normalization_image (str): The normalization image to build (if :dev) or pull.
        """
        super().__init__(context)
        self.use_dev_normalization = normalization_image.endswith(":dev")
        self.normalization_image = normalization_image
        self.normalization_dockerfile = self.DESTINATION_SPECIFIC_NORMALIZATION_DOCKERFILE_MAPPING.get(context.connector, "Dockerfile")
        self.title = f"Build {self.normalization_image}" if self.use_dev_normalization else f"Pull {self.normalization_image}"

    async def _run(self) -> Tuple[StepResult, Container]:
        if self.use_dev_normalization:
            build_normalization_container = environments.with_normalization(self.context, self.normalization_dockerfile)
        else:
            build_normalization_container = self.context.dagger_client.container().from_(self.normalization_image)
        return StepResult(self, StepStatus.SUCCESS), build_normalization_container
