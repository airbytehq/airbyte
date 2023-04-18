#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from dagster import Definitions
from metadata_service.constants import METADATA_FILE_NAME, METADATA_FOLDER
from orchestrator.assets.catalog import (
    cloud_catalog_from_metadata,
    cloud_destinations_dataframe,
    cloud_sources_dataframe,
    latest_cloud_catalog_dict,
    latest_oss_catalog_dict,
    oss_catalog_from_metadata,
    oss_destinations_dataframe,
    oss_sources_dataframe,
)
from orchestrator.assets.catalog_report import (
    all_destinations_dataframe,
    all_sources_dataframe,
    connector_catalog_location_html,
    connector_catalog_location_markdown,
)
from orchestrator.assets.dev import (
    cloud_catalog_diff,
    cloud_catalog_diff_dataframe,
    metadata_directory_report,
    oss_catalog_diff,
    oss_catalog_diff_dataframe,
    overrode_metadata_definitions,
    persist_metadata_definitions,
)
from orchestrator.assets.github import github_connector_folders
from orchestrator.assets.metadata import catalog_derived_metadata_definitions, metadata_definitions, valid_metadata_report_dataframe
from orchestrator.assets.spec_cache import cached_specs
from orchestrator.assets.specs_secrets_mask import all_specs_secrets, specs_secrets_mask_yaml
from orchestrator.config import CATALOG_FOLDER, CONNECTOR_REPO_NAME, CONNECTORS_PATH, REPORT_FOLDER
from orchestrator.jobs.catalog import generate_catalog, generate_catalog_markdown, generate_local_metadata_files
from orchestrator.resources.gcp import gcp_gcs_client, gcs_bucket_manager, gcs_directory_blobs, gcs_file_blob, gcs_file_manager
from orchestrator.resources.github import github_client, github_connector_repo, github_connectors_directory
from orchestrator.resources.local import simple_local_file_manager
from orchestrator.sensors.catalog import catalog_updated_sensor
from orchestrator.sensors.metadata import metadata_updated_sensor

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
    all_specs_secrets,
    specs_secrets_mask_yaml,
    metadata_directory_report,
    metadata_definitions,
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
    "catalog_directory_manager": gcs_file_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": CATALOG_FOLDER}),
    "catalog_report_directory_manager": gcs_file_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REPORT_FOLDER}),
    "metadata_file_blobs": gcs_directory_blobs.configured({"prefix": METADATA_FOLDER, "suffix": METADATA_FILE_NAME}),
    "latest_oss_catalog_gcs_file": gcs_file_blob.configured({"prefix": CATALOG_FOLDER, "gcs_filename": "oss_catalog.json"}),
    "latest_cloud_catalog_gcs_file": gcs_file_blob.configured({"prefix": CATALOG_FOLDER, "gcs_filename": "cloud_catalog.json"}),
}

SENSORS = [
    catalog_updated_sensor(job=generate_catalog_markdown, resources_def=RESOURCES),
    metadata_updated_sensor(job=generate_catalog, resources_def=RESOURCES),
]

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
