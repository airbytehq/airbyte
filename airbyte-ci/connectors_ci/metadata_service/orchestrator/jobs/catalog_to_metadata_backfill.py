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

@op
def succeeds():
    return 1

@asset(required_resource_keys={"latest_oss_catalog"})
def oss_catalog_dataframe(context):
    oss_catalog_file = context.resources.latest_oss_catalog
    json_string = oss_catalog_file.download_as_string().decode('utf-8')
    return pd.read_json(json_string)

# @job
# def generate_catalog_markdown():
#     logger.info("generate_catalog_markdown")

#     oss_df = oss_catalog_dataframe()
#     logger.info(f"oss_catalog_dataframe: {dir(oss_df)}")

#         # recorded metadata can be customized
#     metadata = {
#         # "num_records": len(oss_df),
#         "preview": oss_df,
#     }
#     return Output(value=oss_df, metadata=metadata)

generate_catalog_markdown = define_asset_job(name="generate_catalog_markdown", selection="oss_catalog_dataframe")

# TODO add types
# TODO move this to config so its available in resource_context



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


@resource(required_resource_keys={"gcp_gcs_metadata_bucket"})
def latest_oss_catalog(resource_context: InitResourceContext):
    resource_context.log.info("retrieving latest_oss_catalog")
    bucket = resource_context.resources.gcp_gcs_metadata_bucket
    oss_catalog_path = f"{CATALOG_FOLDER}/oss_catalog.json"
    oss_catalog_file = bucket.get_blob(oss_catalog_path)
    if not oss_catalog_file.exists():
        raise Exception(f"OSS catalog file does not exist in GCS bucket: {BUCKET_NAME} at path: {oss_catalog_path}")

    return oss_catalog_file;

@resource(required_resource_keys={"gcp_gcs_metadata_bucket"})
def latest_cloud_catalog(resource_context: InitResourceContext):
    resource_context.log.info("retrieving latest_cloud_catalog")
    bucket = resource_context.resources.gcp_gcs_metadata_bucket
    cloud_catalog_path = f"{CATALOG_FOLDER}/cloud_catalog.json"
    cloud_catalog_file = bucket.get_blob(cloud_catalog_path);
    if not cloud_catalog_file.exists():
        raise Exception(f"Cloud catalog file does not exist in GCS bucket: {BUCKET_NAME} at path: {cloud_catalog_path}")

    return cloud_catalog_file;

def generate_composite_etag_cursor(etags: List[str]):
    return ":".join(etags)

@sensor(
    name="gcs_catalog_updated_sensor",
    job=generate_catalog_markdown,
    minimum_interval_seconds=30, # Todo have a dev and prod version of this
    default_status=DefaultSensorStatus.RUNNING,
    )
def gcs_catalog_updated_sensor(context: SensorEvaluationContext):
    # TODO parse which catalog(s) we're watching
    context.log.info("Starting gcs_catalog_updated_sensor")

    with build_resources({
        "gcp_gcs_client": gcp_gcs_client,
        "gcp_gsm_credentials": gcp_gsm_credentials,
        "gcp_gcs_metadata_bucket": gcp_gcs_metadata_bucket,
        "latest_oss_catalog": latest_oss_catalog,
        "latest_cloud_catalog": latest_cloud_catalog
    }
    ) as resources:
        context.log.info("Got resources for gcs_catalog_updated_sensor")

        etag_cursor = context.cursor or None
        context.log.info(f"Old etag cursor: {etag_cursor}")

        new_etag_cursor = generate_composite_etag_cursor([resources.latest_oss_catalog.etag, resources.latest_cloud_catalog.etag])
        context.log.info(f"New etag cursor: {new_etag_cursor}")

        # Note: ETAGs are GCS's way of providing a version number for a file
        # Another option would be to use the last modified date or MD5 hash
        if etag_cursor == new_etag_cursor:
            context.log.info("No new catalogs in GCS bucket")
            return SkipReason("No new catalogs in GCS bucket")

        context.update_cursor(new_etag_cursor) # Question: what happens if the run fails? is the cursor still updated?
        context.log.info("New catalogs in GCS bucket")
        return RunRequest(run_key="updated_catalogs")

# TODO move to a generic location
defn = Definitions(
    assets=[oss_catalog_dataframe],
    jobs=[generate_catalog_markdown],
    resources={
        "gcp_gsm_credentials": gcp_gsm_credentials,
        "gcp_gcs_client": gcp_gcs_client,
        "gcp_gcs_metadata_bucket": gcp_gcs_metadata_bucket,
        "latest_oss_catalog": latest_oss_catalog,
        "latest_cloud_catalog": latest_cloud_catalog
    },
    schedules=[],
    sensors=[gcs_catalog_updated_sensor], # todo allow us to watch both the cloud and oss catalog
)

# from: https://github.com/mitodl/ol-data-platform/blob/59b785ab6bd5d73a05d598c9b39bfc8fa4eec65c/src/ol_orchestrate/sensors/sync_gcs_to_s3.py#L7
# def check_new_gcs_assets_sensor(context: SensorEvaluationContext):
#     gcs_config = load_yaml_config("/etc/dagster/edxorg_gcp.yaml")
#     with build_resources(
#         resources={"gcp_gcs": gcp_gcs_resource}, resource_config=gcs_config["resources"]
#     ) as resources:
#         storage_client = resources.gcp_gcs
#         bucket = storage_client.get_bucket("simeon-mitx-course-tarballs")
#         new_files = storage_client.list_blobs(bucket)
#         if new_files:
#             context.update_cursor(str(new_files))
#             yield RunRequest(
#                 run_key="new_gcs_file",
#                 run_config=gcs_config,
#             )
#         else:
#             yield SkipReason("No new files in GCS bucket")


# edx_gcs_courses = Definitions(
#     sensors=[
#         SensorDefinition(
#             evaluation_fn=check_new_gcs_assets_sensor,
#             minimum_interval_seconds=86400,
#             job=gcs_sync_job,
#             default_status=DefaultSensorStatus.RUNNING,
#         )
#     ],
#     jobs=[gcs_sync_job],
# )


# @asset
# def hackernews_top_story_ids():
#     """
#     Get top stories from the HackerNews top stories endpoint.
#     API Docs: https://github.com/HackerNews/API#new-top-and-best-stories
#     """
#     top_story_ids = requests.get(
#         "https://hacker-news.firebaseio.com/v0/topstories.json"
#     ).json()
#     return top_story_ids[:10]


# # asset dependencies can be inferred from parameter names
# @asset
# def hackernews_top_stories(hackernews_top_story_ids):
#     """Get items based on story ids from the HackerNews items endpoint"""
#     results = []
#     for item_id in hackernews_top_story_ids:
#         item = requests.get(
#             f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
#         ).json()
#         results.append(item)

#     df = pd.DataFrame(results)

#     # recorded metadata can be customized
#     metadata = {
#         "num_records": len(df),
#         "preview": MetadataValue.md(df[["title", "by", "url"]].to_markdown()),
#     }

#     return Output(value=df, metadata=metadata)
