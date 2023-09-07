#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module contains hacks used in connectors pipelines. They're gathered here for tech debt visibility."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List

import requests
from connector_ops.utils import ConnectorLanguage
from dagger import DaggerError

if TYPE_CHECKING:
    from dagger import Client, Container, Directory
    from pipelines.contexts import ConnectorContext


LINES_TO_REMOVE_FROM_GRADLE_FILE = [
    # Do not build normalization with Gradle - we build normalization with Dagger in the BuildOrPullNormalization step.
    "project(':airbyte-integrations:bases:base-normalization').airbyteDocker.output",
]


async def _patch_gradle_file(context: ConnectorContext, connector_dir: Directory) -> Directory:
    """Patch the build.gradle file of the connector under test by removing the lines declared in LINES_TO_REMOVE_FROM_GRADLE_FILE.

    Underlying issue:
        Java connectors build.gradle declare a dependency to the normalization module.
        It means every time we test a java connector the normalization is built.
        This is time consuming and not required as normalization is now baked in containers.
        Normalization is going away soon so hopefully this hack will be removed soon.

    Args:
        context (ConnectorContext): The initialized connector context.
        connector_dir (Directory): The directory containing the build.gradle file to patch.
    Returns:
        Directory: The directory containing the patched gradle file.
    """
    if context.connector.language is not ConnectorLanguage.JAVA:
        context.logger.info(f"Connector language {context.connector.language} does not require a patched build.gradle file.")
        return connector_dir

    try:
        gradle_file_content = await connector_dir.file("build.gradle").contents()
    except DaggerError:
        context.logger.info("Could not find build.gradle file in the connector directory. Skipping patching.")
        return connector_dir

    context.logger.warn("Patching build.gradle file to remove normalization build.")

    patched_gradle_file = []

    for line in gradle_file_content.splitlines():
        if not any(line_to_remove in line for line_to_remove in LINES_TO_REMOVE_FROM_GRADLE_FILE):
            patched_gradle_file.append(line)
    return connector_dir.with_new_file("build.gradle", contents="\n".join(patched_gradle_file))


async def patch_connector_dir(context: ConnectorContext, connector_dir: Directory) -> Directory:
    """Patch a connector directory: patch cat config, gradle file and dockerfile.

    Args:
        context (ConnectorContext): The initialized connector context.
        connector_dir (Directory): The directory containing the connector to patch.
    Returns:
        Directory: The directory containing the patched connector.
    """
    patched_connector_dir = await _patch_gradle_file(context, connector_dir)
    return patched_connector_dir.with_timestamps(1)


async def cache_latest_cdk(dagger_client: Client, pip_cache_volume_name: str = "pip_cache") -> None:
    """
    Download the latest CDK version to update the pip cache.

    Underlying issue:
        Most Python connectors, or normalization, are not pinning the CDK version they use.
        It means that the will get whatever version is in the pip cache.
        But the original goal of not pinning the CDK version is to always get the latest version.

    Hack:
        Call this function before building connector test environment to update the cache with the latest CDK version.

    Github Issue:
        Revisiting and aligning how we build Python connectors and using the same container for test, build and publish will provide better control over the CDK version.
        https://github.com/airbytehq/airbyte/issues/25523
    Args:
        dagger_client (Client): Dagger client.
    """

    # We get the latest version of the CDK from PyPI using their API.
    # It allows us to explicitly install the latest version of the CDK in the container
    # while keeping buildkit layer caching when the version value does not change.
    # In other words: we only update the pip cache when the latest CDK version changes.
    # When the CDK version does not change, the pip cache is not updated as the with_exec command remains the same.
    cdk_pypi_url = "https://pypi.org/pypi/airbyte-cdk/json"
    response = requests.get(cdk_pypi_url)
    response.raise_for_status()
    package_info = response.json()
    cdk_latest_version = package_info["info"]["version"]

    await (
        dagger_client.container()
        .from_("python:3.9-slim")
        .with_mounted_cache("/root/.cache/pip", dagger_client.cache_volume(pip_cache_volume_name))
        .with_exec(["pip", "install", "--force-reinstall", f"airbyte-cdk=={cdk_latest_version}"])
        .sync()
    )


def never_fail_exec(command: List[str]) -> Callable:
    """
    Wrap a command execution with some bash sugar to always exit with a 0 exit code but write the actual exit code to a file.

    Underlying issue:
        When a classic dagger with_exec is returning a >0 exit code an ExecError is raised.
        It's OK for the majority of our container interaction.
        But some execution, like running CAT, are expected to often fail.
        In CAT we don't want ExecError to be raised on container interaction because CAT might write updated secrets that we need to pull from the container after the test run.
        The bash trick below is a hack to always return a 0 exit code but write the actual exit code to a file.
        The file is then read by the pipeline to determine the exit code of the container.

    Args:
        command (List[str]): The command to run in the container.

    Returns:
        Callable: _description_
    """

    def never_fail_exec_inner(container: Container):
        return container.with_exec(["sh", "-c", f"{' '.join(command)}; echo $? > /exit_code"], skip_entrypoint=True)

    return never_fail_exec_inner
