#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module contains hacks used in connectors pipelines. They're gathered here for tech debt visibility."""

from __future__ import annotations

from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from dagger import Client


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
