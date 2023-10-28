#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dagger import Container, Platform
from pipelines.airbyte_ci.connectors.build_image.steps import build_customization
from pipelines.airbyte_ci.connectors.build_image.steps.common import BuildConnectorImagesBase
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.dagger.actions.python.common import apply_python_development_overrides, with_python_connector_installed
from pipelines.models.steps import StepResult


class BuildConnectorImages(BuildConnectorImagesBase):
    """
    A step to build a Python connector image.
    A spec command is run on the container to validate it was built successfully.
    """

    PATH_TO_INTEGRATION_CODE = "/airbyte/integration_code"

    async def _build_connector(self, platform: Platform):
        if (
            "connectorBuildOptions" in self.context.connector.metadata
            and "baseImage" in self.context.connector.metadata["connectorBuildOptions"]
        ):
            return await self._build_from_base_image(platform)
        else:
            return await self._build_from_dockerfile(platform)

    def _get_base_container(self, platform: Platform) -> Container:
        base_image_name = self.context.connector.metadata["connectorBuildOptions"]["baseImage"]
        self.logger.info(f"Building connector from base image {base_image_name}")
        return self.dagger_client.container(platform=platform).from_(base_image_name)

    async def _create_builder_container(self, base_container: Container) -> Container:
        """Pre install the connector dependencies in a builder container.

        Args:
            base_container (Container): The base container to use to build the connector.

        Returns:
            Container: The builder container, with installed dependencies.
        """
        ONLY_PYTHON_BUILD_FILES = ["setup.py", "requirements.txt", "pyproject.toml", "poetry.lock"]
        builder = await with_python_connector_installed(
            self.context,
            base_container,
            str(self.context.connector.code_directory),
            include=ONLY_PYTHON_BUILD_FILES,
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
        main_file_name = build_customization.get_main_file_name(self.context.connector)

        builder = await self._create_builder_container(customized_base)

        # The snake case name of the connector corresponds to the python package name of the connector
        # We want to mount it to the container under PATH_TO_INTEGRATION_CODE/connector_snake_case_name
        connector_snake_case_name = self.context.connector.technical_name.replace("-", "_")

        connector_container = (
            # copy python dependencies from builder to connector container
            customized_base.with_directory("/usr/local", builder.directory("/usr/local"))
            .with_workdir(self.PATH_TO_INTEGRATION_CODE)
            .with_file(main_file_name, (await self.context.get_connector_dir(include=main_file_name)).file(main_file_name))
            .with_directory(
                connector_snake_case_name,
                (await self.context.get_connector_dir(include=connector_snake_case_name)).directory(connector_snake_case_name),
            )
            .with_env_variable("AIRBYTE_ENTRYPOINT", " ".join(entrypoint))
            .with_entrypoint(entrypoint)
            .with_label("io.airbyte.version", self.context.connector.metadata["dockerImageTag"])
            .with_label("io.airbyte.name", self.context.connector.metadata["dockerRepository"])
        )
        customized_connector = await build_customization.post_install_hooks(self.context.connector, connector_container, self.logger)
        return customized_connector

    async def _build_from_dockerfile(self, platform: Platform) -> Container:
        """Build the connector container using its Dockerfile.

        Returns:
            Container: The connector container built from its Dockerfile.
        """
        self.logger.warn(
            "This connector is built from its Dockerfile. This is now deprecated. Please set connectorBuildOptions.baseImage metadata field to use our new build process."
        )
        container = self.dagger_client.container(platform=platform).build(await self.context.get_connector_dir())
        container = await apply_python_development_overrides(self.context, container)
        return container


async def run_connector_build(context: ConnectorContext) -> StepResult:
    return await BuildConnectorImages(context).run()
