#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares all the airbyte python connector base image for version 1.
Please create a v2.py module if you want to declare a new major version.
"""

from typing import Final

import dagger
from base_images import common, errors
from base_images.python import AirbytePythonConnectorBaseImage, PythonBase


class _1_0_0(AirbytePythonConnectorBaseImage):

    base_base_image: Final[PythonBase] = PythonBase.PYTHON_3_9

    TIMEZONE: Final[str] = "Etc/UTC"
    # This should be a final class attribute if the base_base_image attribute is Final
    EXPECTED_PYTHON_VERSION: Final[str] = "3.9.18"
    EXPECTED_PIP_VERSION: str = "23.2.1"

    changelog_entry: str = (
        "Declare our first base image version. It uses Python 3.9.18 on a Debian 11 (Bookworm) system with Pip 23.2.1 and UTC timezone."
    )

    @property
    def container(self) -> dagger.Container:
        pip_cache: dagger.CacheVolume = self.dagger_client.cache_volume("pip_cache")

        return (
            self.base_container.with_mounted_cache("/root/.cache/pip", pip_cache)
            # Set the timezone to UTC
            .with_exec(["ln", "-snf", f"/usr/share/zoneinfo/{self.TIMEZONE}", "/etc/localtime"])
            # Upgrade pip to the expected version
            .with_exec(["pip", "install", "--upgrade", "pip==23.2.1"])
        )

    @staticmethod
    async def run_sanity_checks(base_image_version: common.AirbyteConnectorBaseImage):
        await AirbytePythonConnectorBaseImage.run_sanity_checks(base_image_version)
        await _1_0_0.check_time_zone(base_image_version)
        await _1_0_0.check_bash_is_installed(base_image_version)
        await _1_0_0.check_python_version(base_image_version)
        await _1_0_0.check_pip_version(base_image_version)

    @staticmethod
    async def check_python_version(base_image_version: common.AirbyteConnectorBaseImage):
        """Checks that the python version is the expected one.

        Args:
            base_image_version (AirbyteConnectorBaseImage): The base image version on which the sanity checks should run.

        Raises:
            errors.SanityCheckError: Raised if the python --version command could not be executed or if the outputted version is not the expected one.
        """
        try:
            python_version_output: str = await base_image_version.container.with_exec(
                ["python", "--version"], skip_entrypoint=True
            ).stdout()
        except dagger.ExecError as e:
            raise errors.SanityCheckError(e)
        if python_version_output != f"Python {_1_0_0.EXPECTED_PYTHON_VERSION}\n":
            raise errors.SanityCheckError(f"unexpected python version: {python_version_output}")

    @staticmethod
    async def check_pip_version(base_image_version: common.AirbyteConnectorBaseImage):
        """Checks that the pip version is the expected one.

        Args:
            base_image_version (AirbyteConnectorBaseImage): The base image version on which the sanity checks should run.

        Raises:
            errors.SanityCheckError: Raised if the pip --version command could not be executed or if the outputted version is not the expected one.
        """
        try:
            pip_version_output: str = await base_image_version.container.with_exec(["pip", "--version"], skip_entrypoint=True).stdout()
        except dagger.ExecError as e:
            raise errors.SanityCheckError(e)
        if not pip_version_output.startswith(f"pip {_1_0_0.EXPECTED_PIP_VERSION}"):
            raise errors.SanityCheckError(f"unexpected pip version: {pip_version_output}")

    @staticmethod
    async def check_time_zone(base_image_version: common.AirbyteConnectorBaseImage):
        """We want to make sure that the system timezone is set to UTC.

        Args:
            base_image_version (AirbyteConnectorBaseImage): The base image version on which the sanity checks should run.

        Raises:
            errors.SanityCheckError: Raised if the date command could not be executed or if the outputted timezone is not UTC.
        """
        try:
            tz_output: str = await base_image_version.container.with_exec(["date"], skip_entrypoint=True).stdout()
        except dagger.ExecError as e:
            raise errors.SanityCheckError(e)
        if "UTC" not in tz_output:
            raise errors.SanityCheckError(f"unexpected timezone: {tz_output}")

    @staticmethod
    async def check_bash_is_installed(base_image_version: common.AirbyteConnectorBaseImage):
        """Bash should be installed on the base image for debugging purposes and pre/post build hooks.

        Args:
            base_image_version (AirbyteConnectorBaseImage): The base image version on which the sanity checks should run.

        Raises:
            errors.SanityCheckError: Raised if the bash --version command could not be executed.
        """
        try:
            await base_image_version.container.with_exec(["bash", "--version"], skip_entrypoint=True).stdout()
        except dagger.ExecError as e:
            raise errors.SanityCheckError(e)


class _1_1_0(_1_0_0):
    changelog_entry: str = "Install poetry 1.6.1"

    EXPECTED_POETRY_VERSION: str = "1.6.1"

    @property
    def container(self) -> dagger.Container:
        return (
            super()
            .container.with_env_variable("POETRY_VIRTUALENVS_CREATE", "false")
            .with_env_variable("POETRY_VIRTUALENVS_IN_PROJECT", "false")
            .with_env_variable("POETRY_NO_INTERACTION", "1")
            .with_exec(["pip", "install", "poetry==1.6.1"], skip_entrypoint=True)
        )

    @staticmethod
    async def run_sanity_checks(base_image_version: common.AirbyteConnectorBaseImage):
        await _1_0_0.run_sanity_checks(base_image_version)
        await _1_1_0.check_poetry_version(base_image_version, _1_1_0.EXPECTED_POETRY_VERSION)

    @staticmethod
    async def check_poetry_version(base_image_version: common.AirbyteConnectorBaseImage, expected_poetry_version: str):
        try:
            poetry_version_output: str = await base_image_version.container.with_exec(
                ["poetry", "--version"], skip_entrypoint=True
            ).stdout()
        except dagger.ExecError as e:
            raise errors.SanityCheckError(e)
        if not poetry_version_output.startswith(f"Poetry (version {expected_poetry_version})"):
            raise errors.SanityCheckError(f"unexpected poetry version: {poetry_version_output}")


# TODO: remove before release
# EXAMPLE OF A FIX
class _1_1_1(_1_1_0):
    changelog_entry = "Fix: we should use Poetry 1.6.0 instead of 1.6.1"
    EXPECTED_POETRY_VERSION: str = "1.6.0"

    @property
    def container(self) -> dagger.Container:
        return super().container.with_exec(["pip", "install", "poetry==1.6.0"], skip_entrypoint=True)

    @staticmethod
    async def run_sanity_checks(base_image_version: common.AirbyteConnectorBaseImage):
        # As this is version is a fix, we are not running _1_1_0 sanity checks because they will fail as the poetry version is different.
        await _1_0_0.run_sanity_checks(base_image_version)
        await _1_1_0.check_poetry_version(base_image_version, _1_1_1.EXPECTED_POETRY_VERSION)


# DECLARE NEW BASE IMAGE VERSIONS BELOW THIS LINE
# Non breaking version should ideally inherit from the previous version.
# class _1_1_2(_1_1_1):

# Breaking version should inherit from AirbytePythonConnectorBaseImage and be declared in a v2 module.
