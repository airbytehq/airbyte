#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import inspect
import sys
from abc import ABC
from typing import Final, Set, Type

import dagger
from base_images import common


class PythonBase(common.BaseBaseImage):
    """
    This enum declares the Python base images that can be use to build our own base image for python.
    We use the image digest (the a sha256) to ensure that the image is not changed for reproducibility.
    """

    PYTHON_3_9 = {
        dagger.Platform("linux/amd64"): common.PlatformAwareDockerImage(
            image_name="python",
            tag="3.9.18-bookworm",
            sha="40582fe697811beb7bfceef2087416336faa990fd7e24984a7c18a86d3423d58",
            platform=dagger.Platform("linux/amd64"),
        ),
        dagger.Platform("linux/arm64"): common.PlatformAwareDockerImage(
            image_name="python",
            tag="3.9.18-bookworm",
            sha="0d132e30eb9325d53c790738e5478e9abffc98b69115e7de429d7c6fc52dddac",
            platform=dagger.Platform("linux/arm64"),
        ),
    }


class AirbytePythonConnectorBaseImage(common.AirbyteConnectorBaseImage, ABC):
    """An abstract class that represents an Airbyte Python base image."""

    image_name: Final[str] = "airbyte-python-connector-base"

    EXPECTED_ENV_VARS: Set[str] = {
        "PYTHON_VERSION",
        "PYTHON_PIP_VERSION",
        "PYTHON_GET_PIP_SHA256",
        "PYTHON_GET_PIP_URL",
        "AIRBYTE_BASE_BASE_IMAGE",
        "AIRBYTE_BASE_IMAGE",
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

    async def run_sanity_checks(self):
        await super().run_sanity_checks()
        await self.check_env_vars()

    async def check_env_vars(self):
        try:
            printenv_output: str = await self.container.with_exec(["printenv"], skip_entrypoint=True).stdout()
        except dagger.ExecError as e:
            raise common.SanityCheckError("failed to run printenv.") from e
        env_vars = set([line.split("=")[0] for line in printenv_output.splitlines()])
        missing_env_vars = self.EXPECTED_ENV_VARS - env_vars
        if missing_env_vars:
            raise common.SanityCheckError(f"missing environment variables: {missing_env_vars}")


class _0_1_0(AirbytePythonConnectorBaseImage):

    base_base_image: Final[PythonBase] = PythonBase.PYTHON_3_9

    TIMEZONE: Final[str] = "Etc/UTC"
    EXPECTED_PYTHON_VERSION: str = "3.9.18"
    EXPECTED_PIP_VERSION: str = "23.2.1"

    changelog: str = (
        "Declare our first base image version. It uses Python 3.9.18 on a Debian 11 (Bookworm) system with Pip 23.2.1 and UTC timezone."
    )

    @property
    def container(self) -> dagger.Container:
        return self.base_container.with_exec(["ln", "-snf", f"/usr/share/zoneinfo/{self.TIMEZONE}", "/etc/localtime"]).with_exec(
            ["pip", "install", "--upgrade", f"pip=={self.EXPECTED_PIP_VERSION}"]
        )

    async def run_sanity_checks(self):
        await super().run_sanity_checks()
        await self.check_python_version()
        await self.check_pip_version()
        await self.check_time_zone()
        await self.check_bash_is_installed()

    async def check_python_version(self):
        try:
            python_version_output: str = await self.container.with_exec(["python", "--version"], skip_entrypoint=True).stdout()
        except dagger.ExecError as e:
            raise common.SanityCheckError("failed to run python --version.") from e
        if python_version_output != f"Python {self.EXPECTED_PYTHON_VERSION}\n":
            raise common.SanityCheckError(f"unexpected python version: {python_version_output}")

    async def check_pip_version(self):
        try:
            pip_version_output: str = await self.container.with_exec(["pip", "--version"], skip_entrypoint=True).stdout()
        except dagger.ExecError as e:
            raise common.SanityCheckError("failed to run pip --version.") from e
        if not pip_version_output.startswith(f"pip {self.EXPECTED_PIP_VERSION}"):
            raise common.SanityCheckError(f"unexpected pip version: {pip_version_output}")

    async def check_time_zone(self):
        try:
            tz_output: str = await self.container.with_exec(["date"], skip_entrypoint=True).stdout()
        except dagger.ExecError as e:
            raise common.SanityCheckError("failed to run date.") from e
        if "UTC" not in tz_output:
            raise common.SanityCheckError(f"unexpected timezone: {tz_output}")

    async def check_bash_is_installed(self):
        try:
            await self.container.with_exec(["bash", "--version"], skip_entrypoint=True).stdout()
        except dagger.ExecError as e:
            raise common.SanityCheckError("failed to run bash --version.") from e


def get_all_python_base_images() -> dict[str, Type[AirbytePythonConnectorBaseImage]]:
    """Discover the base image versions declared in the module.
    It saves us from hardcoding the list of base images version: implementing a new class should be the only step to make a new base version available.

    Returns:
        dict[str, Type[AirbytePythonConnectorBaseImage]]: A dictionary of the base image versions declared in the module, keys are base image name and tag as string.
    """
    # Reverse the order of the members so that the latest version is first
    cls_members = reversed(inspect.getmembers(sys.modules[__name__], inspect.isclass))
    return {
        cls_member.name_with_tag: cls_member
        for _, cls_member in cls_members
        if issubclass(type(cls_member), type(AirbytePythonConnectorBaseImage))
        and cls_member != AirbytePythonConnectorBaseImage
        and cls_member != ABC
    }


ALL_BASE_IMAGES = get_all_python_base_images()
