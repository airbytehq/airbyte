from dagster import sensor, RunRequest, SkipReason, SensorDefinition, SensorEvaluationContext, build_resources, DefaultSensorStatus
from orchestrator.utils.dagster_helpers import string_array_to_hash


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

            context.log.info(f"Old etag cursor: {context.cursor}")

            latest_metadata_file_blobs = resources.latest_metadata_file_blobs
            new_etags_cursor = string_array_to_hash([blob.etag for blob in latest_metadata_file_blobs])
            context.log.info(f"New etag cursor: {new_etags_cursor}")

            # Note: ETAGs are GCS's way of providing a version number for a file
            # Another option would be to use the last modified date or MD5 hash
            if context.cursor == new_etags_cursor:
                context.log.info("No new updated_metadata_files in GCS bucket")
                return SkipReason("No new updated_metadata_files in GCS bucket")

            context.update_cursor(new_etags_cursor)
            context.log.info("New updated_metadata_files in GCS bucket")
            run_key = f"updated_metadata_files:{new_etags_cursor}"
            return RunRequest(run_key=run_key)

    return metadata_updated_sensor_definition
