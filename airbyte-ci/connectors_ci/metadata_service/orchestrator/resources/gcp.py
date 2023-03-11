import os
import json

from google.cloud import storage
from google.oauth2 import service_account

from dagster import sensor, RunRequest, SkipReason, build_op_context, MetadataValue, SensorEvaluationContext, build_resources, InitResourceContext, resource, DefaultSensorStatus, Definitions, Output, InitResourceContext, get_dagster_logger, asset, define_asset_job, OpExecutionContext

from ..config import BUCKET_NAME

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
