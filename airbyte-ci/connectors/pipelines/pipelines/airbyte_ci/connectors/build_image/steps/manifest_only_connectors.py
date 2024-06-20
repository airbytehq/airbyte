#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any

from dagger import Container, Platform
from pipelines.airbyte_ci.connectors.build_image.steps import build_customization
from pipelines.airbyte_ci.connectors.build_image.steps.common import BuildConnectorImagesBase
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.dagger.actions.python.common import with_python_connector_installed
from pipelines.models.steps import StepResult
from pydash.objects import get


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

    async def _create_builder_container(self, base_container: Container) -> Container:
        """Pre install the connector dependencies in a builder container.

        Args:
            base_container (Container): The base container to use to build the connector.

        Returns:
            Container: The builder container, with installed dependencies.
        """
        ONLY_BUILD_FILES = ["pyproject.toml", "poetry.lock", "poetry.toml", "setup.py", "requirements.txt", "README.md"]

        builder = await with_python_connector_installed(
            self.context, base_container, str(self.context.connector.code_directory), install_root_package=False, include=ONLY_BUILD_FILES
        )
        return builder

    async def _build_from_base_image(self, platform: Platform) -> Container:
        """Build the connector container using the base image defined in the metadata, in the connectorBuildOptions.baseImage field.

        Returns:
            Container: The connector container built from the base image.
        """
        self.logger.info(f"Building connector from base image in metadata for {platform}")
        base = self._get_base_container(platform)

        customized_base = await build_customization.pre_install_hooks(self.context.connector, base, self.logger)
        entrypoint = build_customization.get_entrypoint(self.context.connector)

        manifest_file_name = "manifest.yaml"

        connector_container = (
            customized_base.with_file(
                f"source_declarative_manifest/{manifest_file_name}",
                (await self.context.get_connector_dir(include=[manifest_file_name])).file(manifest_file_name),
            )
            .with_env_variable("AIRBYTE_ENTRYPOINT", " ".join(entrypoint))
            .with_entrypoint(entrypoint)
            .with_label("io.airbyte.version", self.context.connector.metadata["dockerImageTag"])
            .with_label("io.airbyte.name", self.context.connector.metadata["dockerRepository"])
        )
        customized_connector = await build_customization.post_install_hooks(self.context.connector, connector_container, self.logger)
        return customized_connector


async def run_connector_build(context: ConnectorContext) -> StepResult:
    return await BuildConnectorImages(context).run()
