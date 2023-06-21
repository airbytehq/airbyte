#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os

CONNECTOR_TEST_SUMMARY_URL = "https://connectors.airbyte.com/files/generated_reports/test_summary"
CLOUD_CATALOG_URL = "https://connectors.airbyte.com/files/registries/v0/cloud_registry.json"
OSS_CATALOG_URL = "https://connectors.airbyte.com/files/registries/v0/oss_registry.json"

INAPPROPRIATE_FOR_CLOUD_USE_CONNECTORS = [
    "8be1cf83-fde1-477f-a4ad-318d23c9f3c6",  # Local CSV
    "a625d593-bba5-4a1c-a53d-2d246268a816",  # Local JSON
    "b76be0a6-27dc-4560-95f6-2623da0bd7b6",  # Local SQL Lite
    "2300fdcf-a532-419f-9f24-a014336e7966",  # destination-yugabytedb, no strict-encrypt variant
    "7cf88806-25f5-4e1a-b422-b2fa9e1b0090",  # source-elasticsearch, no strict-encrypt variant
    "0dad1a35-ccf8-4d03-b73e-6788c00b13ae",  # source-tidb, no strict-encrypt variant
    "d53f9084-fa6b-4a5a-976c-5b8392f4ad8a",  # source-e2e-testing, a cloud variant already exists
    "f3802bc4-5406-4752-9e8d-01e504ca8194",  # destination-mqtt, no strict-encrypt variant
    "825c5ee3-ed9a-4dd1-a2b6-79ed722f7b13",  # destination-redpanda, no strict-encrypt variant
    "58e6f9da-904e-11ed-a1eb-0242ac120002",  # destination-teradata, no strict-encrypt variant
    "bb6071d9-6f34-4766-bec2-d1d4ed81a653",  # destination-exasol, no strict-encrypt variant
    "7b7d7a0d-954c-45a0-bcfc-39a634b97736",  # destination-weviate, no strict-encrypt variant
    "06ec60c7-7468-45c0-91ac-174f6e1a788b",  # destination-tidb, no strict-encrypt variant
    "2af123bf-0aaf-4e0d-9784-cb497f23741a",  # source-appstore, originally ignored in the source connector masks
    "9fa5862c-da7c-11eb-8d19-0242ac130003",  # source-cockroachdb, originally ignored in the source connector masks
    "445831eb-78db-4b1f-8f1f-0d96ad8739e2",  # source-drift, originally ignored in the source connector masks
    "d917a47b-8537-4d0d-8c10-36a9928d4265",  # source-kafka, originally ignored in the source connector masks
    "9f760101-60ae-462f-9ee6-b7a9dafd454d",  # destination-kafka, originally ignored in the destination connector masks
    "4528e960-6f7b-4412-8555-7e0097e1da17",  # destination-starburst-galaxy, no strict-encrypt variant
    "aa8ba6fd-4875-d94e-fc8d-4e1e09aa2503",  # source-teradata, no strict-encrypt variant
    "447e0381-3780-4b46-bb62-00a4e3c8b8e2",  # source-db2, no strict-encrypt variant
]

GCS_QA_REPORT_PATH = "gs://airbyte-data-connectors-qa-engine/"
AIRBYTE_REPO_OWNER = "airbytehq"
AIRBYTE_REPO_NAME = "airbyte"
AIRBYTE_GITHUB_REPO_URL = f"https://github.com/{AIRBYTE_REPO_OWNER}/{AIRBYTE_REPO_NAME}.git"
AIRBYTE_MAIN_BRANCH_NAME = "master"
AIRBYTE_REPO_ENDPOINT = f"https://api.github.com/repos/{AIRBYTE_REPO_OWNER}/{AIRBYTE_REPO_NAME}"
AIRBYTE_PR_ENDPOINT = f"{AIRBYTE_REPO_ENDPOINT}/pulls"
AIRBYTE_ISSUES_ENDPOINT = f"{AIRBYTE_REPO_ENDPOINT}/issues"

GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN")
GITHUB_API_COMMON_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Authorization": f"Bearer {GITHUB_API_TOKEN}",
}
GIT_USERNAME_FOR_AUTH = "octavia-squidington-iii"
GIT_USER_EMAIL = f"{GIT_USERNAME_FOR_AUTH}@sers.noreply.github.com"
GIT_USERNAME = "Octavia Squidington III"
PR_LABELS = ["team/connector-ops", "cloud-availability-updater"]
