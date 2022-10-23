#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import logging
from pathlib import Path
from typing import Iterator, List, Mapping

import pytest
from airbyte_cdk.sources.streams.files.test_framework import AbstractFilesStreamIntegrationTest
from airbyte_cdk.sources.streams.files.test_framework.sample_files import SAMPLE_DIR
from google.cloud import exceptions, storage
from source_google_cloud_storage.source import SourceGoogleCloudStorage
from source_google_cloud_storage.stream import GoogleCloudStorageStream

# This is a custom integration test specifically for files sources.
# It is additional to any unit tests and the general source acceptance tests.
# It would be a good idea to implement this to ensure robustness of the connector, however it is not an absolute requirement.
# If this isn't being implemented straight away, mass comment out the rest of the file so it can be implemented in the future.


HERE = Path(__file__).resolve().parent
LOGGER = logging.getLogger("airbyte")


class TestGoogleCloudStorageStream(AbstractFilesStreamIntegrationTest):
    @property
    def stream_class(self) -> type:
        return GoogleCloudStorageStream

    @property
    def credentials(self) -> Mapping:
        filename = HERE.parent / "secrets/config.json"
        with open(filename) as json_file:
            config = json.load(json_file)

        return {"service_account_json": config["provider"]["service_account_json"]}

    def provider(self, bucket_name: str) -> Mapping:
        return {"bucket": bucket_name}

    def cloud_files(self, cloud_bucket_name: str, credentials: Mapping, files_to_upload: List, private: bool = True) -> Iterator[str]:
        """
        :param cloud_bucket_name: name of bucket/container/etc.
        :param credentials: mapping of provider specific credentials
        :param files_to_upload: list of paths to local files to upload
        :param private: whether or not to make the files private and require credentials to read, defaults to True
        :yield: url filepath to uploaded file
        """
        print("\n")
        service_account_json = json.loads(credentials.get("service_account_json"), strict=False)
        client = storage.Client.from_service_account_info(service_account_json)
        try:
            new_bucket = client.get_bucket(cloud_bucket_name)
        except exceptions.NotFound:
            LOGGER.info(f"Creating bucket {cloud_bucket_name}")
            client.create_bucket(cloud_bucket_name, project="dataline-integration-testing")
            new_bucket = client.get_bucket(cloud_bucket_name)

        if not private:
            policy = new_bucket.get_iam_policy(requested_policy_version=3)
            policy.bindings.append({"role": "roles/storage.objectViewer", "members": ["allUsers"]})
            new_bucket.set_iam_policy(policy)

        LOGGER.info(f"Uploading {len(files_to_upload)} file(s) to {'private' if private else 'public'} GCS bucket '{cloud_bucket_name}'")
        for filepath in files_to_upload:
            upload_path = str(filepath).replace(str(SAMPLE_DIR), "")
            upload_path = upload_path[1:] if upload_path[0] == "/" else upload_path
            blob = new_bucket.blob(upload_path)
            blob.upload_from_filename(filepath)
            yield f"{new_bucket.name}/{upload_path}"

    def teardown_infra(self, cloud_bucket_name: str, credentials: Mapping) -> None:
        """
        GCS-specific logic to tidy up any cloud resources.

        :param cloud_bucket_name: name of bucket/container/etc.
        :param credentials: mapping of provider specific credentials
        """
        service_account_json = json.loads(credentials.get("service_account_json"), strict=False)
        client = storage.Client.from_service_account_info(service_account_json)

        client.get_bucket(cloud_bucket_name).delete(force=True)
        LOGGER.info(f"GCS Bucket {cloud_bucket_name} is now deleted")
