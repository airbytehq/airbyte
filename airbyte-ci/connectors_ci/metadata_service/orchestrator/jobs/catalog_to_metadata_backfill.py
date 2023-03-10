import pandas as pd
import requests
import json
import os
import logging
from google.cloud import storage
from google.oauth2 import service_account

from dagster import sensor, RunRequest, SkipReason, op, job, SensorEvaluationContext, build_resources, InitResourceContext, resource, DefaultSensorStatus, Definitions, Field, InitResourceContext, String
from dagster_gcp.gcs import gcs_resource; # TODO: figure out how to use this

# from dagster_aws.s3.sensor import get_s3_keys
logger = logging.getLogger("catalog_to_metadata_backfill")

@op
def succeeds():
    logger.info("parse_catalog_files")
    return 1


@job
def parse_catalog_files():
    logger.info("parse_catalog_files")
    succeeds()

# TODO add types
# TODO move this to config so its available in resource_context
def get_gcs_cred_json_from_env():
    raw_cred = os.getenv("GCP_GSM_CREDENTIALS")
    if raw_cred is None:
        raise Exception("GCP_GSM_CREDENTIALS not set")

    return json.loads(raw_cred)

@resource(
    config_schema={
        "project_id": Field(
            String,
            is_required=True,
            description="service account project_id field",
        ),
        "client_x509_cert_url": Field(
            String,
            is_required=True,
            description="service account client_x509_cert_url field",
        ),
        "private_key_id": Field(
            String,
            is_required=True,
            description="service account private_key_id field",
        ),
        "auth_uri": Field(
            String,
            is_required=True,
            description="service account auth_uri field",
        ),
        "token_uri": Field(
            String,
            is_required=True,
            description="service account token_uri field",
        ),
        "client_id": Field(
            String,
            is_required=True,
            description="service account client_id field",
        ),
        "private_key": Field(
            String,
            is_required=True,
            description="service account private_key field",
        ),
        "client_email": Field(
            String,
            is_required=True,
            description="service account client_email field",
        ),
        "auth_provider_x509_cert_url": Field(
            String,
            is_required=True,
            description="TODO",
        ),
        "type": Field(
            String,
            is_required=True,
            description="TODO",
        ),
    }
)
def gcp_gcs_resource(resource_context: InitResourceContext):
    """Create a connection to gcs.
    :param resource_context: Dagster execution context for configuration data
    :type resource_context: InitResourceContext
    :yields: A gcs client instance for use during pipeline execution.
    """
    credentials = service_account.Credentials.from_service_account_info(resource_context)
    yield storage.Client(
        credentials=credentials,
        project=credentials.project_id,
    )

@sensor(
    name="gcs_catalog_updated_sensor",
    job=parse_catalog_files, minimum_interval_seconds=10,
    default_status=DefaultSensorStatus.RUNNING,
    )
def gcs_catalog_updated_sensor(context: SensorEvaluationContext):
    # TODO parse which catalog(s) we're watching
    context.log.info("Logging from a sensor!")
    # break point
    # import pdb; pdb.set_trace()

    gcp_gcs_cred = get_gcs_cred_json_from_env()
    config = {"gcp_gcs": {"config": gcp_gcs_cred}}

    with build_resources(
        resources={"gcp_gcs": gcp_gcs_resource}, resource_config=config
    ) as resources:
        storage_client = resources.gcp_gcs
        bucket = storage_client.get_bucket("ben-ab-test-bucket") # TODO move to config
        new_files = storage_client.list_blobs(bucket)
        if new_files:
            # TODO use a better cursor than the list of files
            context.update_cursor(str(new_files)) # Question: what happens if the run fails? is the cursor still updated?
            yield RunRequest(
                run_key="new_gcs_file",
                run_config=config,
            )
        else:
            yield SkipReason("No new files in GCS bucket")

# Question: Do we have to wire these up?
defn = Definitions(
    # assets=all_assets,
    # resources=resources_by_deployment_name[deployment_name],
    # schedules=[core_assets_schedule],
    sensors=[gcs_catalog_updated_sensor],
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
