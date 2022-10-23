#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.sources.streams.files import FileInfo
from source_s3_new.stream import S3NewStream


@pytest.mark.parametrize(
    ("bucket", "path_prefix", "list_v2_objects", "expected_file_info"),
    (
        (  # two files in the first response, one in the second
            "test_bucket",
            "/widescreen",
            [
                {
                    "Contents": [
                        {"Key": "Key_A", "Size": 2048, "LastModified": datetime(2020, 2, 20, 20, 0, 2)},
                        {"Key": "Key_B", "Size": 1024, "LastModified": datetime(2020, 2, 20, 20, 22, 2)},
                    ],
                    "NextContinuationToken": "token",
                },
                {"Contents": [{"Key": "Key_C", "Size": 512, "LastModified": datetime(2022, 2, 2, 2, 2, 2)}]},
            ],
            [
                FileInfo(key="Key_A", size=2048, last_modified=datetime(2020, 2, 20, 20, 0, 2)),
                FileInfo(key="Key_B", size=1024, last_modified=datetime(2020, 2, 20, 20, 22, 2)),
                FileInfo(key="Key_C", size=512, last_modified=datetime(2022, 2, 2, 2, 2, 2)),
            ],
        ),
        ("another_test_bucket", "/fullscreen", [{}], []),  # empty response
        (  # some keys are not accepted
            "almost_real_test_bucket",
            "/HD",
            [
                {
                    "Contents": [
                        {"Key": "file/path", "Size": 2048, "LastModified": datetime(2020, 2, 20, 20, 0, 2)},
                        {"Key": "file/path/A/", "Size": 1024, "LastModified": datetime(2020, 2, 20, 20, 22, 2)},
                    ],
                    "NextContinuationToken": "token",
                },
                {"Contents": [{"Key": "file/path/B/", "Size": 512, "LastModified": datetime(2022, 2, 2, 2, 2, 2)}]},
            ],
            [
                FileInfo(key="file/path", size=2048, last_modified=datetime(2020, 2, 20, 20, 0, 2)),
            ],
        ),
    ),
)
def test_file_iterator(bucket, path_prefix, list_v2_objects, expected_file_info):
    provider = {"aws_access_key_id": "key_id", "aws_secret_access_key": "access_key"}
    s3_client_mock = MagicMock(return_value=MagicMock(list_objects_v2=MagicMock(side_effect=list_v2_objects)))
    with patch("source_s3_new.stream.make_s3_client", s3_client_mock):
        stream_instance = S3NewStream(
            dataset="dummy",
            provider={"bucket": bucket, "path_prefix": path_prefix, **provider},
            format={},
            path_pattern="**/prefix*.png",
        )
        expected_info = iter(expected_file_info)

        for file_info in stream_instance.file_iterator():
            assert file_info == next(expected_info)
