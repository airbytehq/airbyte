from dagster import define_asset_job, AssetSelection, job, SkipReason, op
from orchestrator.assets import registry_entry
from orchestrator.config import MAX_METADATA_PARTITION_RUN_REQUEST, HIGH_QUEUE_PRIORITY

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
def add_new_metadata_partitions_op(context):
    """
    This op is responsible for polling for new metadata files and adding their etag to the dynamic partition.
    """
    all_metadata_file_blobs = context.resources.all_metadata_file_blobs
    partition_name = registry_entry.metadata_partitions_def.name

    new_etags_found = [
        blob.etag for blob in all_metadata_file_blobs if not context.instance.has_dynamic_partition(partition_name, blob.etag)
    ]

    context.log.info(f"New etags found: {new_etags_found}")

    if not new_etags_found:
        return SkipReason(f"No new metadata files to process in GCS bucket")

    # if there are more than the MAX_METADATA_PARTITION_RUN_REQUEST, we need to split them into multiple runs
    if len(new_etags_found) > MAX_METADATA_PARTITION_RUN_REQUEST:
        new_etags_found = new_etags_found[:MAX_METADATA_PARTITION_RUN_REQUEST]
        context.log.info(f"Only processing first {MAX_METADATA_PARTITION_RUN_REQUEST} new blobs: {new_etags_found}")

    context.instance.add_dynamic_partitions(partition_name, new_etags_found)


@job(tags={"dagster/priority": HIGH_QUEUE_PRIORITY})
def add_new_metadata_partitions():
    """
    This job is responsible for polling for new metadata files and adding their etag to the dynamic partition.
    """
    add_new_metadata_partitions_op()
