from dagster import sensor, RunRequest, SkipReason, build_op_context, MetadataValue, SensorEvaluationContext, build_resources, InitResourceContext, resource, DefaultSensorStatus, Definitions, Output, InitResourceContext, get_dagster_logger, asset, define_asset_job, OpExecutionContext
from ..config import BUCKET_NAME, CATALOG_FOLDER

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
