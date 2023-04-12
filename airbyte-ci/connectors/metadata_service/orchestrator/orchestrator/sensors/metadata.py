from dagster import sensor, RunRequest, SkipReason, SensorDefinition, SensorEvaluationContext, build_resources, DefaultSensorStatus
from orchestrator.utils.dagster_helpers import deserialize_composite_etag_cursor, serialize_composite_etag_cursor


def metadata_updated_sensor(job, resources_def) -> SensorDefinition:
    """
    This sensor is responsible for polling the metadata folder in GCS for new or updated metadata files.
    If it notices that the etags have changed, it will trigger the given job.
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
            ## TODO, yaml vs yml
            new_etag_cursors = [blob.etag for blob in metadata_folder_blobs if blob.name.endswith("metadata.yaml")]
            new_etag_cursor_set = set(new_etag_cursors)
            context.log.info(f"New etag cursor: {new_etag_cursor_set}")

            # Note: ETAGs are GCS's way of providing a version number for a file
            # Another option would be to use the last modified date or MD5 hash
            if etag_cursor_set == new_etag_cursor_set:
                context.log.info("No new updated_metadata_files in GCS bucket")
                return SkipReason("No new updated_metadata_files in GCS bucket")

            serialized_new_etag_cursor = serialize_composite_etag_cursor(new_etag_cursors)
            context.update_cursor(serialized_new_etag_cursor)
            context.log.info("New updated_metadata_files in GCS bucket")
            return RunRequest(run_key="updated_metadata_files")

    return metadata_updated_sensor_definition
