#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

import docker  # type: ignore
from connector_ops.utils import Connector  # type: ignore
from dagger import Container, ExecError, Platform, QueryError
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.helpers.utils import export_container_to_tarball
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from typing import Any


def apply_airbyte_docker_labels(connector_container: Container, connector: Connector) -> Container:
    return connector_container.with_label("io.airbyte.version", connector.metadata["dockerImageTag"]).with_label(
        "io.airbyte.name", connector.metadata["dockerRepository"]
    )


class BuildConnectorImagesBase(Step, ABC):
    """
    A step to build connector images for a set of platforms.
    """

    context: ConnectorContext

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
                connector_container = await self._build_connector(platform, *args)
                connector_container = apply_airbyte_docker_labels(connector_container, self.context.connector)
                try:
                    await connector_container.with_exec(["spec"], use_entrypoint=True)
                except ExecError as e:
                    return StepResult(
                        step=self,
                        status=StepStatus.FAILURE,
                        stderr=str(e),
                        stdout=f"Failed to run the spec command on the connector container for platform {platform}.",
                        exc_info=e,
                    )
                build_results_per_platform[platform] = connector_container
            except QueryError as e:
                return StepResult(
                    step=self, status=StepStatus.FAILURE, stderr=f"Failed to build connector image for platform {platform}: {e}"
                )
        success_message = (
            f"The {self.context.connector.technical_name} docker image "
            f"was successfully built for platform(s) {', '.join(self.build_platforms)}"
        )
        return StepResult(step=self, status=StepStatus.SUCCESS, stdout=success_message, output=build_results_per_platform)

    async def _build_connector(self, platform: Platform, *args: Any, **kwargs: Any) -> Container:
        """Implement the generation of the image for the platform and return the corresponding container.

        Returns:
            Container: The container to package as a docker image for this platform.
        """
        raise NotImplementedError("`BuildConnectorImagesBase`s must define a '_build_connector' attribute.")


class LoadContainerToLocalDockerHost(Step):
    context: ConnectorContext

    def __init__(self, context: ConnectorContext, containers: dict[Platform, Container], image_tag: str = "dev") -> None:
        super().__init__(context)
        self.image_tag = image_tag
        self.containers = containers

    def _generate_dev_tag(self, platform: Platform, multi_platforms: bool) -> str:
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

    async def _run(self) -> StepResult:
        loaded_images = []
        image_sha = None
        multi_platforms = len(self.containers) > 1
        for platform, container in self.containers.items():
            _, exported_tar_path = await export_container_to_tarball(self.context, container, platform)
            if not exported_tar_path:
                return StepResult(
                    step=self,
                    status=StepStatus.FAILURE,
                    stderr=f"Failed to export the connector image {self.image_name}:{self.image_tag} to a tarball.",
                )
            try:
                client = docker.from_env()
                image_tag = self._generate_dev_tag(platform, multi_platforms)
                full_image_name = f"{self.image_name}:{image_tag}"
                with open(exported_tar_path, "rb") as tarball_content:
                    new_image = client.images.load(tarball_content.read())[0]
                    new_image.tag(self.image_name, tag=image_tag)
                    image_sha = new_image.id
                    loaded_images.append(full_image_name)
            except docker.errors.DockerException as e:
                return StepResult(
                    step=self, status=StepStatus.FAILURE, stderr=f"Something went wrong while interacting with the local docker client: {e}"
                )

        return StepResult(
            step=self, status=StepStatus.SUCCESS, stdout=f"Loaded image {','.join(loaded_images)} to your Docker host ({image_sha})."
        )
