from typing import List
import pandas as pd
import requests
import json
import os
import logging
from google.cloud import storage
from google.oauth2 import service_account

from dagster import sensor, RunRequest, SkipReason, op, job, SensorEvaluationContext, build_resources, InitResourceContext, resource, DefaultSensorStatus, Definitions, Output, InitResourceContext, get_dagster_logger, asset, define_asset_job
from dagster_gcp.gcs import gcs_resource; # TODO: figure out how to use this

# from dagster_aws.s3.sensor import get_s3_keys
logger = get_dagster_logger()

# move to config -> metadata service
BUCKET_NAME = "ben-ab-test-bucket"
CATALOG_FOLDER = "catalogs"

# ------ Assets ------ #



@asset
def cloud_sources_dataframe(latest_cloud_catalog_dict):
    sources = latest_cloud_catalog_dict["sources"]
    return pd.DataFrame(sources)

@asset
def oss_sources_dataframe(latest_oss_catalog_dict):
    sources = latest_oss_catalog_dict["sources"]
    return pd.DataFrame(sources)

@asset
def cloud_destinations_dataframe(latest_cloud_catalog_dict):
    destinations = latest_cloud_catalog_dict["destinations"]
    return pd.DataFrame(destinations)

@asset
def oss_destinations_dataframe(latest_oss_catalog_dict):
    destinations = latest_oss_catalog_dict["destinations"]
    return pd.DataFrame(destinations)

@asset(required_resource_keys={"latest_cloud_catalog_gcs_file"})
def latest_cloud_catalog_dict(context):
    oss_catalog_file = context.resources.latest_cloud_catalog_gcs_gcs_file
    json_string = oss_catalog_file.download_as_string().decode('utf-8')
    oss_catalog_dict = json.loads(json_string)
    return oss_catalog_dict

# TODO add partitions
@asset(required_resource_keys={"latest_oss_catalog_gcs_file"})
def latest_oss_catalog_dict(context):
    oss_catalog_file = context.resources.latest_oss_catalog_gcs_file
    json_string = oss_catalog_file.download_as_string().decode('utf-8')
    oss_catalog_dict = json.loads(json_string)
    return oss_catalog_dict


# ------ Resources ------ #

@resource(required_resource_keys={"gcp_gcs_metadata_bucket"})
def latest_oss_catalog_gcs_file(resource_context: InitResourceContext):
    resource_context.log.info("retrieving latest_oss_catalog_gcs_file")
    bucket = resource_context.resources.gcp_gcs_metadata_bucket
    oss_catalog_path = f"{CATALOG_FOLDER}/oss_catalog.json"
    oss_catalog_file = bucket.get_blob(oss_catalog_path)
    if not oss_catalog_file.exists():
        raise Exception(f"OSS catalog file does not exist in GCS bucket: {BUCKET_NAME} at path: {oss_catalog_path}")

    return oss_catalog_file;

@resource(required_resource_keys={"gcp_gcs_metadata_bucket"})
def latest_cloud_catalog_gcs_file(resource_context: InitResourceContext):
    resource_context.log.info("retrieving latest_cloud_catalog_gcs_file")
    bucket = resource_context.resources.gcp_gcs_metadata_bucket
    cloud_catalog_path = f"{CATALOG_FOLDER}/cloud_catalog.json"
    cloud_catalog_file = bucket.get_blob(cloud_catalog_path);
    if not cloud_catalog_file.exists():
        raise Exception(f"Cloud catalog file does not exist in GCS bucket: {BUCKET_NAME} at path: {cloud_catalog_path}")

    return cloud_catalog_file;


@resource()
def gcp_gsm_credentials(resource_context: InitResourceContext):
    resource_context.log.info("retrieving gcp_gsm_credentials")

    raw_cred = os.getenv("GCP_GSM_CREDENTIALS")
    if raw_cred is None:
        raise Exception("GCP_GSM_CREDENTIALS not set")

    return json.loads(raw_cred)

