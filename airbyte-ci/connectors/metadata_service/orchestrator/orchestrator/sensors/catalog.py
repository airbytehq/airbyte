from typing import List, Optional
from dagster import sensor, RunRequest, SkipReason, SensorDefinition, SensorEvaluationContext, build_resources, DefaultSensorStatus

CURSOR_SEPARATOR = ":"

def deserialize_composite_etag_cursor(etag_cursor: Optional[str]) -> List[str]:
    if etag_cursor is None:
        return []

    return etag_cursor.split(CURSOR_SEPARATOR)

def serialize_composite_etag_cursor(etags: List[str]):
    return CURSOR_SEPARATOR.join(etags)


def catalog_updated_sensor(job, resources_def) -> SensorDefinition:
    """
    This sensor is responsible for polling the catalog folder in GCS for updates to our oss and cloud catalogs.
    If it has, it will trigger the given job.
    """

    @sensor(
        name=f"{job.name}_on_catalog_updated",
        job=job,
        minimum_interval_seconds=30,
        default_status=DefaultSensorStatus.STOPPED,
    )
    def catalog_updated_sensor_definition(context: SensorEvaluationContext):
        context.log.info("Starting gcs_catalog_updated_sensor")

        with build_resources(resources_def) as resources:
            context.log.info("Got resources for gcs_catalog_updated_sensor")

            etag_cursor = context.cursor or None
            context.log.info(f"Old etag cursor: {etag_cursor}")

            new_etag_cursor = serialize_composite_etag_cursor(
                [resources.latest_oss_catalog_gcs_file.etag, resources.latest_cloud_catalog_gcs_file.etag]
            )
            context.log.info(f"New etag cursor: {new_etag_cursor}")

            # Note: ETAGs are GCS's way of providing a version number for a file
            # Another option would be to use the last modified date or MD5 hash
            if etag_cursor == new_etag_cursor:
                context.log.info("No new catalogs in GCS bucket")
                return SkipReason("No new catalogs in GCS bucket")

            context.update_cursor(new_etag_cursor)  # Question: what happens if the run fails? is the cursor still updated?
            context.log.info("New catalogs in GCS bucket")
            return RunRequest(run_key="updated_catalogs")

    return catalog_updated_sensor_definition


def metadata_updated_sensor(job, resources_def) -> SensorDefinition:
    """
    TODO
    """

    @sensor(
        name=f"{job.name}_on_metadata_updated",
        job=job,
        minimum_interval_seconds=30,
        default_status=DefaultSensorStatus.STOPPED,
    )
    def metadata_updated_sensor_definition(context: SensorEvaluationContext):
        context.log.info("Starting gcs_metadata_updated_sensor")

        with build_resources(resources_def) as resources:
            context.log.info("Got resources for gcs_metadata_updated_sensor")

            etag_cursor_raw = context.cursor or None
            etag_cursor = deserialize_composite_etag_cursor(etag_cursor_raw)
            etag_cursor_set = set(etag_cursor)

            context.log.info(f"Old etag cursor: {etag_cursor}")

            metadata_folder_blobs = resources.metadata_folder_blobs
            new_etag_cursors = [blob.etag for blob in metadata_folder_blobs if blob.name.endswith("metadata.yml")]
            new_etag_cursor_set = set(new_etag_cursors)
            context.log.info(f"New etag cursor: {new_etag_cursor_set}")

            # Note: ETAGs are GCS's way of providing a version number for a file
            # Another option would be to use the last modified date or MD5 hash
            if etag_cursor_set == new_etag_cursor_set:
                context.log.info("No new updated_metadata_files in GCS bucket")
                return SkipReason("No new updated_metadata_files in GCS bucket")

            serialized_new_etag_cursor = serialize_composite_etag_cursor(new_etag_cursors)
            context.update_cursor(serialized_new_etag_cursor)  # Question: what happens if the run fails? is the cursor still updated?
            context.log.info("New updated_metadata_files in GCS bucket")
            return RunRequest(run_key="updated_metadata_files")

    return metadata_updated_sensor_definition
