#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dagster import AssetSelection, SkipReason, define_asset_job, job, op
from orchestrator.assets import metadata, registry, registry_entry, specs_secrets_mask
from orchestrator.config import HIGH_QUEUE_PRIORITY, MAX_METADATA_PARTITION_RUN_REQUEST
from orchestrator.logging.publish_connector_lifecycle import PublishConnectorLifecycle, PublishConnectorLifecycleStage, StageStatus

oss_registry_inclusive = AssetSelection.keys("persisted_oss_registry", "specs_secrets_mask_yaml").upstream()
generate_oss_registry = define_asset_job(name="generate_oss_registry", selection=oss_registry_inclusive)


cloud_registry_inclusive = AssetSelection.keys("persisted_cloud_registry", "specs_secrets_mask_yaml").upstream()
generate_cloud_registry = define_asset_job(name="generate_cloud_registry", selection=cloud_registry_inclusive)

registry_reports_inclusive = AssetSelection.keys("connector_registry_report").upstream()
generate_registry_reports = define_asset_job(name="generate_registry_reports", selection=registry_reports_inclusive)

registry_entry_inclusive = AssetSelection.keys("registry_entry").upstream()
generate_registry_entry = define_asset_job(
    name="generate_registry_entry",
    selection=registry_entry_inclusive,
    partitions_def=registry_entry.metadata_partitions_def,
)


@op(required_resource_keys={"all_metadata_file_blobs"})
def remove_stale_metadata_partitions_op(context):
    """
    This op is responsible for polling for new metadata files and adding their etag to the dynamic partition.
    """
    all_metadata_file_blobs = context.resources.all_metadata_file_blobs
    partition_name = registry_entry.metadata_partitions_def.name

    all_fresh_etags = [blob.etag for blob in all_metadata_file_blobs]
    context.log.info(f"Found {len(all_fresh_etags)} fresh metadata files found in GCS bucket")

    all_etag_partitions = context.instance.get_dynamic_partitions(partition_name)
    context.log.info(f"Found {len(all_etag_partitions)} existing metadata partitions")

    for stale_etag in [etag for etag in all_etag_partitions if etag not in all_fresh_etags]:
        context.log.info(f"Removing stale etag: {stale_etag}")
        context.instance.delete_dynamic_partition(partition_name, stale_etag)
        context.log.info(f"Removed stale etag: {stale_etag}")


@job(tags={"dagster/priority": HIGH_QUEUE_PRIORITY})
def remove_stale_metadata_partitions():
    """
    This job is responsible for removing stale metadata partitions (metadata files or versions of files that no longer exist).
    """
    remove_stale_metadata_partitions_op()


@op(required_resource_keys={"latest_metadata_file_blobs"})
def remove_latest_metadata_partitions_op(context):
    """
    This op is responsible for removing for latest metadata files. (Generally used to reprocess metadata files).
    """
    latest_metadata_file_blobs = context.resources.latest_metadata_file_blobs
    partition_name = registry_entry.metadata_partitions_def.name

    all_latest = [blob.etag for blob in latest_metadata_file_blobs]
    context.log.info(f"Found {len(all_latest)} latest metadata files found in GCS bucket")

    all_etag_partitions = context.instance.get_dynamic_partitions(partition_name)
    context.log.info(f"Found {len(all_etag_partitions)} existing metadata partitions")

    for latest_etag in all_latest:
        if latest_etag in all_etag_partitions:
            context.log.info(f"Removing latest etag: {latest_etag}")
            context.instance.delete_dynamic_partition(partition_name, latest_etag)
            context.log.info(f"Removed latest etag: {latest_etag}")


@job(tags={"dagster/priority": HIGH_QUEUE_PRIORITY})
def remove_latest_metadata_partitions():
    """
    This job is responsible for removing latest metadata partitions. (Generally used to reprocess metadata files).
    """
    remove_latest_metadata_partitions_op()


@op(required_resource_keys={"slack", "all_metadata_file_blobs"})
def add_new_metadata_partitions_op(context):
    """
    This op is responsible for polling for new metadata files and adding their etag to the dynamic partition.
    """
    context.log.info("Starting add_new_metadata_partitions_op")

    all_metadata_file_blobs = context.resources.all_metadata_file_blobs
    context.log.info(f"Found {len(all_metadata_file_blobs)} metadata files found in GCS bucket")

    partition_name = registry_entry.metadata_partitions_def.name
    existing_partitions = context.instance.get_dynamic_partitions(partition_name)
    context.log.info(f"Found {len(existing_partitions)} existing metadata partitions")

    new_files_found = {blob.etag: blob.name for blob in all_metadata_file_blobs if not blob.etag in existing_partitions}

    new_etags_found = list(new_files_found.keys())
    context.log.info(f"New etags found: {new_etags_found}")

    if not new_etags_found:
        return SkipReason(f"No new metadata files to process in GCS bucket")

    # if there are more than the MAX_METADATA_PARTITION_RUN_REQUEST, we need to split them into multiple runs
    etags_to_process = new_etags_found
    if len(new_etags_found) > MAX_METADATA_PARTITION_RUN_REQUEST:
        etags_to_process = etags_to_process[:MAX_METADATA_PARTITION_RUN_REQUEST]
        context.log.info(f"Only processing first {MAX_METADATA_PARTITION_RUN_REQUEST} new blobs: {etags_to_process}")

    context.instance.add_dynamic_partitions(partition_name, etags_to_process)

    # format new_files_found into a loggable string
    new_metadata_log_string = "\n".join([f"{new_files_found[etag]} *{etag}* " for etag in etags_to_process])

    PublishConnectorLifecycle.log(
        context,
        PublishConnectorLifecycleStage.METADATA_SENSOR,
        StageStatus.SUCCESS,
        f"*Queued {len(etags_to_process)}/{len(new_etags_found)} new metadata files for processing:*\n\n {new_metadata_log_string}",
    )


@job(tags={"dagster/priority": HIGH_QUEUE_PRIORITY})
def add_new_metadata_partitions():
    """
    This job is responsible for polling for new metadata files and adding their etag to the dynamic partition.
    """
    add_new_metadata_partitions_op()
