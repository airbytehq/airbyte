#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import subprocess
from pathlib import Path
from typing import Any

from pipelines.airbyte_ci.connectors.build_image.steps.common import BuildConnectorImagesBase
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.dagger.actions.python.common import apply_python_development_overrides, with_python_connector_installed
from pipelines.models.steps import StepResult


class BuildConnectorImages(BuildConnectorImagesBase):
    """
    A step to build a Python connector image.
    A spec command is run on the container to validate it was built successfully.
    """

    context: ConnectorContext
    PATH_TO_INTEGRATION_CODE = "/airbyte/integration_code"

    async def _build_connector(self, platform: str, *args: Any) -> str:
        if (
            "connectorBuildOptions" in self.context.connector.metadata
            and "baseImage" in self.context.connector.metadata["connectorBuildOptions"]
        ):
            return await self._build_from_base_image(platform)
        else:
            return await self._build_from_dockerfile(platform)

    def _get_base_container(self, platform: str) -> str:
        base_image_name = self.context.connector.metadata["connectorBuildOptions"]["baseImage"]
        self.logger.info(f"Building connector from base image {base_image_name}")
        return base_image_name

    async def _create_builder_container(self, base_image_name: str, user: str) -> str:
        """Pre install the connector dependencies in a builder container.

        Args:
            base_image_name (str): The base image name to use to build the connector.
            user (str): The user to use in the container.
        Returns:
            str: The builder image name, with installed dependencies.
        """
        return base_image_name

    async def _build_from_base_image(self, platform: str) -> str:
        """Build the connector container using the base image defined in the metadata, in the connectorBuildOptions.baseImage field.

        Returns:
            str: The connector image name built from the base image.
        """
        self.logger.info(f"Building connector from base image in metadata for {platform}")
        base_image_name = self._get_base_container(platform)
        
        docker_images_dir = Path(__file__).parent.parent.parent.parent.parent.parent.parent / "docker-images"
        dockerfile_path = docker_images_dir / "Dockerfile.python-connector"
        
        image_name = f"airbyte/{self.context.connector.technical_name}:dev-{platform.replace('/', '-')}"
        
        cmd = [
            "docker", "build",
            "--platform", f"linux/{platform}",
            "--file", str(dockerfile_path),
            "--build-arg", f"BASE_IMAGE={base_image_name}",
            "--build-arg", f"CONNECTOR_NAME={self.context.connector.technical_name}",
            "--build-arg", "EXTRA_PREREQS_SCRIPT=",
            "--tag", image_name,
            str(self.context.connector.code_directory)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to build Python connector: {result.stderr}")
            
        return image_name

    async def _build_from_dockerfile(self, platform: str) -> str:
        """Build the connector container using its Dockerfile.

        Returns:
            str: The connector image name built from its Dockerfile.
        """
        self.logger.warn(
            "This connector is built from its Dockerfile. This is now deprecated. Please set connectorBuildOptions.baseImage metadata field to use our new build process."
        )
        
        dockerfile_path = self.context.connector.code_directory / "Dockerfile"
        if not dockerfile_path.exists():
            raise FileNotFoundError(f"Dockerfile not found at {dockerfile_path}")

        image_name = f"airbyte/{self.context.connector.technical_name}:dev-{platform.replace('/', '-')}"
        
        cmd = [
            "docker", "build",
            "--platform", f"linux/{platform}",
            "--tag", image_name,
            str(self.context.connector.code_directory)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to build connector from Dockerfile: {result.stderr}")
            
        return image_name


async def run_connector_build(context: ConnectorContext) -> StepResult:
    return await BuildConnectorImages(context).run()
