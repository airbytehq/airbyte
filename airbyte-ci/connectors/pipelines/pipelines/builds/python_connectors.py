#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

from base_images import GLOBAL_REGISTRY
from dagger import Container, QueryError
from pipelines.actions.environments import find_local_python_dependencies
from pipelines.bases import StepResult, StepStatus
from pipelines.builds.common import BuildConnectorImageBase, BuildConnectorImageForAllPlatformsBase
from pipelines.contexts import ConnectorContext


class BuildConnectorImage(BuildConnectorImageBase):
    """
    A step to build a Python connector image.
    A spec command is run on the container to validate it was built successfully.
    """

    DEFAULT_ENTRYPOINT = ["python", "/airbyte/integration_code/main.py"]
    PATH_TO_INTEGRATION_CODE = "/airbyte/integration_code"

    @property
    def _build_connector_function(self):
        if (
            "connectorBuildOptions" in self.context.connector.metadata
            and "baseImage" in self.context.connector.metadata["connectorBuildOptions"]
        ):
            return self._build_from_base_image
        else:
            return self._build_from_dockerfile

    async def _run(self) -> StepResult:
        connector: Container = await self._build_connector_function()
        try:
            return await self.get_step_result(connector.with_exec(["spec"]))
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e))

    def _get_base_container(self) -> Container:
        base_image_name = self.context.connector.metadata["connectorBuildOptions"]["baseImage"]
        BaseImageVersion = GLOBAL_REGISTRY.get_version(base_image_name)
        self.logger.info(f"Building connector from base image {base_image_name}")
        return BaseImageVersion(self.dagger_client, self.build_platform).container

    async def _provision_builder_container(self, base_container: Container) -> Container:
        """Pre install the connector dependencies in a builder container.
        If a python connectors depends on another local python connector, we need to mount its source in the container
        This occurs for the source-file-secure connector for example, which depends on source-file

        Args:
            base_container (Container): The base container to use to build the connector.

        Returns:
            Container: The builder container, with installed dependencies.
        """
        setup_dependencies_to_mount = await find_local_python_dependencies(
            self.context,
            str(self.context.connector.code_directory),
            search_dependencies_in_setup_py=True,
            search_dependencies_in_requirements_txt=False,
        )
        builder = (
            base_container.with_workdir(self.PATH_TO_INTEGRATION_CODE)
            # This env var is used in the setup.py to know if it is run in a container or not
            # When run in a container, we need to mount the local dependencies to ./local_dependencies
            # The setup.py reacts to this env var and use the /local_dependencies path instead of the normal local path
            .with_env_variable("DAGGER_BUILD", "1").with_file(
                "setup.py", (await self.context.get_connector_dir(include="setup.py")).file("setup.py")
            )
        )
        for dependency_path in setup_dependencies_to_mount:
            in_container_dependency_path = f"/local_dependencies/{Path(dependency_path).name}"
            builder = builder.with_mounted_directory(in_container_dependency_path, self.context.get_repo_dir(dependency_path))

        return builder.with_exec(["pip", "install", "--prefix=/install", "."])

    async def _build_from_base_image(self) -> Container:
        """Build the connector container using the base image defined in the metadata, in the connectorBuildOptions.baseImage field.

        Returns:
            Container: The connector container built from the base image.
        """
        base = self._get_base_container()
        builder = await self._provision_builder_container(base)
        connector_snake_case_name = self.context.connector.technical_name.replace("-", "_")

        connector_container = (
            base.with_directory("/usr/local", builder.directory("/install"))
            .with_workdir(self.PATH_TO_INTEGRATION_CODE)
            .with_file("main.py", (await self.context.get_connector_dir(include="main.py")).file("main.py"))
            .with_directory(
                connector_snake_case_name,
                (await self.context.get_connector_dir(include=connector_snake_case_name)).directory(connector_snake_case_name),
            )
            .with_env_variable("AIRBYTE_ENTRYPOINT", " ".join(self.DEFAULT_ENTRYPOINT))
            .with_entrypoint(self.DEFAULT_ENTRYPOINT)
            .with_label("io.airbyte.version", self.context.connector.metadata["dockerImageTag"])
            .with_label("io.airbyte.name", self.context.connector.metadata["dockerRepository"])
        )
        return connector_container

    async def _build_from_dockerfile(self) -> Container:
        """Build the connector container using its Dockerfile.

        Returns:
            Container: The connector container built from its Dockerfile.
        """
        self.logger.warn(
            "This connector is built from its Dockerfile. This is now deprecated. Please set connectorBuildOptions.baseImage metadata field to use or new build process."
        )
        return self.dagger_client.container(platform=self.build_platform).build(await self.context.get_connector_dir())


class BuildConnectorImageForAllPlatforms(BuildConnectorImageForAllPlatformsBase):
    """Build a Python connector image for all platforms."""

    async def _run(self) -> StepResult:
        build_results_per_platform = {}
        for platform in self.ALL_PLATFORMS:
            build_connector_step_result = await BuildConnectorImage(self.context, platform).run()
            if build_connector_step_result.status is not StepStatus.SUCCESS:
                return build_connector_step_result
            build_results_per_platform[platform] = build_connector_step_result.output_artifact
        return self.get_success_result(build_results_per_platform)


async def run_connector_build(context: ConnectorContext) -> StepResult:
    return await BuildConnectorImageForAllPlatforms(context).run()
