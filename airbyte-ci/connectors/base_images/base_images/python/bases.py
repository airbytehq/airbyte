#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Final

import dagger
from base_images import bases, published_image
from base_images import sanity_checks as base_sanity_checks
from base_images.python import sanity_checks as python_sanity_checks
from base_images.root_images import PYTHON_3_9_18


class AirbytePythonConnectorBaseImage(bases.AirbyteConnectorBaseImage):

    root_image: Final[published_image.PublishedImage] = PYTHON_3_9_18
    repository: Final[str] = "airbyte/python-connector-base"

    pip_cache_name: Final[str] = "pip-cache"

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

        await base_sanity_checks.check_timezone_is_utc(container)
        await base_sanity_checks.check_a_command_is_available_using_version_option(container, "bash")
        await python_sanity_checks.check_python_version(container, "3.9.18")
        await python_sanity_checks.check_pip_version(container, "23.2.1")
        await python_sanity_checks.check_poetry_version(container, "1.6.1")
        await python_sanity_checks.check_python_image_has_expected_env_vars(container)
