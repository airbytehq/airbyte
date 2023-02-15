#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os

CONNECTOR_BUILD_OUTPUT_URL = "https://dnsgjos7lj2fu.cloudfront.net/tests/history/connectors"
CLOUD_CATALOG_URL = "https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/cloud_catalog.json"
OSS_CATALOG_URL = "https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/oss_catalog.json"

INAPPROPRIATE_FOR_CLOUD_USE_CONNECTORS = [
    "8be1cf83-fde1-477f-a4ad-318d23c9f3c6",  # Local CSV
    "a625d593-bba5-4a1c-a53d-2d246268a816",  # Local JSON
    "b76be0a6-27dc-4560-95f6-2623da0bd7b6",  # Local SQL Lite
]

GCS_QA_REPORT_PATH = "gs://airbyte-data-connectors-qa-engine/"
AIRBYTE_PLATFORM_INTERNAL_REPO_OWNER = "airbytehq"
AIRBYTE_PLATFORM_INTERNAL_REPO_NAME = "airbyte-platform-internal"
AIRBYTE_PLATFORM_INTERNAL_GITHUB_REPO_URL = (
    f"https://github.com/{AIRBYTE_PLATFORM_INTERNAL_REPO_OWNER}/{AIRBYTE_PLATFORM_INTERNAL_REPO_NAME}.git"
)
AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME = "master"
AIRBYTE_PLATFORM_INTERNAL_PR_ENDPOINT = (
    f"https://api.github.com/repos/{AIRBYTE_PLATFORM_INTERNAL_REPO_OWNER}/{AIRBYTE_PLATFORM_INTERNAL_REPO_NAME}/pulls"
)
GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN")
GITHUB_API_COMMON_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Authorization": f"Bearer {GITHUB_API_TOKEN}",
}
