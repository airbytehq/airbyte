from dagster import build_op_context

from orchestrator.resources.gcp import gcp_gcs_client, gcs_bucket_manager, gcs_file_manager, gcs_directory_blobs

from orchestrator.assets.registry import (
    persist_oss_registry_from_metadata,
)

from orchestrator.assets.metadata import (
    metadata_definitions,
)

from metadata_service.constants import METADATA_FILE_NAME, METADATA_FOLDER
from orchestrator.config import REGISTRIES_FOLDER


def debug_registry_generation():
    resources = {
        "gcp_gcs_client": gcp_gcs_client.configured(
            {
                "gcp_gcs_cred_string": {"env": "GCS_CREDENTIALS"},
            }
        ),
        "gcs_bucket_manager": gcs_bucket_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}}),
        "registry_directory_manager": gcs_file_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REGISTRIES_FOLDER}),
        "latest_metadata_file_blobs": gcs_directory_blobs.configured({"prefix": METADATA_FOLDER, "suffix": METADATA_FILE_NAME}),
    }

    context = build_op_context(resources=resources)
    metadata_definitions_asset = metadata_definitions(context)
    persist_oss_registry_from_metadata(context, metadata_definitions_asset).value
