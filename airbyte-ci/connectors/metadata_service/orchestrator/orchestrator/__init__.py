#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from dagster import Definitions

from orchestrator.jobs.registry import generate_registry, generate_registry_markdown, generate_local_metadata_files
from orchestrator.resources.gcp import gcp_gcs_client, gcs_bucket_manager, gcs_directory_blobs, gcs_file_blob, gcs_file_manager
from orchestrator.resources.github import github_client, github_connector_repo, github_connectors_directory
from orchestrator.resources.local import simple_local_file_manager


from orchestrator.assets.github import github_connector_folders
from orchestrator.assets.specs_secrets_mask import all_specs_secrets, specs_secrets_mask_yaml
from orchestrator.assets.spec_cache import cached_specs
from orchestrator.assets.registry_report import (
    all_sources_dataframe,
    all_destinations_dataframe,
    connector_registry_location_markdown,
    connector_registry_location_html,
)
from orchestrator.assets.registry import (
    oss_destinations_dataframe,
    cloud_destinations_dataframe,
    oss_sources_dataframe,
    cloud_sources_dataframe,
    latest_oss_registry_dict,
    latest_cloud_registry_dict,
    oss_registry_from_metadata,
    cloud_registry_from_metadata,
)
from orchestrator.assets.metadata import (
    registry_derived_metadata_definitions,
    valid_metadata_report_dataframe,
    metadata_definitions,
)

from orchestrator.assets.dev import (
    persist_metadata_definitions,
    overrode_metadata_definitions,
    oss_registry_diff,
    cloud_registry_diff,
    cloud_registry_diff_dataframe,
    oss_registry_diff_dataframe,
    metadata_directory_report,
)

from orchestrator.jobs.registry import generate_registry_markdown, generate_local_metadata_files, generate_registry
from orchestrator.sensors.registry import registry_updated_sensor
from orchestrator.sensors.metadata import metadata_updated_sensor

from orchestrator.config import REPORT_FOLDER, REGISTRIES_FOLDER, CONNECTORS_PATH, CONNECTOR_REPO_NAME
from metadata_service.constants import METADATA_FILE_NAME, METADATA_FOLDER

ASSETS = [
    oss_destinations_dataframe,
    cloud_destinations_dataframe,
    oss_sources_dataframe,
    cloud_sources_dataframe,
    latest_oss_registry_dict,
    latest_cloud_registry_dict,
    all_sources_dataframe,
    all_destinations_dataframe,
    connector_registry_location_markdown,
    connector_registry_location_html,
    github_connector_folders,
    registry_derived_metadata_definitions,
    valid_metadata_report_dataframe,
    persist_metadata_definitions,
    overrode_metadata_definitions,
    cached_specs,
    oss_registry_diff,
    oss_registry_from_metadata,
    cloud_registry_diff,
    cloud_registry_from_metadata,
    cloud_registry_diff_dataframe,
    oss_registry_diff_dataframe,
    all_specs_secrets,
    specs_secrets_mask_yaml,
    metadata_directory_report,
    metadata_definitions,
]

RESOURCES = {
    "metadata_file_directory": simple_local_file_manager.configured({"base_dir": "/tmp/metadata"}),
    "github_client": github_client.configured({"github_token": {"env": "GITHUB_METADATA_SERVICE_TOKEN"}}),
    "github_connector_repo": github_connector_repo.configured({"connector_repo_name": CONNECTOR_REPO_NAME}),
    "github_connectors_directory": github_connectors_directory.configured({"connectors_path": CONNECTORS_PATH}),
    "gcp_gcs_client": gcp_gcs_client.configured(
        {
            "gcp_gcs_cred_string": {"env": "GCS_CREDENTIALS"},
        }
    ),
    "gcs_bucket_manager": gcs_bucket_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}}),
    "registry_directory_manager": gcs_file_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REGISTRIES_FOLDER}),
    "registry_report_directory_manager": gcs_file_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REPORT_FOLDER}),
    "metadata_file_blobs": gcs_directory_blobs.configured({"prefix": METADATA_FOLDER, "suffix": METADATA_FILE_NAME}),
    "latest_oss_registry_gcs_file": gcs_file_blob.configured({"prefix": REGISTRIES_FOLDER, "gcs_filename": "oss_registry.json"}),
    "latest_cloud_registry_gcs_file": gcs_file_blob.configured({"prefix": REGISTRIES_FOLDER, "gcs_filename": "cloud_registry.json"}),
}

SENSORS = [
    registry_updated_sensor(job=generate_registry_markdown, resources_def=RESOURCES),
    metadata_updated_sensor(job=generate_registry, resources_def=RESOURCES),
]

SCHEDULES = []

JOBS = [generate_registry_markdown, generate_local_metadata_files]

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
