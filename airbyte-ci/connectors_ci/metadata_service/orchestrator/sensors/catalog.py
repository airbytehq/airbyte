from typing import List
from dagster import sensor, RunRequest, SkipReason, build_op_context, MetadataValue, SensorEvaluationContext, build_resources, InitResourceContext, resource, DefaultSensorStatus, Definitions, Output, InitResourceContext, get_dagster_logger, asset, define_asset_job, OpExecutionContext

from ..resources.gcp import gcp_gcs_client, gcp_gsm_credentials, gcp_gcs_metadata_bucket
from ..resources.catalog import latest_oss_catalog_gcs_file, latest_cloud_catalog_gcs_file

from ..jobs.catalog import generate_catalog_markdown

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

    # TOOD apply this through the context
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

