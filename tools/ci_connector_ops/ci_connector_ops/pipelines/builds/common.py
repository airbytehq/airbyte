#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC
from typing import Tuple

import docker
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.pipelines.utils import export_container_to_tarball
from dagger import Container, Platform


class BuildConnectorImageBase(Step, ABC):
    @property
    def title(self):
        return f"Build {self.context.connector.technical_name} docker image for platform {self.build_platform}"

    def __init__(self, context: ConnectorContext, build_platform: Platform) -> None:
        self.build_platform = build_platform
        super().__init__(context)


class LoadContainerToLocalDockerHost(Step):
    IMAGE_TAG = "dev"

    def __init__(self, context: ConnectorContext, container: Container) -> None:
        super().__init__(context)
        self.container = container

    @property
    def title(self):
        return f"Load {self.image_name}:{self.IMAGE_TAG} to the local docker host."

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
