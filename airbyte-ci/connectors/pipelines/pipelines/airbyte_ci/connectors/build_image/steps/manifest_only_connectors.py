#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import subprocess
from pathlib import Path
from typing import Any

from pydash.objects import get  # type: ignore

from pipelines.airbyte_ci.connectors.build_image.steps.common import BuildConnectorImagesBase
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.consts import COMPONENTS_FILE_PATH, MANIFEST_FILE_PATH
from pipelines.dagger.actions.python.common import apply_python_development_overrides
from pipelines.models.steps import StepResult


class BuildConnectorImages(BuildConnectorImagesBase):
    """
    A step to build a manifest only connector image.
    A spec command is run on the container to validate it was built successfully.
    """

    context: ConnectorContext
    PATH_TO_INTEGRATION_CODE = "/airbyte/integration_code"

    async def _build_connector(self, platform: str, *args: Any) -> str:
        baseImage = get(self.context.connector.metadata, "connectorBuildOptions.baseImage")
        if not baseImage:
            raise ValueError("connectorBuildOptions.baseImage is required to build a manifest only connector.")

        return await self._build_from_base_image(platform)

    def _get_base_container(self, platform: str) -> str:
        base_image_name = get(self.context.connector.metadata, "connectorBuildOptions.baseImage")
        self.logger.info(f"Building manifest connector from base image {base_image_name}")
        return base_image_name

    async def _build_from_base_image(self, platform: str) -> str:
        """Build the connector container using the base image defined in the metadata, in the connectorBuildOptions.baseImage field.

        Returns:
            str: The connector image name built from the base image.
        """
        self.logger.info(f"Building connector from base image in metadata for {platform}")
        base_image_name = self._get_base_container(platform)
        
        docker_images_dir = Path(__file__).parent.parent.parent.parent.parent.parent.parent / "docker-images"
        dockerfile_path = docker_images_dir / "Dockerfile.manifest-only-connector"
        
        image_name = f"airbyte/{self.context.connector.technical_name}:dev-{platform.replace('/', '-')}"
        
        connector_snake_name = self.context.connector.technical_name.replace("-", "_")
        
        cmd = [
            "docker", "build",
            "--platform", f"linux/{platform}",
            "--file", str(dockerfile_path),
            "--build-arg", f"BASE_IMAGE={base_image_name}",
            "--build-arg", f"CONNECTOR_SNAKE_NAME={connector_snake_name}",
            "--build-arg", f"CONNECTOR_NAME={self.context.connector.technical_name}",
            "--build-arg", f"CONNECTOR_VERSION={self.context.connector.metadata.get('dockerImageTag', 'dev')}",
            "--tag", image_name,
            str(self.context.connector.code_directory)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to build manifest-only connector: {result.stderr}")
            
        return image_name


async def run_connector_build(context: ConnectorContext) -> StepResult:
    return await BuildConnectorImages(context).run()
