#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import importlib
import inspect
import pkgutil
from abc import ABC
from typing import Final, Set, Type

import dagger
from base_images import common, errors


class PythonBase(common.BaseBaseImage):
    """
    This enum declares the Python base images that can be use to build our own base image for python.
    We use the image digest (the a sha256) to ensure that the image is not changed for reproducibility.
    """

    PYTHON_3_9 = {
        # https://hub.docker.com/layers/library/python/3.9.18-bookworm/images/sha256-40582fe697811beb7bfceef2087416336faa990fd7e24984a7c18a86d3423d58
        dagger.Platform("linux/amd64"): common.PlatformAwareDockerImage(
            image_name="python",
            tag="3.9.18-bookworm",
            sha="40582fe697811beb7bfceef2087416336faa990fd7e24984a7c18a86d3423d58",
            platform=dagger.Platform("linux/amd64"),
        ),
        # https://hub.docker.com/layers/library/python/3.9.18-bookworm/images/sha256-0d132e30eb9325d53c790738e5478e9abffc98b69115e7de429d7c6fc52dddac
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

    @staticmethod
    async def run_sanity_checks(base_image_version: common.AirbyteConnectorBaseImage):
        await common.AirbyteConnectorBaseImage.run_sanity_checks(base_image_version)
        await AirbytePythonConnectorBaseImage.check_env_vars(base_image_version)

    @staticmethod
    async def check_env_vars(base_image_version: common.AirbyteConnectorBaseImage):
        """Checks that the expected environment variables are set on the base image.
        The EXPECTED_ENV_VARS were set on all our certified python connectors that were not using this base image
        We want to make sure that they are still set on all our connectors to avoid breaking changes.

        Args:
            base_image_version (AirbyteConnectorBaseImage): The base image version on which the sanity checks should run.

        Raises:
            errors.SanityCheckError: Raised if a sanity check fails: the printenv command could not be executed or an expected variable is not set.
        """
        try:
            printenv_output: str = await base_image_version.container.with_exec(["printenv"], skip_entrypoint=True).stdout()
        except dagger.ExecError as e:
            raise errors.SanityCheckError(e)
        env_vars = set([line.split("=")[0] for line in printenv_output.splitlines()])
        missing_env_vars = AirbytePythonConnectorBaseImage.EXPECTED_ENV_VARS - env_vars
        if missing_env_vars:
            raise errors.SanityCheckError(f"missing environment variables: {missing_env_vars}")


# HELPER FUNCTIONS
def get_all_python_base_images() -> dict[str, Type[AirbytePythonConnectorBaseImage]]:
    """Discover the base image versions declared in the module.
    It saves us from hardcoding the list of base images version: implementing a new class should be the only step to make a new base version available.

    Returns:
        dict[str, Type[AirbytePythonConnectorBaseImage]]: A dictionary of the base image versions declared in the module, keys are base image name and tag as string.
    """
    # Reverse the order of the members so that the latest version is first
    # cls_members = reversed(inspect.getmembers(sys.modules[__name__], inspect.isclass))
    # return {
    #     cls_member.name_with_tag: cls_member
    #     for _, cls_member in cls_members
    #     if issubclass(type(cls_member), type(AirbytePythonConnectorBaseImage))
    #     and cls_member != AirbytePythonConnectorBaseImage
    #     and cls_member != ABC
    # }

    current_package = __package__ or ""

    # Get a list of all modules in the current package
    package_path = current_package.replace(".", "/")
    package_modules = [module_name for _, module_name, _ in pkgutil.iter_modules([package_path])]

    # List all classes in the imported modules
    all_base_image_classes = {}
    for module_name in package_modules:
        module = importlib.import_module(f"{current_package}.{module_name}")
        cls_members = list(reversed(inspect.getmembers(module, inspect.isclass)))
        all_base_image_classes.update(
            {
                cls_member.name_with_tag: cls_member
                for _, cls_member in cls_members
                if issubclass(type(cls_member), type(AirbytePythonConnectorBaseImage))
                and cls_member != AirbytePythonConnectorBaseImage
                and cls_member != ABC
            }
        )
    return all_base_image_classes


ALL_BASE_IMAGES = get_all_python_base_images()
