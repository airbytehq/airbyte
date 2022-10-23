#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

from source_google_cloud_storage.google_cloud_storage_file import GoogleCloudStorageFile


def test_google_cloud_storage_file_open(sample_config):

    file_instance = GoogleCloudStorageFile(file_info=MagicMock(), provider=sample_config["provider"])

    # TODO: Write an appropriate unit test for file_instance.open()
    # As a unit test this shouldn't actually connect to any container/bucket, so be sure to mock relevant methods.


# TODO: if you add or override any methods in google_cloud_storage_file.py, add unit tests for those here
