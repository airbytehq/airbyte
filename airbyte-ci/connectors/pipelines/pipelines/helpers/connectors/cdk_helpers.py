#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import re

import requests
from dagger import Directory


def get_latest_python_cdk_version() -> str:
    """
    Get the latest version of airbyte-cdk from pypi
    """
    cdk_pypi_url = "https://pypi.org/pypi/airbyte-cdk/json"
    response = requests.get(cdk_pypi_url)
    response.raise_for_status()
    package_info = response.json()
    return package_info["info"]["version"]


async def get_latest_java_cdk_version(repo_dir: Directory) -> str:
    version_file_content = await repo_dir.file("airbyte-cdk/java/airbyte-cdk/core/src/main/resources/version.properties").contents()
    match = re.search(r"version *= *(?P<version>[0-9]*\.[0-9]*\.[0-9]*)", version_file_content)
    if match:
        return match.group("version")
    raise ValueError("Could not find version in version.properties")
