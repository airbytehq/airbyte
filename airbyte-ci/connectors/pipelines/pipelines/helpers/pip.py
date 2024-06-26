# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Optional

import requests


def is_package_published(package_name: Optional[str], version: Optional[str], registry_url: str) -> bool:
    """
    Check if a package with a specific version is published on a python registry.
    """
    if not package_name or not version:
        return False

    url = f"{registry_url}/{package_name}/{version}/json"

    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
