#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from dagster import Definitions, EnvVar, ScheduleDefinition, load_assets_from_modules
from dagster_slack import SlackResource
from metadata_service.constants import METADATA_FILE_NAME, METADATA_FOLDER
from orchestrator.assets import connector_test_report, connector_metrics, github, metadata, registry, registry_entry, registry_report, specs_secrets_mask, slack
from orchestrator.config import (
    ANALYTICS_BUCKET,
    ANALYTICS_FOLDER,
    CI_MASTER_TEST_OUTPUT_REGEX,
    CI_TEST_REPORT_PREFIX,
    CONNECTOR_REPO_NAME,
    CONNECTORS_PATH,
    HIGH_QUEUE_PRIORITY,
    NIGHTLY_COMPLETE_REPORT_FILE_NAME,
    NIGHTLY_FOLDER,
    NIGHTLY_GHA_WORKFLOW_ID,
    NIGHTLY_INDIVIDUAL_TEST_REPORT_FILE_NAME,
    REGISTRIES_FOLDER,
    REPORT_FOLDER,
)
from orchestrator.jobs.connector_test_report import generate_connector_test_summary_reports, generate_nightly_reports
from orchestrator.jobs.metadata import generate_stale_gcs_latest_metadata_file
from orchestrator.jobs.registry import (
    add_new_metadata_partitions,
    remove_stale_metadata_partitions,
    remove_latest_metadata_partitions,
    generate_cloud_registry,
    generate_oss_registry,
    generate_registry_entry,
    generate_registry_reports,
)
from orchestrator.logging.sentry import setup_dagster_sentry
from orchestrator.resources.gcp import gcp_gcs_client, gcs_directory_blobs, gcs_file_blob, gcs_file_manager
from orchestrator.resources.github import (
    github_client,
    github_connector_repo,
    github_connectors_directory,
    github_connectors_metadata_files,
    github_workflow_runs,
)
from orchestrator.sensors.gcs import new_gcs_blobs_sensor
from orchestrator.sensors.registry import registry_updated_sensor

ASSETS = load_assets_from_modules(
    [
        slack,
        github,
        specs_secrets_mask,
        metadata,
        connector_metrics,
        registry,
        registry_report,
        connector_test_report,
        registry_entry,
    ]
)

SLACK_RESOURCE_TREE = {
    "slack": SlackResource(token=EnvVar("SLACK_TOKEN")),
}

GITHUB_RESOURCE_TREE = {
    "github_client": github_client.configured({"github_token": {"env": "GITHUB_METADATA_SERVICE_TOKEN"}}),
    "github_connector_repo": github_connector_repo.configured({"connector_repo_name": CONNECTOR_REPO_NAME}),
    "github_connectors_directory": github_connectors_directory.configured({"connectors_path": CONNECTORS_PATH}),
    "github_connectors_metadata_files": github_connectors_metadata_files.configured({"connectors_path": CONNECTORS_PATH}),
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
    **SLACK_RESOURCE_TREE,
    **GCS_RESOURCE_TREE,
    "all_metadata_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": METADATA_FOLDER, "match_regex": f".*/{METADATA_FILE_NAME}$"}
    ),
    "latest_metadata_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": METADATA_FOLDER, "match_regex": f".*latest/{METADATA_FILE_NAME}$"}
    )
}

DATA_WAREHOUSE_RESOURCE_TREE = {
    **GCS_RESOURCE_TREE,
    "latest_metrics_gcs_blob": gcs_directory_blobs.configured(
        {"gcs_bucket": ANALYTICS_BUCKET, "prefix": ANALYTICS_FOLDER, "match_regex": f".*.jsonl$", "only_one": True, "sort_key": "name", "reverse_sort": True}
    ),
}

REGISTRY_RESOURCE_TREE = {
    **SLACK_RESOURCE_TREE,
    **GCS_RESOURCE_TREE,

    "latest_oss_registry_gcs_blob": gcs_file_blob.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REGISTRIES_FOLDER, "gcs_filename": "oss_registry.json"}
    ),
    "latest_cloud_registry_gcs_blob": gcs_file_blob.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REGISTRIES_FOLDER, "gcs_filename": "cloud_registry.json"}
    ),
}

