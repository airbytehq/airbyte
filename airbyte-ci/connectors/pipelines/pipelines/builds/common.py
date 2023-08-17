#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC

import docker
from dagger import Container, Platform
from pipelines.bases import Step, StepResult, StepStatus
from pipelines.consts import BUILD_PLATFORMS
from pipelines.contexts import ConnectorContext
from pipelines.utils import export_container_to_tarball


class BuildConnectorImageBase(Step, ABC):
    @property
    def title(self):
        return f"Build {self.context.connector.technical_name} docker image for platform {self.build_platform}"

    def __init__(self, context: ConnectorContext, build_platform: Platform) -> None:
        self.build_platform = build_platform
        super().__init__(context)


class BuildImageForAllPlatformsBase(Step, ABC):

    ALL_PLATFORMS = BUILD_PLATFORMS

    title = f"Build image for {BUILD_PLATFORMS}"

    def get_success_result(self, build_results_per_platform: dict[Platform, Container]) -> StepResult:
        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout="The image was successfully built for all platforms.",
            output_artifact=build_results_per_platform,
        )


class LoadContainerToLocalDockerHost(Step):
    IMAGE_TAG = "dev"

    def __init__(self, context: ConnectorContext, container: Container, image_name: str) -> None:
        super().__init__(context)
        self.container = container
        self.image_name = image_name

    @property
    def title(self):
        return f"Load {self.image_name}:{self.IMAGE_TAG} to the local docker host."

    async def _run(self) -> StepResult:
        tar_file_name = f"{self.image_name.replace('/', '-')}-{self.IMAGE_TAG}-{self.context.git_revision}.tar"
        _, exported_tarball_path = await export_container_to_tarball(self.context, self.container, tar_file_name=tar_file_name)
        client = docker.from_env()
        try:
            with open(exported_tarball_path, "rb") as tarball_content:
                new_image = client.images.load(tarball_content.read())[0]
            new_image.tag(self.image_name, tag=self.IMAGE_TAG)
            return StepResult(self, StepStatus.SUCCESS)
        except ConnectionError:
            return StepResult(self, StepStatus.FAILURE, stderr="The connection to the local docker host failed.")
