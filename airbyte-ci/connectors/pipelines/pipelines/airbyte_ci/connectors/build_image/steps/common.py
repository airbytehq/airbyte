#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import subprocess
from abc import ABC
from typing import TYPE_CHECKING

import docker  # type: ignore
from base_images.bases import AirbyteConnectorBaseImage  # type: ignore
from click import UsageError
from connector_ops.utils import Connector  # type: ignore

from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.helpers.utils import export_container_to_tarball, sh_dash_c
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    T = TypeVar("T", bound="BuildConnectorImagesBase")


def apply_airbyte_docker_labels(image_name: str, connector: Connector) -> str:
    """
    Apply Airbyte Docker labels to an image using docker build --label.
    Returns the same image name since labels are applied during build.
    """
    return image_name


class BuildConnectorImagesBase(Step, ABC):
    """
    A step to build connector images for a set of platforms.
    """

    context: ConnectorContext
    USER = AirbyteConnectorBaseImage.USER

    @property
    def title(self) -> str:
        return f"Build {self.context.connector.technical_name} docker image for platform(s) {', '.join(self.build_platforms)}"

    def __init__(self, context: ConnectorContext) -> None:
        self.build_platforms = context.targeted_platforms
        super().__init__(context)

    async def _run(self, *args: Any) -> StepResult:
        build_results_per_platform = {}
        for platform in self.build_platforms:
            try:
                image_name = await self._build_connector(platform, *args)
                image_name = apply_airbyte_docker_labels(image_name, self.context.connector)
                
                cmd = ["docker", "run", "--rm", image_name, "spec"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    return StepResult(
                        step=self,
                        status=StepStatus.FAILURE,
                        stderr=f"Failed to run spec on connector container for platform {platform}: {result.stderr}",
                    )
                build_results_per_platform[platform] = image_name
            except Exception as e:
                return StepResult(
                    step=self, status=StepStatus.FAILURE, stderr=f"Failed to build connector image for platform {platform}: {e}"
                )
        success_message = (
            f"The {self.context.connector.technical_name} docker image "
            f"was successfully built for platform(s) {', '.join(self.build_platforms)}"
        )
        return StepResult(step=self, status=StepStatus.SUCCESS, stdout=success_message, output=build_results_per_platform)

    async def _build_connector(self, platform: str, *args: Any, **kwargs: Any) -> str:
        """Implement the generation of the image for the platform and return the corresponding image name.

        Returns:
            str: The image name for this platform.
        """
        raise NotImplementedError("`BuildConnectorImagesBase`s must define a '_build_connector' attribute.")

    @classmethod
    async def get_image_user(cls: Type[T], base_image_name: str) -> str:
        """If the base image in use has a user named 'airbyte', we will use it as the user for the connector image.

        Args:
            base_image_name (str): The base image name to check.

        Returns:
            str: The user to use for the connector image.
        """
        cmd = ["docker", "run", "--rm", base_image_name, "sh", "-c", "cut -d: -f1 /etc/passwd | sort | uniq"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            users = result.stdout.splitlines()
            if cls.USER in users:
                return cls.USER
        return "root"


class LoadContainerToLocalDockerHost(Step):
    context: ConnectorContext

    def __init__(self, context: ConnectorContext, image_tag: str = "dev") -> None:
        super().__init__(context)
        self.image_tag = image_tag

    def _generate_dev_tag(self, platform: str, multi_platforms: bool) -> str:
        """
        When building for multiple platforms, we need to tag the image with the platform name.
        There's no way to locally build a multi-arch image, so we need to tag the image with the platform name when the user passed multiple architecture options.
        """
        return f"{self.image_tag}-{platform.replace('/', '-')}" if multi_platforms else self.image_tag

    @property
    def title(self) -> str:
        return f"Load {self.image_name}:{self.image_tag} to the local docker host."

    @property
    def image_name(self) -> str:
        return f"airbyte/{self.context.connector.technical_name}"

    async def _run(self, images: dict[str, str]) -> StepResult:
        loaded_images = []
        image_sha = None
        multi_platforms = len(images) > 1
        for platform, image_name in images.items():
            try:
                client = docker.from_env()
                image_tag = self._generate_dev_tag(platform, multi_platforms)
                full_image_name = f"{self.image_name}:{image_tag}"
                
                image = client.images.get(image_name)
                image.tag(self.image_name, tag=image_tag)
                image_sha = image.id
                loaded_images.append(full_image_name)
            except Exception as e:
                return StepResult(
                    step=self, status=StepStatus.FAILURE, stderr=f"Something went wrong while interacting with the local docker client: {e}"
                )

        return StepResult(
            step=self, status=StepStatus.SUCCESS, stdout=f"Loaded image {','.join(loaded_images)} to your Docker host ({image_sha})."
        )
