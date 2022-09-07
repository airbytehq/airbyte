#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Mapping
from unittest.mock import MagicMock

import pytest
import smart_open
from source_s3_new.s3_new_file import S3NewFile


def test_s3_new_file_open(sample_config):
    smart_open.open = MagicMock()
    file_instance = S3NewFile(file_info=MagicMock(), provider=sample_config["provider"])
    with file_instance.open("rb") as s3_file:
        assert s3_file


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
def test_use_aws_account(provider: Mapping[str, str], return_true: bool) -> None:
    assert S3NewFile.use_aws_account(provider) is return_true
