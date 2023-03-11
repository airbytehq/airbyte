from typing import List
import pandas as pd
import requests
import json
import os
import logging
from google.cloud import storage
from google.oauth2 import service_account

from dagster import sensor, RunRequest, SkipReason, build_op_context, MetadataValue, SensorEvaluationContext, build_resources, InitResourceContext, resource, DefaultSensorStatus, Definitions, Output, InitResourceContext, get_dagster_logger, asset, define_asset_job, OpExecutionContext
from dagster_gcp.gcs import gcs_resource; # TODO: figure out how to use this

# from dagster_aws.s3.sensor import get_s3_keys
logger = get_dagster_logger()

# move to config -> metadata service
BUCKET_NAME = "ben-ab-test-bucket"
CATALOG_FOLDER = "catalogs"
REPORT_FOLDER = "generated_reports"

# ------ helpers ------ #

def html_body(title, content):
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>{title}</title>
        </head>
        <body>
            {content}
        </body>
    </html>
    """


# ------ Assets ------ #

@asset(required_resource_keys={"gcp_gcs_metadata_bucket"})
def connector_catalog_location_html(context, all_destinations_dataframe, all_sources_dataframe):
    title = "Connector Catalogs"
    content = f"<h1>{title}</h1>"
    content += f"<h2>Sources</h2>"
    content += all_sources_dataframe.to_html()
    content += f"<h2>Destinations</h2>"
    content += all_destinations_dataframe.to_html()

    html = html_body(title, content)

    bucket = context.resources.gcp_gcs_metadata_bucket
    blob = bucket.blob(f"{REPORT_FOLDER}/connector_catalog_locations.html")
    blob.upload_from_string(html)
    blob.content_type = "text/html"
    blob.patch()

    public_url = blob.public_url

    metadata = {
        "public_url": MetadataValue.url(public_url),
    }
    return Output(metadata=metadata, value=html)

@asset(required_resource_keys={"gcp_gcs_metadata_bucket"})
def connector_catalog_location_markdown(context, all_destinations_dataframe, all_sources_dataframe):
    markdown = f"# Connector Catalog Locations\n\n"
    markdown += f"## Sources\n"
    markdown += all_sources_dataframe.to_markdown()
    markdown += f"\n\n## Destinations\n"
    markdown += all_destinations_dataframe.to_markdown()

    bucket = context.resources.gcp_gcs_metadata_bucket

    blob = bucket.blob(f"{REPORT_FOLDER}/connector_catalog_locations.md")
    blob.upload_from_string(markdown)

    public_url = blob.public_url

    metadata = {
        "preview": MetadataValue.md(markdown),
        "public_url": MetadataValue.url(public_url),
    }
    return Output(metadata=metadata, value=markdown)

@asset
def all_destinations_dataframe(cloud_destinations_dataframe, oss_destinations_dataframe):
    # Add a column 'is_cloud' to indicate if an image/version pair is in the cloud catalog
    cloud_destinations_dataframe['is_cloud'] = True

    # Add a column 'is_oss' to indicate if an image/version pair is in the oss catalog
    oss_destinations_dataframe['is_oss'] = True

    composite_key = ['dockerRepository', 'dockerImageTag']

    # Merge the two catalogs on the 'image' and 'version' columns, keeping only the unique pairs
    merged_catalog = pd.merge(cloud_destinations_dataframe, oss_destinations_dataframe, how='outer', on=composite_key).drop_duplicates(subset=composite_key)

    # Replace NaN values in the 'is_cloud' and 'is_oss' columns with False
    merged_catalog[['is_cloud', 'is_oss']] = merged_catalog[['is_cloud', 'is_oss']].fillna(False)

    # Return the merged catalog with the desired columns
    return merged_catalog[['name_x', 'dockerRepository', 'dockerImageTag', 'is_oss', 'is_cloud']]


@asset
def all_sources_dataframe(cloud_sources_dataframe, oss_sources_dataframe):
    # Add a column 'is_cloud' to indicate if an image/version pair is in the cloud catalog
    cloud_sources_dataframe['is_cloud'] = True

    # Add a column 'is_oss' to indicate if an image/version pair is in the oss catalog
    oss_sources_dataframe['is_oss'] = True

    composite_key = ['dockerRepository', 'dockerImageTag']

    # Merge the two catalogs on the 'image' and 'version' columns, keeping only the unique pairs
    merged_catalog = pd.merge(cloud_sources_dataframe, oss_sources_dataframe, how='outer', on=composite_key).drop_duplicates(subset=composite_key)

    # Replace NaN values in the 'is_cloud' and 'is_oss' columns with False
    merged_catalog[['is_cloud', 'is_oss']] = merged_catalog[['is_cloud', 'is_oss']].fillna(False)

    # Return the merged catalog with the desired columns
    return merged_catalog[['name_x', 'dockerRepository', 'dockerImageTag', 'is_oss', 'is_cloud']]

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
def latest_cloud_catalog_dict(context: OpExecutionContext):
    oss_catalog_file = context.resources.latest_cloud_catalog_gcs_file
    json_string = oss_catalog_file.download_as_string().decode('utf-8')
    oss_catalog_dict = json.loads(json_string)
    return oss_catalog_dict

# TODO add partitions
@asset(required_resource_keys={"latest_oss_catalog_gcs_file"})
def latest_oss_catalog_dict(context: OpExecutionContext):
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

# Generate all
generate_catalog_markdown = define_asset_job(name="generate_catalog_markdown", selection="connector_catalog_location_markdown")

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
        all_sources_dataframe,
        all_destinations_dataframe,
        connector_catalog_location_markdown,
        connector_catalog_location_html,
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

def debug_catalog_projection():
    context = build_op_context(resources={
        "gcp_gsm_credentials": gcp_gsm_credentials,
        "gcp_gcs_client": gcp_gcs_client,
        "gcp_gcs_metadata_bucket": gcp_gcs_metadata_bucket,
        "latest_oss_catalog_gcs_file": latest_oss_catalog_gcs_file,
        "latest_cloud_catalog_gcs_file": latest_cloud_catalog_gcs_file
    })
    cloud_catalog_dict = latest_cloud_catalog_dict(context)
    cloud_destinations_df = cloud_destinations_dataframe(cloud_catalog_dict)
    cloud_sources_df = cloud_sources_dataframe(cloud_catalog_dict)

    oss_catalog_dict = latest_oss_catalog_dict(context)
    oss_destinations_df = oss_destinations_dataframe(oss_catalog_dict)
    oss_sources_df = oss_sources_dataframe(oss_catalog_dict)

    all_sources_df = all_sources_dataframe(cloud_sources_df, oss_sources_df)
    all_destinations_df = all_destinations_dataframe(cloud_destinations_df, oss_destinations_df)

    connector_catalog_location_html(context, all_sources_df, all_destinations_df)

# debug_catalog_projection()
