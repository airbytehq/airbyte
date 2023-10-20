#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module contains hacks used in connectors pipelines. They're gathered here for tech debt visibility."""

from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING, Callable, List

import requests

if TYPE_CHECKING:
    from dagger import Client, Container
    from pipelines.airbyte_ci.connectors.context import ConnectorContext


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


# We want to invalidate the persisted dagger cache and gradle cache for source-postgres.
# We do it in the context of a project to boost the CI speed for this connector.
# Invalidating the cache on every run will help us gather unbiased metrics on the CI speed.
# This should be removed once the project is over.
CONNECTORS_WITHOUT_CACHING = [
    "source-postgres",
]


def get_cachebuster(context: ConnectorContext, logger: Logger) -> str:
    """
    This function will return a semi-static cachebuster value for connectors in CONNECTORS_WITHOUT_CACHING and a static value for all other connectors.
    By semi-static I mean that the value (the pipeline start time) will change on each pipeline execution but will be the same for all the steps of the pipeline.
    It ensures we do not use the remotely persisted dagger cache but we still benefit from the buildkit layer caching inside the pipeline execution.
    This hack is useful to collect unbiased metrics on the CI speed for connectors in CONNECTORS_WITHOUT_CACHING.

    When the cachebuster value is static it won't invalidate the dagger cache because it's the same value as the previous run: no layer will be rebuilt.
    When the cachebuster value is changed it will invalidate the dagger cache because it's a different value than the previous run: all downstream layers will be rebuilt.

    Returns:
        str: The cachebuster value.
    """
    if context.connector.technical_name in CONNECTORS_WITHOUT_CACHING:
        logger.warning(
            f"Invalidating the persisted dagger cache for {context.connector.technical_name}. Only used in the context of the CI performance improvements project for {context.connector.technical_name}."
        )
        return str(context.pipeline_start_timestamp)
    return "0"


def get_gradle_cache_volume_name(context: ConnectorContext, logger: Logger) -> str:
    """
    This function will return a semi-static gradle cache volume name for connectors in CONNECTORS_WITHOUT_CACHING and a static value for all other connectors.
    By semi-static I mean that the gradle cache volume name will change on each pipeline execution but will be the same for all the steps of the pipeline.
    This hack is useful to collect unbiased metrics on the CI speed for connectors in CONNECTORS_WITHOUT_CACHING: it guarantees that the gradle cache volume will be empty on each pipeline execution and no remote caching is used.

    Returns:
        str: The gradle cache volume name.
    """
    if context.connector.technical_name in CONNECTORS_WITHOUT_CACHING:
        logger.warning(
            f"Getting a fresh gradle cache volume name for {context.connector.technical_name} to not use remote caching. Only used in the context of the CI performance improvements project for {context.connector.technical_name}."
        )
        return f"gradle-cache-{context.pipeline_start_timestamp}"
    return "gradle-cache"
