#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch builds steps according to the connector language."""

import platform
from typing import Optional, Tuple

import docker
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.builds import java_connectors, python_connectors
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.utils import export_container_to_tarball
from ci_connector_ops.utils import ConnectorLanguage
from dagger import Container, Platform

BUILD_PLATFORMS = [Platform("linux/amd64"), Platform("linux/arm64")]
LOCAL_BUILD_PLATFORM = Platform(f"linux/{platform.machine()}")


class NoBuildStepForLanguageError(Exception):
    pass


LANGUAGE_BUILD_CONNECTOR_MAPPING = {
    ConnectorLanguage.PYTHON: python_connectors.BuildConnectorImage,
    ConnectorLanguage.LOW_CODE: python_connectors.BuildConnectorImage,
    ConnectorLanguage.JAVA: java_connectors.BuildConnectorImage,
}


async def run_connector_build(context: ConnectorTestContext) -> dict[str, Tuple[StepResult, Optional[Container]]]:
    """Build a connector according to its language and return the build result and the built container.

    Args:
        context (ConnectorTestContext): The current connector test context.

    Returns:
        dict[str, Tuple[StepResult, Optional[Container]]]: A dictionary with platform as key and a tuple of step result and built container as value.
    """
    try:
        BuildConnectorImage = LANGUAGE_BUILD_CONNECTOR_MAPPING[context.connector.language]
    except KeyError:
        raise NoBuildStepForLanguageError(f"No step to build a {context.connector.language} connector was found.")

    per_platform_containers = {}
    for build_platform in BUILD_PLATFORMS:
        per_platform_containers[build_platform] = await BuildConnectorImage(context, build_platform).run()

    return per_platform_containers


class LoadContainerToLocalDockerHost(Step):
    IMAGE_TAG = "dev"

    def __init__(self, context: ConnectorTestContext, container: Container) -> None:
        super().__init__(context)
        self.container = container

    @property
    def title(self):
        return f"Load {self.image_name}:{self.IMAGE_TAG} to local docker host."

    @property
    def image_name(self) -> Tuple:
        return f"airbyte/{self.context.connector.technical_name}"

    async def _run(self) -> StepResult:
        _, exported_tarball_path = await export_container_to_tarball(self.context, self.container)
        client = docker.from_env()
        with open(exported_tarball_path, "rb") as tarball_content:
            new_image = client.images.load(tarball_content.read())[0]
        new_image.tag(self.image_name, tag=self.IMAGE_TAG)
        return StepResult(self, StepStatus.SUCCESS)


async def load_connector_container_to_local_docker_host(context: ConnectorTestContext, connector_container: Container) -> StepResult:
    return await LoadContainerToLocalDockerHost(context, connector_container).run()
