import json

from google.cloud import storage
from google.oauth2 import service_account

from dagster import StringSource, InitResourceContext, resource, InitResourceContext, Field
from dagster_gcp.gcs.file_manager import GCSFileManager

from ..config import BUCKET_NAME

@resource(config_schema={"gcp_gsm_cred_string": StringSource})
def gcp_gcs_client(resource_context: InitResourceContext):
    """Create a connection to gcs.
    :param resource_context: Dagster execution context for configuration data
    :type resource_context: InitResourceContext
    :yields: A gcs client instance for use during pipeline execution.
    """
    resource_context.log.info("retrieving gcp_gcs_client")
    gcp_gsm_cred_string = resource_context.resource_config["gcp_gsm_cred_string"]
    gcp_gsm_cred_json = json.loads(gcp_gsm_cred_string)
    credentials = service_account.Credentials.from_service_account_info(gcp_gsm_cred_json)
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


@resource(
    required_resource_keys={"gcp_gcs_client"},
    config_schema={
        "gcs_bucket": StringSource,
        "gcs_prefix": Field(StringSource, is_required=False, default_value="dagster"),
    },
)
def gcs_file_manager(resource_context):
    """FileManager that provides abstract access to GCS.

    Implements the :py:class:`~dagster._core.storage.file_manager.FileManager` API.
    """

    storage_client = resource_context.resources.gcp_gcs_client

    return GCSFileManager(
        client=storage_client,
        gcs_bucket=resource_context.resource_config["gcs_bucket"],
        gcs_base_key=resource_context.resource_config["gcs_prefix"],
    )
