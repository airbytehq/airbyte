#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from typing import Optional

DEFAULT_ASSET_URL = "https://storage.googleapis.com"

VALID_REGISTRIES = ["oss", "cloud"]
REGISTRIES_FOLDER = "registries/v0"
REPORT_FOLDER = "generated_reports"

NIGHTLY_FOLDER = "airbyte-ci/connectors/test/nightly_builds/master"
NIGHTLY_COMPLETE_REPORT_FILE_NAME = "complete.json"
NIGHTLY_INDIVIDUAL_TEST_REPORT_FILE_NAME = "output.json"
NIGHTLY_GHA_WORKFLOW_ID = "connector_nightly_builds_dagger.yml"
CI_TEST_REPORT_PREFIX = "airbyte-ci/connectors/test"
CI_MASTER_TEST_OUTPUT_REGEX = f".*master.*output.json$"

CONNECTOR_REPO_NAME = "airbytehq/airbyte"
CONNECTORS_PATH = "airbyte-integrations/connectors"
CONNECTOR_TEST_SUMMARY_FOLDER = "test_summary"

CONNECTOR_DEPENDENCY_FOLDER = "connector_dependencies"
CONNECTOR_DEPENDENCY_FILE_NAME = "dependencies.json"

MAX_METADATA_PARTITION_RUN_REQUEST = 50

HIGH_QUEUE_PRIORITY = "3"
MED_QUEUE_PRIORITY = "2"
LOW_QUEUE_PRIORITY = "1"
NO_QUEUE_PRIORITY = "-1"


def get_public_url_for_gcs_file(bucket_name: str, file_path: str, cdn_url: Optional[str] = None) -> str:
    """Get the public URL to a file in the GCS bucket.

    Args:
        bucket_name: The name of the GCS bucket.
        file_path: The path to the file in the bucket.
        cdn_url: The base URL of the CDN that serves the bucket.

    Returns:
        The public URL to the file.
    """
    return f"{cdn_url}/{file_path}" if cdn_url else f"{DEFAULT_ASSET_URL}/{bucket_name}/{file_path}"


def get_public_metadata_service_url(file_path: str) -> str:
    metadata_bucket = os.getenv("METADATA_BUCKET")
    metadata_cdn_url = os.getenv("METADATA_CDN_BASE_URL")
    return get_public_url_for_gcs_file(metadata_bucket, file_path, metadata_cdn_url)


REPO_URL = "https://github.com/airbytehq/airbyte/"