REGISTRY_ENTRY_RESOURCE_TREE = {
    **SLACK_RESOURCE_TREE,
    **GCS_RESOURCE_TREE,
    "latest_cloud_registry_entries_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": METADATA_FOLDER, "match_regex": f".*latest/cloud.json$"}
    ),
    "latest_oss_registry_entries_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": METADATA_FOLDER, "match_regex": f".*latest/oss.json$"}
    ),
    "release_candidate_cloud_registry_entries_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": METADATA_FOLDER, "match_regex": f".*release_candidate/cloud.json$"}
    ),
    "release_candidate_oss_registry_entries_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": METADATA_FOLDER, "match_regex": f".*release_candidate/oss.json$"}
    ),
}

CONNECTOR_TEST_REPORT_SENSOR_RESOURCE_TREE = {
    **GCS_RESOURCE_TREE,
    "latest_nightly_complete_file_blobs": gcs_directory_blobs.configured(
        {"gcs_bucket": {"env": "CI_REPORT_BUCKET"}, "prefix": NIGHTLY_FOLDER, "match_regex": f".*{NIGHTLY_COMPLETE_REPORT_FILE_NAME}$"}
    ),
}

CONNECTOR_TEST_REPORT_RESOURCE_TREE = {
    **SLACK_RESOURCE_TREE,
    **GITHUB_RESOURCE_TREE,
    **GCS_RESOURCE_TREE,
    **CONNECTOR_TEST_REPORT_SENSOR_RESOURCE_TREE,
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
    **DATA_WAREHOUSE_RESOURCE_TREE,
    **REGISTRY_RESOURCE_TREE,
    **REGISTRY_ENTRY_RESOURCE_TREE,
    **CONNECTOR_TEST_REPORT_RESOURCE_TREE,
}

SENSORS = [
    registry_updated_sensor(job=generate_registry_reports, resources_def=REGISTRY_RESOURCE_TREE),
    new_gcs_blobs_sensor(
        job=generate_oss_registry,
        resources_def=REGISTRY_ENTRY_RESOURCE_TREE,
        gcs_blobs_resource_key="latest_oss_registry_entries_file_blobs",
        interval=60,
    ),
    new_gcs_blobs_sensor(
        job=generate_oss_registry,
        resources_def=REGISTRY_ENTRY_RESOURCE_TREE,
        gcs_blobs_resource_key="release_candidate_oss_registry_entries_file_blobs",
        interval=60,
        allow_duplicate_runs=True,
    ),
    new_gcs_blobs_sensor(
        job=generate_cloud_registry,
        resources_def=REGISTRY_ENTRY_RESOURCE_TREE,
        gcs_blobs_resource_key="latest_cloud_registry_entries_file_blobs",
        interval=60,
    ),
    new_gcs_blobs_sensor(
        job=generate_cloud_registry,
        resources_def=REGISTRY_ENTRY_RESOURCE_TREE,
        gcs_blobs_resource_key="release_candidate_cloud_registry_entries_file_blobs",
        interval=60,
        allow_duplicate_runs=True,
    ),
    new_gcs_blobs_sensor(
        job=generate_nightly_reports,
        resources_def=CONNECTOR_TEST_REPORT_SENSOR_RESOURCE_TREE,
        gcs_blobs_resource_key="latest_nightly_complete_file_blobs",
        interval=(1 * 60 * 60),
    ),
]

SCHEDULES = [
    ScheduleDefinition(job=add_new_metadata_partitions, cron_schedule="*/2 * * * *", tags={"dagster/priority": HIGH_QUEUE_PRIORITY}),
    ScheduleDefinition(
        cron_schedule="*/2 * * * *",  # Every 2 minutes
        execution_timezone="US/Pacific",
        job=remove_stale_metadata_partitions,
    ),
    ScheduleDefinition(job=generate_connector_test_summary_reports, cron_schedule="@hourly"),
    ScheduleDefinition(
        cron_schedule="0 * * * *",  # Every hour
        execution_timezone="US/Pacific",
        job=generate_stale_gcs_latest_metadata_file,
    ),
]

JOBS = [
    generate_registry_reports,
    generate_oss_registry,
    generate_cloud_registry,
    generate_registry_entry,
    generate_nightly_reports,
    add_new_metadata_partitions,
    remove_stale_metadata_partitions,
    remove_latest_metadata_partitions,
    generate_stale_gcs_latest_metadata_file,
]

"""
START HERE

This is the entry point for the orchestrator.
It is a list of all the jobs, assets, resources, schedules, and sensors that are available to the orchestrator.
"""

setup_dagster_sentry()

defn = Definitions(
    jobs=JOBS,
    assets=ASSETS,
    resources=RESOURCES,
    schedules=SCHEDULES,
    sensors=SENSORS,
)
