# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import dpath.util
from source_azure_blob_storage import SourceAzureBlobStorageSpec


def test_spec():
    config = SourceAzureBlobStorageSpec(
        azure_blob_storage_endpoint="https://teststorage.blob.core.windows.net",
        azure_blob_storage_account_name="account1",
        azure_blob_storage_container_name="airbyte-source-azure-blob-storage-test",
        credentials={"auth_type": "storage_account_key", "azure_blob_storage_account_key": "key1"},
        streams=[],
        start_date="2024-01-01T00:00:00.000000Z",
    )

    assert config.documentation_url() == "https://docs.airbyte.com/integrations/sources/azure-blob-storage"
    assert len(dpath.util.get(config.schema(), "properties/streams/items/properties/format/oneOf/4/properties/processing/oneOf")) == 1
