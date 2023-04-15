from dagster import Definitions

from orchestrator.resources.gcp import gcp_gcs_client, gcs_bucket_manager, gcs_file_manager, gcs_file_blob
from orchestrator.resources.github import github_client, github_connector_repo, github_connectors_directory
from orchestrator.resources.local import simple_local_file_manager

from orchestrator.assets.github import github_connector_folders
from orchestrator.assets.spec_cache import cached_specs
from orchestrator.assets.catalog_report import (
    all_sources_dataframe,
    all_destinations_dataframe,
    connector_catalog_location_markdown,
    connector_catalog_location_html,
)
from orchestrator.assets.catalog import (
    oss_destinations_dataframe,
    cloud_destinations_dataframe,
    oss_sources_dataframe,
    cloud_sources_dataframe,
    latest_oss_catalog_dict,
    latest_cloud_catalog_dict,
    oss_catalog_from_metadata,
    cloud_catalog_from_metadata,
)
from orchestrator.assets.metadata import (
    catalog_derived_metadata_definitions,
    valid_metadata_report_dataframe,
)

from orchestrator.assets.dev import (
    persist_metadata_definitions,
    overrode_metadata_definitions,
    oss_catalog_diff,
    cloud_catalog_diff,
    cloud_catalog_diff_dataframe,
    oss_catalog_diff_dataframe,
)

from orchestrator.jobs.catalog import generate_catalog_markdown, generate_local_metadata_files
from orchestrator.sensors.catalog import catalog_updated_sensor

from orchestrator.config import REPORT_FOLDER, CATALOG_FOLDER, CONNECTORS_PATH, CONNECTOR_REPO_NAME

ASSETS = [
    oss_destinations_dataframe,
    cloud_destinations_dataframe,
    oss_sources_dataframe,
    cloud_sources_dataframe,
    latest_oss_catalog_dict,
    latest_cloud_catalog_dict,
    all_sources_dataframe,
    all_destinations_dataframe,
    connector_catalog_location_markdown,
    connector_catalog_location_html,
    github_connector_folders,
    catalog_derived_metadata_definitions,
    valid_metadata_report_dataframe,
    persist_metadata_definitions,
    overrode_metadata_definitions,
    cached_specs,
    oss_catalog_diff,
    oss_catalog_from_metadata,
    cloud_catalog_diff,
    cloud_catalog_from_metadata,
    cloud_catalog_diff_dataframe,
    oss_catalog_diff_dataframe,
]

RESOURCES = {
    "metadata_file_directory": simple_local_file_manager.configured({"base_dir": "/tmp/metadata"}),
    "github_client": github_client,
    "github_connector_repo": github_connector_repo.configured({"connector_repo_name": CONNECTOR_REPO_NAME}),
    "github_connectors_directory": github_connectors_directory.configured({"connectors_path": CONNECTORS_PATH}),
    "gcp_gcs_client": gcp_gcs_client.configured(
        {
            "gcp_gcs_cred_string": {"env": "GCS_CREDENTIALS"},
        }
    ),
    "gcs_bucket_manager": gcs_bucket_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}}),
    "catalog_report_directory_manager": gcs_file_manager.configured(
        {"gcs_bucket": {"env": "METADATA_BUCKET"}, "gcs_prefix": REPORT_FOLDER}
    ),
    "latest_oss_catalog_gcs_file": gcs_file_blob.configured({"gcs_prefix": CATALOG_FOLDER, "gcs_filename": "oss_catalog.json"}),
    "latest_cloud_catalog_gcs_file": gcs_file_blob.configured({"gcs_prefix": CATALOG_FOLDER, "gcs_filename": "cloud_catalog.json"}),
}

SENSORS = [catalog_updated_sensor(job=generate_catalog_markdown, resources_def=RESOURCES)]

SCHEDULES = []

JOBS = [generate_catalog_markdown, generate_local_metadata_files]

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
