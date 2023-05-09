from dagster import sensor, RunRequest, SkipReason, SensorDefinition, SensorEvaluationContext, build_resources, DefaultSensorStatus

from orchestrator.utils.dagster_helpers import serialize_composite_etags_cursor


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

            new_etag_cursor = serialize_composite_etags_cursor(
                [resources.latest_oss_catalog_gcs_file.etag, resources.latest_cloud_catalog_gcs_file.etag]
            )
            context.log.info(f"New etag cursor: {new_etag_cursor}")

            # Note: ETAGs are GCS's way of providing a version number for a file
            # Another option would be to use the last modified date or MD5 hash
            if etag_cursor == new_etag_cursor:
                context.log.info("No new catalogs in GCS bucket")
                return SkipReason("No new catalogs in GCS bucket")

            context.update_cursor(new_etag_cursor)
            context.log.info("New catalogs in GCS bucket")
            return RunRequest(run_key="updated_catalogs")

    return catalog_updated_sensor_definition
