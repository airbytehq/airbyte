#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from source_google_cloud_storage.stream import GoogleCloudStorageStream


def test_file_iterator(sample_config):

    stream = GoogleCloudStorageStream(dataset="foo", provider=sample_config["provider"], format={}, path_pattern="**")

    # TODO: Write an appropriate unit test for stream.file_iterator()
    # As a unit test this shouldn't actually connect to any container/bucket, so be sure to mock relevant methods.


# TODO: if you add or override any methods in stream.py, add unit tests for those here
