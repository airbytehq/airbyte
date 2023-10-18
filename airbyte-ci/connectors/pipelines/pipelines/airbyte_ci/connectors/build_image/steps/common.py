#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import List, Tuple

import docker
from dagger import Container, ExecError, Platform, QueryError
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.consts import BUILD_PLATFORMS
from pipelines.helpers.utils import export_container_to_tarball
from pipelines.models.steps import Step, StepResult, StepStatus


class BuildConnectorImagesBase(Step, ABC):
    """
    A step to build connector images for a set of platforms.
    """

    @property
    def title(self):
        return f"Build {self.context.connector.technical_name} docker image for platform(s) {', '.join(self.build_platforms)}"

    def __init__(self, context: ConnectorContext, *build_platforms: List[Platform]) -> None:
        self.build_platforms = build_platforms if build_platforms else BUILD_PLATFORMS
        super().__init__(context)

    async def _run(self, *args) -> StepResult:
        build_results_per_platform = {}
        for platform in self.build_platforms:
            try:
                connector = await self._build_connector(platform, *args)
                try:
                    await connector.with_exec(["spec"])
                except ExecError:
                    return StepResult(
                        self, StepStatus.FAILURE, stderr=f"Failed to run spec on the connector built for platform {platform}."
                    )
                build_results_per_platform[platform] = connector
            except QueryError as e:
                return StepResult(self, StepStatus.FAILURE, stderr=f"Failed to build connector image for platform {platform}: {e}")
        success_message = (
            f"The {self.context.connector.technical_name} docker image "
            f"was successfully built for platform(s) {', '.join(self.build_platforms)}"
        )
        return StepResult(self, StepStatus.SUCCESS, stdout=success_message, output_artifact=build_results_per_platform)

    async def _build_connector(self, platform: Platform, *args) -> Container:
        """Implement the generation of the image for the platform and return the corresponding container.

        Returns:
            Container: The container to package as a docker image for this platform.
        """
        raise NotImplementedError("`BuildConnectorImagesBase`s must define a '_build_connector' attribute.")


class LoadContainerToLocalDockerHost(Step):
    IMAGE_TAG = "dev"

    def __init__(self, context: ConnectorContext, platform: Platform, containers: dict[Platform, Container]) -> None:
        super().__init__(context)
        self.platform = platform
        self.container = containers[platform]

    @property
    def title(self):
        return f"Load {self.image_name}:{self.IMAGE_TAG} for platform {self.platform} to the local docker host."

    @property
    def image_name(self) -> Tuple:
        return f"airbyte/{self.context.connector.technical_name}"

    async def _run(self) -> StepResult:
        _, exported_tarball_path = await export_container_to_tarball(self.context, self.container)
        client = docker.from_env()
        try:
            with open(exported_tarball_path, "rb") as tarball_content:
                new_image = client.images.load(tarball_content.read())[0]
            new_image.tag(self.image_name, tag=self.IMAGE_TAG)
            return StepResult(self, StepStatus.SUCCESS)
        except ConnectionError:
            return StepResult(self, StepStatus.FAILURE, stderr="The connection to the local docker host failed.")
