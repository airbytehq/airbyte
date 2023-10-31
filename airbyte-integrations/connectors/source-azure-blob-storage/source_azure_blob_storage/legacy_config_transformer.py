#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, MutableMapping


class LegacyConfigTransformer:
    """
    Class that takes in Azure Blob Storage source configs in the legacy format and transforms them into
    configs that can be used by the new Azure Blob Storage source built with the file-based CDK.
    """

    @classmethod
    def convert(cls, legacy_config: Mapping) -> MutableMapping[str, Any]:
        azure_blob_storage_blobs_prefix = legacy_config.get("azure_blob_storage_blobs_prefix", "")

        return {
            "azure_blob_storage_endpoint": legacy_config.get("azure_blob_storage_endpoint", None),
            "azure_blob_storage_account_name": legacy_config["azure_blob_storage_account_name"],
            "azure_blob_storage_account_key": legacy_config["azure_blob_storage_account_key"],
            "azure_blob_storage_container_name": legacy_config["azure_blob_storage_container_name"],
            "streams": [
                {
                    "name": legacy_config["azure_blob_storage_container_name"],
                    "legacy_prefix": azure_blob_storage_blobs_prefix,
                    "validation_policy": "Emit Record",
                    "format": {"filetype": "jsonl"},
                }
            ],
        }
