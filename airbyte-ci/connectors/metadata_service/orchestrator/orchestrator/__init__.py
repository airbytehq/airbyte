from dagster import Definitions

from .resources.gcp_resources import gcp_gcs_client, gcs_bucket_manager, gcs_file_manager, gcs_file_blob
from .resources.github_resources import github_client, github_connector_repo, github_connectors_directory
from .resources.local_resources import simple_local_file_manager

from .assets.catalog_assets import (
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
    metadata_definitions,
    valid_metadata_list,
    write_metadata_definitions_to_filesystem,
)
from .assets.github_assets import source_controlled_connectors

from .jobs.catalog_jobs import generate_catalog_markdown
from .sensors.catalog_sensors import catalog_updated_sensor

from .config import REPORT_FOLDER, CATALOG_FOLDER, CONNECTORS_PATH, CONNECTOR_REPO_NAME


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
    source_controlled_connectors,
    metadata_definitions,
    valid_metadata_list,
    write_metadata_definitions_to_filesystem,
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

JOBS = [generate_catalog_markdown]

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
