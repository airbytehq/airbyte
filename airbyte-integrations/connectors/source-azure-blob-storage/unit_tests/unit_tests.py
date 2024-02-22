# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from source_azure_blob_storage.legacy_config_transformer import LegacyConfigTransformer


def test_config_convertation():
    legacy_config = {
        "azure_blob_storage_endpoint": "https://airbyteteststorage.blob.core.windows.net",
        "azure_blob_storage_account_name": "airbyteteststorage",
        "azure_blob_storage_account_key": "secret/key==",
        "azure_blob_storage_container_name": "airbyte-source-azure-blob-storage-test",
        "azure_blob_storage_blobs_prefix": "subfolder/",
        "azure_blob_storage_schema_inference_limit": 500,
        "format": "jsonl",
    }
    new_config = LegacyConfigTransformer.convert(legacy_config)
    assert new_config == {
        "azure_blob_storage_account_key": "secret/key==",
        "azure_blob_storage_account_name": "airbyteteststorage",
        "azure_blob_storage_container_name": "airbyte-source-azure-blob-storage-test",
        "azure_blob_storage_endpoint": "https://airbyteteststorage.blob.core.windows.net",
        "streams": [
            {
                "format": {"filetype": "jsonl"},
                "legacy_prefix": "subfolder/",
                "name": "airbyte-source-azure-blob-storage-test",
                "validation_policy": "Emit Record",
            }
        ],
    }
