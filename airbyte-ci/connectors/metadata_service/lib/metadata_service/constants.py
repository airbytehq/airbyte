#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import datetime

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