@resource(required_resource_keys={"gcp_gsm_credentials"})
def gcp_gcs_client(resource_context: InitResourceContext):
    """Create a connection to gcs.
    :param resource_context: Dagster execution context for configuration data
    :type resource_context: InitResourceContext
    :yields: A gcs client instance for use during pipeline execution.
    """
    resource_context.log.info("retrieving gcp_gcs_client")

    credentials = service_account.Credentials.from_service_account_info(resource_context.resources.gcp_gsm_credentials)
    return storage.Client(
        credentials=credentials,
        project=credentials.project_id,
    )

@resource(required_resource_keys={"gcp_gcs_client"})
def gcp_gcs_metadata_bucket(resource_context: InitResourceContext):
    """Create a connection to gcs.
    :param resource_context: Dagster execution context for configuration data
    :type resource_context: InitResourceContext
    :yields: A gcs client instance for use during pipeline execution.
    """
    resource_context.log.info("retrieving gcp_gcs_metadata_bucket")

    storage_client = resource_context.resources.gcp_gcs_client
    return storage_client.get_bucket(BUCKET_NAME)


# ------ Jobs ------ #

# todo kick off the final asset creation
generate_catalog_markdown = define_asset_job(name="generate_catalog_markdown", selection="oss_destinations_dataframe")

# ------ Sensors ------ #

def generate_composite_etag_cursor(etags: List[str]):
    return ":".join(etags)

@sensor(
    name="gcs_catalog_updated_sensor",
    job=generate_catalog_markdown,
    minimum_interval_seconds=30, # Todo have a dev and prod version of this
    default_status=DefaultSensorStatus.STOPPED,
    )
def gcs_catalog_updated_sensor(context: SensorEvaluationContext):
    # TODO parse which catalog(s) we're watching
    context.log.info("Starting gcs_catalog_updated_sensor")

    with build_resources({
        "gcp_gcs_client": gcp_gcs_client,
        "gcp_gsm_credentials": gcp_gsm_credentials,
        "gcp_gcs_metadata_bucket": gcp_gcs_metadata_bucket,
        "latest_oss_catalog_gcs_file": latest_oss_catalog_gcs_file,
        "latest_cloud_catalog_gcs_file": latest_cloud_catalog_gcs_file
    }
    ) as resources:
        context.log.info("Got resources for gcs_catalog_updated_sensor")

        etag_cursor = context.cursor or None
        context.log.info(f"Old etag cursor: {etag_cursor}")

        new_etag_cursor = generate_composite_etag_cursor([resources.latest_oss_catalog_gcs_file.etag, resources.latest_cloud_catalog_gcs_file.etag])
        context.log.info(f"New etag cursor: {new_etag_cursor}")

        # Note: ETAGs are GCS's way of providing a version number for a file
        # Another option would be to use the last modified date or MD5 hash
        if etag_cursor == new_etag_cursor:
            context.log.info("No new catalogs in GCS bucket")
            return SkipReason("No new catalogs in GCS bucket")

        context.update_cursor(new_etag_cursor) # Question: what happens if the run fails? is the cursor still updated?
        context.log.info("New catalogs in GCS bucket")
        return RunRequest(run_key="updated_catalogs")

# ------ Definitions ------ #

# TODO move to a generic location
# todo turn into a repository representation
defn = Definitions(
    assets=[
        oss_destinations_dataframe,
        cloud_destinations_dataframe,
        oss_sources_dataframe,
        cloud_sources_dataframe,
        latest_oss_catalog_dict,
        latest_cloud_catalog_dict,
    ],
    jobs=[generate_catalog_markdown],
    resources={
        "gcp_gsm_credentials": gcp_gsm_credentials,
        "gcp_gcs_client": gcp_gcs_client,
        "gcp_gcs_metadata_bucket": gcp_gcs_metadata_bucket,
        "latest_oss_catalog_gcs_file": latest_oss_catalog_gcs_file,
        "latest_cloud_catalog_gcs_file": latest_cloud_catalog_gcs_file
    },
    schedules=[],
    sensors=[gcs_catalog_updated_sensor], # todo allow us to watch both the cloud and oss catalog
)
