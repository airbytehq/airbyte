#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from dagster import Definitions, ScheduleDefinition, load_assets_from_modules

from orchestrator.resources.gcp import gcp_gcs_client, gcs_directory_blobs, gcs_file_blob, gcs_file_manager
from orchestrator.resources.github import github_client, github_connector_repo, github_connectors_directory, github_workflow_runs

from orchestrator.assets import (
    connector_test_report,
    github,
    specs_secrets_mask,
    spec_cache,
    registry,
    registry_report,
    registry_entry,
    metadata,
)

from orchestrator.jobs.registry import (
    generate_registry_reports,
    generate_oss_registry,
    generate_cloud_registry,
    generate_registry_entry,
    add_new_metadata_partitions,
)
from orchestrator.jobs.connector_test_report import generate_nightly_reports, generate_connector_test_summary_reports
from orchestrator.sensors.registry import registry_updated_sensor
from orchestrator.sensors.gcs import new_gcs_blobs_sensor

from orchestrator.config import (
    REPORT_FOLDER,
    REGISTRIES_FOLDER,
    CONNECTORS_PATH,
    CONNECTOR_REPO_NAME,
    NIGHTLY_FOLDER,
    NIGHTLY_COMPLETE_REPORT_FILE_NAME,
    NIGHTLY_INDIVIDUAL_TEST_REPORT_FILE_NAME,
    NIGHTLY_GHA_WORKFLOW_ID,
    CI_TEST_REPORT_PREFIX,
    CI_MASTER_TEST_OUTPUT_REGEX,
)
from metadata_service.constants import METADATA_FILE_NAME, METADATA_FOLDER

ASSETS = load_assets_from_modules(
    [
        github,
        specs_secrets_mask,
        spec_cache,
        metadata,
        registry,
        registry_report,
        connector_test_report,
        registry_entry,
    ]
)

GITHUB_RESOURCE_TREE = {
    "github_client": github_client.configured({"github_token": {"env": "GITHUB_METADATA_SERVICE_TOKEN"}}),
    "github_connector_repo": github_connector_repo.configured({"connector_repo_name": CONNECTOR_REPO_NAME}),
    "github_connectors_directory": github_connectors_directory.configured({"connectors_path": CONNECTORS_PATH}),
    "github_connector_nightly_workflow_successes": github_workflow_runs.configured(
        {
            "workflow_id": NIGHTLY_GHA_WORKFLOW_ID,
            "branch": "master",
            "status": "success",
        }
    ),
}

GCS_RESOURCE_TREE = {
    "gcp_gcs_client": gcp_gcs_client.configured(
        {
            "gcp_gcs_cred_string": {"env": "GCS_CREDENTIALS"},
        }
    ),
    "registry_directory_manager": gcs_file_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REGISTRIES_FOLDER}),
    "registry_report_directory_manager": gcs_file_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REPORT_FOLDER}),
    "root_metadata_directory_manager": gcs_file_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": ""}),
}

METADATA_RESOURCE_TREE = {
    **GCS_RESOURCE_TREE,
    "all_metadata_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": METADATA_FOLDER, "match_regex": f".*/{METADATA_FILE_NAME}$"}
    ),
    "latest_metadata_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": METADATA_FOLDER, "match_regex": f".*latest/{METADATA_FILE_NAME}$"}
    ),
}

REGISTRY_RESOURCE_TREE = {
    **GCS_RESOURCE_TREE,
    "latest_oss_registry_gcs_blob": gcs_file_blob.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REGISTRIES_FOLDER, "gcs_filename": "oss_registry.json"}
    ),
    "latest_cloud_registry_gcs_blob": gcs_file_blob.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REGISTRIES_FOLDER, "gcs_filename": "cloud_registry.json"}
    ),
}

REGISTRY_ENTRY_RESOURCE_TREE = {
    **GCS_RESOURCE_TREE,
    "latest_cloud_registry_entries_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": METADATA_FOLDER, "match_regex": f".*latest/cloud.json$"}
    ),
    "latest_oss_registry_entries_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": METADATA_FOLDER, "match_regex": f".*latest/oss.json$"}
    ),
}

CONNECTOR_TEST_REPORT_RESOURCE_TREE = {
    **GITHUB_RESOURCE_TREE,
    **GCS_RESOURCE_TREE,
    "latest_nightly_complete_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "CI_REPORT_BUCKET"}, "prefix": NIGHTLY_FOLDER, "match_regex": f".*{NIGHTLY_COMPLETE_REPORT_FILE_NAME}$"}
    ),
    "latest_nightly_test_output_file_blobs": gcs_directory_blobs.configured(
        {
            "gcs_bucket": {"env": "CI_REPORT_BUCKET"},
            "prefix": NIGHTLY_FOLDER,
            "match_regex": f".*{NIGHTLY_INDIVIDUAL_TEST_REPORT_FILE_NAME}$",
        }
    ),
    "all_connector_test_output_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "CI_REPORT_BUCKET"}, "prefix": CI_TEST_REPORT_PREFIX, "match_regex": CI_MASTER_TEST_OUTPUT_REGEX}
    ),
}

RESOURCES = {
    **METADATA_RESOURCE_TREE,
    **REGISTRY_RESOURCE_TREE,
    **REGISTRY_ENTRY_RESOURCE_TREE,
    **CONNECTOR_TEST_REPORT_RESOURCE_TREE,
}

SENSORS = [
    registry_updated_sensor(job=generate_registry_reports, resources_def=RESOURCES),
    new_gcs_blobs_sensor(
        job=generate_oss_registry,
        resources_def=REGISTRY_ENTRY_RESOURCE_TREE,
        gcs_blobs_resource_key="latest_oss_registry_entries_file_blobs",
        interval=30,
    ),
    new_gcs_blobs_sensor(
        job=generate_cloud_registry,
        resources_def=REGISTRY_ENTRY_RESOURCE_TREE,
        gcs_blobs_resource_key="latest_cloud_registry_entries_file_blobs",
        interval=30,
    ),
    new_gcs_blobs_sensor(
        job=generate_nightly_reports,
        resources_def=CONNECTOR_TEST_REPORT_RESOURCE_TREE,
        gcs_blobs_resource_key="latest_nightly_complete_file_blobs",
        interval=(1 * 60 * 60),
    ),
]

SCHEDULES = [
    ScheduleDefinition(job=add_new_metadata_partitions, cron_schedule="* * * * *"),
    ScheduleDefinition(job=generate_connector_test_summary_reports, cron_schedule="@hourly"),
]

JOBS = [
    generate_registry_reports,
    generate_oss_registry,
    generate_cloud_registry,
    generate_registry_entry,
    generate_nightly_reports,
    add_new_metadata_partitions,
]

"""
START HERE

This is the entry point for the orchestrator.
It is a list of all the jobs, assets, resources, schedules, and sensors that are available to the orchestrator.
"""
defn = Definitions(
    jobs=JOBS,
    assets=ASSETS,
    resources=RESOURCES,
    schedules=SCHEDULES,
    sensors=SENSORS,
)
