#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares all the airbyte python connector base image for version 1.
Please create a v2.py module if you want to declare a new major version.
"""
from __future__ import annotations

from typing import Final, Type, final

import dagger
from base_images import common, sanity_checks
from base_images.python import AirbytePythonConnectorBaseImage, PythonBase


class _1_0_0(AirbytePythonConnectorBaseImage):

    base_base_image: Final[PythonBase] = PythonBase.PYTHON_3_9_18

    changelog_entry: Final[
        str
    ] = "Declare our first base image version. It uses Python 3.9.18 on a Debian 11 (Bookworm) system with Pip 23.2.1 and UTC timezone."

    run_previous_version_sanity_checks = False

    @property
    def container(self) -> dagger.Container:
        pip_cache_volume: dagger.CacheVolume = self.dagger_client.cache_volume(AirbytePythonConnectorBaseImage.pip_cache_name)

        return (
            self.base_container.with_mounted_cache("/root/.cache/pip", pip_cache_volume)
            # Set the timezone to UTC
            .with_exec(["ln", "-snf", "/usr/share/zoneinfo/Etc/UTC", "/etc/localtime"])
            # Upgrade pip to the expected version
            .with_exec(["pip", "install", "--upgrade", "pip==23.2.1"])
        )

    @final
    @staticmethod
    async def run_sanity_checks(base_image_version: common.AirbyteConnectorBaseImage):
        await sanity_checks.check_timezone_is_utc(base_image_version.container)
        await sanity_checks.check_a_command_is_available_using_version_option(base_image_version.container, "bash")
        await sanity_checks.check_python_version(base_image_version.container, "3.9.18")
        await sanity_checks.check_pip_version(base_image_version.container, "23.2.1")

    def get_previous_version(self) -> Type[AirbytePythonConnectorBaseImage]:
        return AirbytePythonConnectorBaseImage


class _1_1_0(AirbytePythonConnectorBaseImage):

    base_base_image: Final[PythonBase] = PythonBase.PYTHON_3_9_18

    changelog_entry: Final[str] = "Install poetry 1.6.1"

    run_previous_version_sanity_checks = True

    @property
    def container(self) -> dagger.Container:
        pip_cache_volume: dagger.CacheVolume = self.dagger_client.cache_volume(AirbytePythonConnectorBaseImage.pip_cache_name)
        return (
            self.base_container.with_mounted_cache("/root/.cache/pip", pip_cache_volume)
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

    @final
    @staticmethod
    async def run_sanity_checks(base_image_version: common.AirbyteConnectorBaseImage):
        await sanity_checks.check_poetry_version(base_image_version.container, "1.6.1")


# DECLARE NEW BASE IMAGE VERSIONS BELOW THIS LINE
# class _1_1_1(AirbytePythonConnectorBaseImage):

# Breaking version should be declared in a v2 module.
