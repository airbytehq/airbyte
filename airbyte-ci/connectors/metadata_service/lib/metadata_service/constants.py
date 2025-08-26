#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import datetime
from typing import Optional

CONNECTORS_PATH = "airbyte-integrations/connectors"
METADATA_FILE_NAME = "metadata.yaml"
MANIFEST_FILE_NAME = "manifest.yaml"
COMPONENTS_PY_FILE_NAME = "components.py"
ICON_FILE_NAME = "icon.svg"
METADATA_FOLDER = "metadata"
DOCS_FOLDER_PATH = "docs/integrations"
DOC_FILE_NAME = "doc.md"
DOC_INAPP_FILE_NAME = "doc.inapp.md"
COMPONENTS_ZIP_FILE_NAME = "components.zip"
COMPONENTS_ZIP_SHA256_FILE_NAME = "components.zip.sha256"
LATEST_GCS_FOLDER_NAME = "latest"
RELEASE_CANDIDATE_GCS_FOLDER_NAME = "release_candidate"
METADATA_CDN_BASE_URL = "https://connectors.airbyte.com/files"
DEFAULT_ASSET_URL = "https://storage.googleapis.com"

VALID_REGISTRIES = ["oss", "cloud"]
REGISTRIES_FOLDER = "registries/v0"
ANALYTICS_BUCKET = "ab-analytics-connector-metrics"
ANALYTICS_FOLDER = "data/connector_quality_metrics"
PUBLIC_GCS_BASE_URL = "https://storage.googleapis.com/"

VALID_REGISTRIES = ["oss", "cloud"]
REGISTRIES_FOLDER = "registries/v0"
ANALYTICS_BUCKET = "ab-analytics-connector-metrics"
ANALYTICS_FOLDER = "data/connector_quality_metrics"
PUBLIC_GCS_BASE_URL = "https://storage.googleapis.com/"

GITHUB_REPO_NAME = "airbytehq/airbyte"
EXTENSIBILITY_TEAM_SLACK_TEAM_ID = "S08SQDL2RS9"  # @oc-extensibility-critical-systems
STALE_REPORT_CHANNEL = "C05507UP11A"  # #dev-connectors-extensibility-alerts
PUBLISH_UPDATE_CHANNEL = "C056HGD1QSW"  # #connector-publish-updates
# We give 6 hours for the metadata to be updated
# This is an empirical value that we can adjust if needed
# When our auto-merge pipeline runs it can merge hundreds of up-to-date PRs following.
# Given our current publish concurrency of 10 runners, it can take up to 6 hours to publish all the connectors.
# A shorter grace period could lead to false positives in stale metadata detection.
PUBLISH_GRACE_PERIOD = datetime.timedelta(hours=6)
SLACK_NOTIFICATIONS_ENABLED = "true"

SPECS_SECRETS_MASK_FILE_NAME = "specs_secrets_mask.yaml"

CONNECTOR_DEPENDENCY_FOLDER = "connector_dependencies"
CONNECTOR_DEPENDENCY_FILE_NAME = "dependencies.json"


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
