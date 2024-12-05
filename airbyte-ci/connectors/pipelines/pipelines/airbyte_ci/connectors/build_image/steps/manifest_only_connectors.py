#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any

from dagger import Container, Platform
from pipelines.airbyte_ci.connectors.build_image.steps import build_customization
from pipelines.airbyte_ci.connectors.build_image.steps.common import BuildConnectorImagesBase
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.consts import COMPONENTS_FILE_PATH, MANIFEST_FILE_PATH
from pipelines.models.steps import StepResult
from pydash.objects import get  # type: ignore


class BuildConnectorImages(BuildConnectorImagesBase):
    """
    A step to build a manifest only connector image.
    A spec command is run on the container to validate it was built successfully.
    """

    context: ConnectorContext
    PATH_TO_INTEGRATION_CODE = "/airbyte/integration_code"

    async def _build_connector(self, platform: Platform, *args: Any) -> Container:
        baseImage = get(self.context.connector.metadata, "connectorBuildOptions.baseImage")
        if not baseImage:
            raise ValueError("connectorBuildOptions.baseImage is required to build a manifest only connector.")

        return await self._build_from_base_image(platform)

    def _get_base_container(self, platform: Platform) -> Container:
        base_image_name = get(self.context.connector.metadata, "connectorBuildOptions.baseImage")
        self.logger.info(f"Building manifest connector from base image {base_image_name}")
        return self.dagger_client.container(platform=platform).from_(base_image_name)

    async def _build_from_base_image(self, platform: Platform) -> Container:
        """Build the connector container using the base image defined in the metadata, in the connectorBuildOptions.baseImage field.

        Returns:
            Container: The connector container built from the base image.
        """
        self.logger.info(f"Building connector from base image in metadata for {platform}")

        # Mount manifest file
        base_container = self._get_base_container(platform).with_file(
            f"source_declarative_manifest/{MANIFEST_FILE_PATH}",
            (await self.context.get_connector_dir(include=[MANIFEST_FILE_PATH])).file(MANIFEST_FILE_PATH),
        )

        # Mount components file if it exists
        components_file = self.context.connector.manifest_only_components_path
        if components_file.exists():
            base_container = base_container.with_file(
                f"source_declarative_manifest/{COMPONENTS_FILE_PATH}",
                (await self.context.get_connector_dir(include=[COMPONENTS_FILE_PATH])).file(COMPONENTS_FILE_PATH),
            )

        connector_container = build_customization.apply_airbyte_entrypoint(base_container, self.context.connector)
        return connector_container


async def run_connector_build(context: ConnectorContext) -> StepResult:
    return await BuildConnectorImages(context).run()
