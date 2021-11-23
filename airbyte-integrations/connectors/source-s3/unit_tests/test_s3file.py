#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
from airbyte_cdk import AirbyteLogger
from source_s3.s3file import S3File

LOGGER = AirbyteLogger()


class TestS3File:
    @pytest.mark.parametrize(  # passing in full provider to emulate real usage (dummy values are unused by func)
        "provider, return_true",
        [
            ({"storage": "S3", "bucket": "dummy", "aws_access_key_id": "id", "aws_secret_access_key": "key", "path_prefix": "dummy"}, True),
            ({"storage": "S3", "bucket": "dummy", "aws_access_key_id": None, "aws_secret_access_key": None, "path_prefix": "dummy"}, False),
            ({"storage": "S3", "bucket": "dummy", "path_prefix": "dummy"}, False),
            ({"storage": "S3", "bucket": "dummy", "aws_access_key_id": "id", "aws_secret_access_key": None, "path_prefix": "dummy"}, False),
            (
                {"storage": "S3", "bucket": "dummy", "aws_access_key_id": None, "aws_secret_access_key": "key", "path_prefix": "dummy"},
                False,
            ),
            ({"storage": "S3", "bucket": "dummy", "aws_access_key_id": "id", "path_prefix": "dummy"}, False),
            ({"storage": "S3", "bucket": "dummy", "aws_secret_access_key": "key", "path_prefix": "dummy"}, False),
        ],
    )
    def test_use_aws_account(self, provider, return_true):
        assert S3File.use_aws_account(provider) is return_true
