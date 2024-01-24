# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Optional
from urllib.parse import urlparse

import requests


def is_package_published(package_name: Optional[str], version: Optional[str], registry_url: str) -> bool:
    """
    Check if a package with a specific version is published on PyPI or Test PyPI.

    :param package_name: The name of the package to check.
    :param version: The version of the package.
    :param test_pypi: Set to True to check on Test PyPI, False for regular PyPI.
    :return: True if the package is found with the specified version, False otherwise.
    """
    if not package_name or not version:
        return False

    parsed_registry_url = urlparse(registry_url)
    base_url = f"{parsed_registry_url.scheme}://{parsed_registry_url.netloc}"

    url = f"{base_url}/{package_name}/{version}/json"

    response = requests.get(url)
    return response.status_code == 200
