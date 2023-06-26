from dagster import (
    DynamicPartitionsDefinition,
    asset,
)

GROUP_NAME = "registry_entry"

metadata_partitions_def = DynamicPartitionsDefinition(name="metadata")

@asset(required_resource_keys={"latest_metadata_file_blobs"}, group_name=GROUP_NAME, partitions_def=metadata_partitions_def)
def registry_entry(context):
    etag = context.partition_key
    latest_metadata_file_blobs = context.resources.latest_metadata_file_blobs

    # find the blob with the matching etag
    matching_blob = next(
        (blob for blob in latest_metadata_file_blobs if blob.etag == etag), None
    )

    if not matching_blob:
        raise Exception(f"Could not find blob with etag {etag}")

    # read the blob
    filename = matching_blob.name
    return filename
