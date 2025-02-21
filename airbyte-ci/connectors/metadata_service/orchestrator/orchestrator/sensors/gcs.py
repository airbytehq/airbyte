#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time

from dagster import (
    DefaultSensorStatus,
    RunRequest,
    SensorDefinition,
    SensorEvaluationContext,
    SensorResult,
    SkipReason,
    build_resources,
    sensor,
)
from orchestrator.logging import sentry
from orchestrator.utils.dagster_helpers import string_array_to_hash


def new_gcs_blobs_sensor(
    gcs_blobs_resource_key,
    job,
    interval,
    resources_def,
    allow_duplicate_runs=False,
) -> SensorDefinition:
    """
    This sensor is responsible for polling a list of gcs blobs and triggering a job when the list changes.
    """

    sensor_name = f"{job.name}_on_new_{gcs_blobs_resource_key}"

    @sensor(
        name=sensor_name,
        job=job,
        minimum_interval_seconds=interval,
        default_status=DefaultSensorStatus.STOPPED,
    )
    @sentry.instrument_sensor
    def new_gcs_blobs_sensor_definition(context: SensorEvaluationContext):
        with build_resources(resources_def) as resources:
            context.log.info(f"Got resources for {sensor_name}")

            context.log.info(f"Old etag cursor: {context.cursor}")

            gcs_blobs_resource = getattr(resources, gcs_blobs_resource_key)
            new_etags_cursor = string_array_to_hash([blob.etag for blob in gcs_blobs_resource])
            context.log.info(f"New etag cursor: {new_etags_cursor}")

            # Note: ETAGs are GCS's way of providing a version number for a file
            # Another option would be to use the last modified date or MD5 hash
            if context.cursor == new_etags_cursor:
                return SkipReason(f"No new {gcs_blobs_resource_key} in GCS bucket")

            context.update_cursor(new_etags_cursor)
            context.log.info(f"New {gcs_blobs_resource_key} in GCS bucket")
            run_key = f"{sensor_name}:{new_etags_cursor}"
            # Dagster skips runs with the same run_key
            # It means that if the GCS blob list changed back to a state which was already processed, the run will be skipped
            # This is not desirable in cases we want to reprocess the same data again after a blob deletion
            if allow_duplicate_runs:
                run_key += f":{int(time.time())}"
            return RunRequest(run_key=run_key)

    return new_gcs_blobs_sensor_definition


def new_gcs_blobs_partition_sensor(
    gcs_blobs_resource_key,
    job,
    interval,
    resources_def,
    partitions_def,
) -> SensorDefinition:
    """
    This sensor is responsible for polling a list of gcs blobs and triggering a partitioned job when the list changes.
    """
    MAX_RUN_REQUEST = 30
    sensor_name = f"{job.name}_on_new_{gcs_blobs_resource_key}"

    @sensor(
        name=sensor_name,
        job=job,
        minimum_interval_seconds=interval,
        default_status=DefaultSensorStatus.STOPPED,
    )
    @sentry.instrument_sensor
    def new_gcs_blobs_sensor_definition(context: SensorEvaluationContext):
        context.log.info(f"Starting {sensor_name}")

        with build_resources(resources_def) as resources:
            context.log.info(f"Got resources for {sensor_name}")

            context.log.info(f"Old etag cursor: {context.cursor}")

            gcs_blobs_resource = getattr(resources, gcs_blobs_resource_key)

            new_etags_found = [
                blob.etag for blob in gcs_blobs_resource if not context.instance.has_dynamic_partition(partitions_def.name, blob.etag)
            ]
            context.log.info(f"New etags found: {new_etags_found}")

            if not new_etags_found:
                return SkipReason(f"No new {gcs_blobs_resource_key} in GCS bucket")

            # if there are more than the MAX_RUN_REQUEST, we need to split them into multiple runs
            if len(new_etags_found) > MAX_RUN_REQUEST:
                new_etags_found = new_etags_found[:MAX_RUN_REQUEST]
                context.log.info(f"Only processing first {MAX_RUN_REQUEST} new blobs: {new_etags_found}")

            return SensorResult(
                run_requests=[RunRequest(partition_key=etag) for etag in new_etags_found],
                dynamic_partitions_requests=[partitions_def.build_add_request(new_etags_found)],
            )

    return new_gcs_blobs_sensor_definition
