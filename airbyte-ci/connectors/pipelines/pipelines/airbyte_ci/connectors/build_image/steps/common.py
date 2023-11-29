#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from abc import ABC
from typing import List, Optional, Tuple

import docker
from dagger import Container, ExecError, Platform, QueryError
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.helpers.utils import export_containers_to_tarball
from pipelines.models.steps import Step, StepResult, StepStatus


class BuildConnectorImagesBase(Step, ABC):
    """
    A step to build connector images for a set of platforms.
    """

    @property
    def title(self):
        return f"Build {self.context.connector.technical_name} docker image for platform(s) {', '.join(self.build_platforms)}"

    def __init__(self, context: ConnectorContext) -> None:
        self.build_platforms: List[Platform] = context.targeted_platforms
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
    def __init__(self, context: ConnectorContext, containers: dict[Platform, Container], image_tag: Optional[str] = "dev") -> None:
        super().__init__(context)
        self.image_tag = image_tag
        self.containers = containers

    @property
    def title(self):
        return f"Load {self.image_name}:{self.image_tag} to the local docker host."

    @property
    def image_name(self) -> Tuple:
        return f"airbyte/{self.context.connector.technical_name}"

    async def _run(self) -> StepResult:
        container_variants = list(self.containers.values())
        _, exported_tar_path = await export_containers_to_tarball(self.context, container_variants)
        if not exported_tar_path:
            return StepResult(
                self,
                StepStatus.FAILURE,
                stderr=f"Failed to export the connector image {self.image_name}:{self.image_tag} to a tarball.",
            )
        try:
            client = docker.from_env()
            response = client.api.import_image_from_file(str(exported_tar_path), repository=self.image_name, tag=self.image_tag)
            try:
                image_sha = json.loads(response)["status"]
            except (json.JSONDecodeError, KeyError):
                return StepResult(
                    self,
                    StepStatus.FAILURE,
                    stderr=f"Failed to import the connector image {self.image_name}:{self.image_tag} to your Docker host: {response}",
                )
            return StepResult(
                self, StepStatus.SUCCESS, stdout=f"Loaded image {self.image_name}:{self.image_tag} to your Docker host ({image_sha})."
            )
        except docker.errors.DockerException as e:
            return StepResult(self, StepStatus.FAILURE, stderr=f"Something went wrong while interacting with the local docker client: {e}")
