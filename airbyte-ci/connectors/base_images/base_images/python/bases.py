#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import Final, Set

import dagger
from base_images import common, sanity_checks
from connector_ops.utils import ConnectorLanguage  # type: ignore

from .base_bases import PYTHON_3_9_18


class AirbytePythonConnectorBaseImage(common.AirbyteConnectorBaseImage):

    compatible_languages = (ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE)
    base_base_image: Final[common.PublishedImage] = PYTHON_3_9_18
    image_name: Final[str] = "airbyte/python-connector-base"

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

    def get_container(self, platform: dagger.Platform) -> dagger.Container:
        """Returns the container used to build the base image.
        We currently use the python:3.9.18-slim-bookworm image as a base.
        We set the container system timezone to UTC.
        We then upgrade pip and install poetry.

        Args:
            platform (dagger.Platform): The platform this container should be built for.

        Returns:
            dagger.Container: The container used to build the base image.
        """
        pip_cache_volume: dagger.CacheVolume = self.dagger_client.cache_volume(AirbytePythonConnectorBaseImage.pip_cache_name)

        return (
            self.get_base_container(platform)
            .with_mounted_cache("/root/.cache/pip", pip_cache_volume)
            # Set the timezone to UTC
            .with_exec(["ln", "-snf", "/usr/share/zoneinfo/Etc/UTC", "/etc/localtime"])
            # Upgrade pip to the expected version
            .with_exec(["pip", "install", "--upgrade", "pip==23.2.1"])
            # Declare poetry specific environment variables
            .with_env_variable("POETRY_VIRTUALENVS_CREATE", "false")
            .with_env_variable("POETRY_VIRTUALENVS_IN_PROJECT", "false")
            .with_env_variable("POETRY_NO_INTERACTION", "1")
            .with_exec(["pip", "install", "poetry==1.6.1"], skip_entrypoint=True)
        )

    async def run_sanity_checks(self, platform: dagger.Platform):
        """Runs sanity checks on the base image container.
        This method is called before image publication.
        Consider it like a pre-flight check before take-off to the remote registry.

        Args:
            platform (dagger.Platform): The platform on which the sanity checks should run.
        """
        container = self.get_container(platform)
        for expected_env_var in self.expected_env_vars:
            await sanity_checks.check_env_var_with_printenv(container, expected_env_var)

        await sanity_checks.check_timezone_is_utc(container)
        await sanity_checks.check_a_command_is_available_using_version_option(container, "bash")
        await sanity_checks.check_python_version(container, "3.9.18")
        await sanity_checks.check_pip_version(container, "23.2.1")
        await sanity_checks.check_poetry_version(container, "1.6.1")
