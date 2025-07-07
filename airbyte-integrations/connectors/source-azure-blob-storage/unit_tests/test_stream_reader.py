# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import datetime
import logging
from typing import Dict, Union
from unittest.mock import patch

import freezegun
import pytest
from azure.storage.blob import BlobProperties, ContainerClient
from source_azure_blob_storage.spec import SourceAzureBlobStorageSpec
from source_azure_blob_storage.stream_reader import AzureOauth2Authenticator, SourceAzureBlobStorageStreamReader


logger = logging.Logger("")


@pytest.mark.parametrize(
    "credentials, expected_credentials_type",
    [
        (
            {
                "auth_type": "oauth2",
                "tenant_id": "tenant_id",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "refresh_token": "refresh_token",
            },
            AzureOauth2Authenticator,
        ),
        ({"auth_type": "storage_account_key", "azure_blob_storage_account_key": "key1"}, str),
    ],
    ids=["oauth2", "storage_account_key"],
)
def test_stream_reader_credentials(credentials: Dict, expected_credentials_type: Union[str, AzureOauth2Authenticator]):
    reader = SourceAzureBlobStorageStreamReader()
    config = SourceAzureBlobStorageSpec(
        azure_blob_storage_endpoint="https://teststorage.blob.core.windows.net",
        azure_blob_storage_account_name="account1",
        azure_blob_storage_container_name="airbyte-source-azure-blob-storage-test",
        credentials=credentials,
        streams=[],
        start_date="2024-01-01T00:00:00.000000Z",
    )
    reader.config = config
    assert isinstance(reader.azure_credentials, expected_credentials_type)


@freezegun.freeze_time("2024-01-02T00:00:00")
def test_stream_reader_files_read_and_filter_by_date():
    reader = SourceAzureBlobStorageStreamReader()
    config = SourceAzureBlobStorageSpec(
        azure_blob_storage_endpoint="https://teststorage.blob.core.windows.net",
        azure_blob_storage_account_name="account1",
        azure_blob_storage_container_name="airbyte-source-azure-blob-storage-test",
        credentials={"auth_type": "storage_account_key", "azure_blob_storage_account_key": "key1"},
        streams=[],
        start_date="2024-01-01T00:00:00.000000Z",
    )
    reader.config = config
    with patch.object(ContainerClient, "list_blobs") as blobs:
        blobs.return_value = [
            BlobProperties(name="sample_file_1.csv", **{"Last-Modified": datetime.datetime(2023, 1, 1, 1, 1, 0)}),
            BlobProperties(name="sample_file_2.csv", **{"Last-Modified": datetime.datetime(2024, 1, 1, 1, 1, 0)}),
            BlobProperties(name="sample_file_3.csv", **{"Last-Modified": datetime.datetime(2024, 1, 5, 1, 1, 0)}),
        ]
        files = list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))
        assert len(files) == 2
