#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from abc import ABC
from typing import Final, Set, final

import dagger
from base_images import common, errors, sanity_checks


class PythonBase(common.BaseBaseImage):
    """
    This enum declares the Python base images that can be use to build our own base image for python.
    We use the image digest (the a sha256) to ensure that the image is not changed for reproducibility.
    """

    PYTHON_3_9_18 = {
        # https://hub.docker.com/layers/library/python/3.9.18-slim-bookworm/images/sha256-3b4e3a36cce74c444b333a26958d65d08b0ded00869f1557faffe8d131a0bdc6
        dagger.Platform("linux/amd64"): common.PlatformAwareDockerImage(
            image_name="python",
            tag="3.9.18-slim-bookworm",
            sha="3b4e3a36cce74c444b333a26958d65d08b0ded00869f1557faffe8d131a0bdc6",
            platform=dagger.Platform("linux/amd64"),
        ),
        # x86_64 and amd64 are the same platform, they'll use the same image
        # https://hub.docker.com/layers/library/python/3.9.18-slim-bookworm/images/sha256-3b4e3a36cce74c444b333a26958d65d08b0ded00869f1557faffe8d131a0bdc6
        dagger.Platform("linux/x86_64"): common.PlatformAwareDockerImage(
            image_name="python",
            tag="3.9.18-slim-bookworm",
            sha="3b4e3a36cce74c444b333a26958d65d08b0ded00869f1557faffe8d131a0bdc6",
            platform=dagger.Platform("linux/amd64"),
        ),
        # https://hub.docker.com/layers/library/python/3.9.18-slim-bookworm/images/sha256-ac1eb5caf138ab249f57f2d19666d8d55f25449e3408c2630479523c3537c0f1
        dagger.Platform("linux/arm64"): common.PlatformAwareDockerImage(
            image_name="python",
            tag="3.9.18-slim-bookworm",
            sha="ac1eb5caf138ab249f57f2d19666d8d55f25449e3408c2630479523c3537c0f1",
            platform=dagger.Platform("linux/arm64"),
        ),
    }


class AirbytePythonConnectorBaseImage(common.AirbyteConnectorBaseImage, ABC):
    """An abstract class that represents an Airbyte Python base image."""

    image_name: Final[str] = "airbyte-python-connector-base"
    pip_cache_name: Final[str] = "pip-cache"
    expected_env_vars: Set[str] = {
        "PYTHON_VERSION",
        "PYTHON_PIP_VERSION",
        "PYTHON_GET_PIP_SHA256",
        "PYTHON_GET_PIP_URL",
        "HOME",
        "PATH",
        "LANG",
        "GPG_KEY",
        "OTEL_EXPORTER_OTLP_TRACES_PROTOCOL",
        "PYTHON_SETUPTOOLS_VERSION",
        "OTEL_TRACES_EXPORTER",
        "OTEL_TRACE_PARENT",
        "TRACEPARENT",
    }

    @final
    def __init_subclass__(cls) -> None:
        if not cls.__base__ == AirbytePythonConnectorBaseImage:
            raise errors.BaseImageVersionError(
                f"AirbytePythonConnectorBaseImage subclasses must directly inherit from AirbytePythonConnectorBaseImage. {cls.__name__} does not."
            )
        return super().__init_subclass__()

    @staticmethod
    async def run_sanity_checks(base_image_version: common.AirbyteConnectorBaseImage):
        await common.AirbyteConnectorBaseImage.run_sanity_checks(base_image_version)
        await AirbytePythonConnectorBaseImage.check_env_vars(base_image_version)

    async def run_sanity_checks_for_version(self):
        await common.AirbyteConnectorBaseImage.run_sanity_checks(self)
        await AirbytePythonConnectorBaseImage.check_env_vars(self)
        return await super().run_sanity_checks_for_version()

    @staticmethod
    async def check_env_vars(base_image_version: common.AirbyteConnectorBaseImage):
        """Checks that the expected environment variables are set on the base image.
        The expected_env_vars were set on all our certified python connectors that were not using this base image
        We want to make sure that they are still set on all our connectors to avoid breaking changes.

        Args:
            base_image_version (AirbyteConnectorBaseImage): The base image version on which the sanity checks should run.

        Raises:
            errors.SanityCheckError: Raised if a sanity check fails: the printenv command could not be executed or an expected variable is not set.
        """
        for expected_env_var in AirbytePythonConnectorBaseImage.expected_env_vars:
            await sanity_checks.check_env_var_with_printenv(base_image_version.container, expected_env_var)
