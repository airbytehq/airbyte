#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

import requests
from orchestrator.models.metadata import LatestMetadataEntry


GROUP_NAME = "connector_cdk_versions"

BASE_URL = "https://storage.googleapis.com/dev-airbyte-cloud-connector-metadata-service/"
DEPENDENCY_FOLDER = "connector_dependencies"
DEPENDENCY_FILE = "dependencies.json"
PACKAGE_NAME = "airbyte-cdk"
PYTHON_CDK_SLUG = "python"

# HELPERS


def safe_get_json_from_url(url: str) -> Optional[dict]:
    try:
        response = requests.get(url)
        if response.ok:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None


def find_package_version(dependencies_body: dict, package_name: str) -> Optional[str]:
    for package in dependencies_body.get("dependencies", []):
        if package.get("package_name") == package_name:
            return package.get("version")
    return None


def get_cdk_version(
    metadata_entry: LatestMetadataEntry,
) -> Optional[str]:
    url = metadata_entry.dependency_file_url
    if not url:
        return None

    response = safe_get_json_from_url(url)
    if not response:
        return None

    version = find_package_version(response, PACKAGE_NAME)

    # Note: Prefix the version with the python slug as the python cdk is the only one we have
    # versions available for.
    return f"{PYTHON_CDK_SLUG}:{version}" if version else None
