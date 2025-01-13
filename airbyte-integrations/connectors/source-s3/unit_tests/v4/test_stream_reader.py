#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import io
import logging
from datetime import datetime, timedelta
from itertools import product
from typing import Any, Dict, List, Optional, Set
from unittest.mock import ANY, MagicMock, Mock, patch

import pytest
from botocore.stub import Stubber
from moto import mock_sts
from pydantic.v1 import AnyUrl
from source_s3.v4.config import Config
from source_s3.v4.stream_reader import SourceS3StreamReader

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.exceptions import ErrorListingFiles, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


logger = logging.Logger("")

endpoint_values = ["https://fake.com", None]
_get_matching_files_cases = [
    pytest.param([], [], False, set(), id="no-files-match-if-no-globs"),
    pytest.param(
        ["**"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "a/file2.csv", "LastModified": datetime.now()},
            {"Key": "a/b/file3.csv", "LastModified": datetime.now()},
            {"Key": "a/b/c/file4.csv", "LastModified": datetime.now()},
        ],
        False,
        {"file1.csv", "a/file2.csv", "a/b/file3.csv", "a/b/c/file4.csv"},
        id="all-files-match-single-page",
    ),
    pytest.param(
        ["**"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "a/file2.csv", "LastModified": datetime.now()},
            {"Key": "a/b/file3.csv", "LastModified": datetime.now()},
            {"Key": "a/b/c/file4.csv", "LastModified": datetime.now()},
        ],
        True,
        {"file1.csv", "a/file2.csv", "a/b/file3.csv", "a/b/c/file4.csv"},
        id="all-files-match-multiple-pages",
    ),
    pytest.param(
        ["**/*.csv"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "a/file2.csv", "LastModified": datetime.now()},
            {"Key": "a/b/file3.jsonl", "LastModified": datetime.now()},
            {"Key": "a/b/c/file4.jsonl", "LastModified": datetime.now()},
        ],
        True,
        {"file1.csv", "a/file2.csv"},
        id="nonmatching-files-are-filtered",
    ),
    pytest.param(
        ["a/*.csv", "a/*.jsonl"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "file2.jsonl", "LastModified": datetime.now()},
            {"Key": "a/file3.csv", "LastModified": datetime.now()},
            {"Key": "a/file4.jsonl", "LastModified": datetime.now()},
        ],
        True,
        {"a/file3.csv", "a/file4.jsonl"},
        id="nonmatching-files-are-filtered-multiple-prefixes",
    ),
    pytest.param(
        ["**", "a/*.jsonl"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "file2.jsonl", "LastModified": datetime.now()},
            {"Key": "a/file3.csv", "LastModified": datetime.now()},
            {"Key": "a/file4.jsonl", "LastModified": datetime.now()},
        ],
        True,
        {"file1.csv", "file2.jsonl", "a/file3.csv", "a/file4.jsonl"},
        id="files-matching-multiple-prefixes-only-listed-once",
    ),
    pytest.param(
        ["**"],
        [
            {"Key": "file1.csv", "LastModified": datetime.now()},
            {"Key": "file2.jsonl", "LastModified": datetime.now()},
            {"Key": "file3.csv", "LastModified": datetime.now()},
            {"Key": "file3.csv", "LastModified": datetime.now()},
        ],
        True,
        {"file1.csv", "file2.jsonl", "file3.csv"},
        id="duplicate-files-only-listed-once",
    ),
]

get_matching_files_cases = []
for original_case, endpoint_value in product(_get_matching_files_cases, endpoint_values):
    params = list(original_case.values) + [endpoint_value]
    test_case = pytest.param(*params, id=original_case.id + f"-endpoint-{endpoint_value}")
    get_matching_files_cases.append(test_case)


@pytest.mark.parametrize("globs,mocked_response,multiple_pages,expected_uris,endpoint", get_matching_files_cases)
def test_get_matching_files(
    globs: List[str], mocked_response: List[Dict[str, Any]], multiple_pages: bool, expected_uris: Set[str], endpoint: Optional[str]
):
    reader = SourceS3StreamReader()
    try:
        aws_access_key_id = aws_secret_access_key = None if endpoint else "test"
        reader.config = Config(
            bucket="test",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            streams=[],
            endpoint=endpoint,
        )
    except Exception as exc:
        raise exc

    with patch.object(SourceS3StreamReader, "s3_client", new_callable=MagicMock) as mock_s3_client:
        _setup_mock_s3_client(mock_s3_client, mocked_response, multiple_pages)
        files = list(reader.get_matching_files(globs, None, logger))
        assert set(f.uri for f in files) == expected_uris


def _setup_mock_s3_client(mock_s3_client, mocked_response, multiple_pages):
    responses = []
    if multiple_pages and len(mocked_response) > 1:
        # Split the mocked_response for pagination simulation
        first_half = mocked_response[: len(mocked_response) // 2]
        second_half = mocked_response[len(mocked_response) // 2 :]

        responses.append(
            {
                "IsTruncated": True,
                "Contents": first_half,
                "KeyCount": len(first_half),
                "NextContinuationToken": "token",
            }
        )

        responses.append(
            {
                "IsTruncated": False,
                "Contents": second_half,
                "KeyCount": len(second_half),
            }
        )
    else:
        responses.append(
            {
                "IsTruncated": False,
                "Contents": mocked_response,
                "KeyCount": len(mocked_response),
            }
        )

    def list_objects_v2_side_effect(Bucket, Prefix=None, ContinuationToken=None, **kwargs):
        if ContinuationToken == "token":
            return responses[1]
        return responses[0]

    mock_s3_client.list_objects_v2 = MagicMock(side_effect=list_objects_v2_side_effect)


def _split_mocked_response(mocked_response, multiple_pages):
    if not multiple_pages:
        return mocked_response, []
    split_index = len(mocked_response) // 2
    return mocked_response[:split_index], mocked_response[split_index:]


@patch("boto3.client")
def test_given_multiple_pages_when_get_matching_files_then_pass_continuation_token(boto3_client_mock) -> None:
    boto3_client_mock.return_value.list_objects_v2.side_effect = [
        {
            "Contents": [{"Key": "1", "LastModified": datetime.now()}, {"Key": "2", "LastModified": datetime.now()}],
            "KeyCount": 2,
            "NextContinuationToken": "a key",
        },
        {"Contents": [{"Key": "1", "LastModified": datetime.now()}, {"Key": "2", "LastModified": datetime.now()}], "KeyCount": 2},
    ]
    reader = SourceS3StreamReader()
    reader.config = Config(
        bucket="test",
        aws_access_key_id="aws_access_key_id",
        aws_secret_access_key="aws_secret_access_key",
        streams=[],
        endpoint=None,
    )
    list(reader.get_matching_files(["**"], None, logger))
    assert boto3_client_mock.return_value.list_objects_v2.call_count == 2
    assert "ContinuationToken" in boto3_client_mock.return_value.list_objects_v2.call_args_list[1].kwargs


def test_get_matching_files_exception():
    reader = SourceS3StreamReader()
    reader.config = Config(bucket="test", aws_access_key_id="test", aws_secret_access_key="test", streams=[])
    stub = Stubber(reader.s3_client)
    stub.add_client_error("list_objects_v2")
    stub.activate()
    with pytest.raises(ErrorListingFiles) as exc:
        list(reader.get_matching_files(["*"], None, logger))
    stub.deactivate()
    assert FileBasedSourceError.ERROR_LISTING_FILES.value in exc.value.args[0]


def test_get_matching_files_without_config_raises_exception():
    with pytest.raises(ValueError):
        next(SourceS3StreamReader().get_matching_files([], None, logger))


def test_open_file_without_config_raises_exception():
    with pytest.raises(ValueError):
        with SourceS3StreamReader().open_file(RemoteFile(uri="", last_modified=datetime.now()), FileReadMode.READ, None, logger) as fp:
            fp.read()


@patch("smart_open.open")
def test_open_file_calls_any_open_with_the_right_encoding(smart_open_mock):
    smart_open_mock.return_value = io.BytesIO()
    reader = SourceS3StreamReader()
    reader.config = Config(bucket="test", aws_access_key_id="test", aws_secret_access_key="test", streams=[])
    try:
        reader.config = Config(
            bucket="test",
            aws_access_key_id="test",
            aws_secret_access_key="test",
            streams=[],
            endpoint=None,
        )
    except Exception as exc:
        raise exc

    encoding = "utf8"
    with reader.open_file(RemoteFile(uri="", last_modified=datetime.now()), FileReadMode.READ, encoding, logger) as fp:
        fp.read()

    assert smart_open_mock.call_args.args == ("s3://test/",)
    assert smart_open_mock.call_args.kwargs["mode"] == FileReadMode.READ.value
    assert smart_open_mock.call_args.kwargs["encoding"] == encoding


@patch("source_s3.v4.stream_reader.SourceS3StreamReader.file_size")
@patch("boto3.client")
def test_get_file(mock_boto_client, s3_reader_file_size_mock):
    s3_reader_file_size_mock.return_value = 100

    mock_s3_client_instance = Mock()
    mock_boto_client.return_value = mock_s3_client_instance
    mock_s3_client_instance.download_file.return_value = None

    reader = SourceS3StreamReader()
    reader.config = Config(
        bucket="test",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        streams=[],
        delivery_method={"delivery_type": "use_file_transfer"},
    )
    try:
        reader.config = Config(
            bucket="test",
            aws_access_key_id="test",
            aws_secret_access_key="test",
            streams=[],
            endpoint=None,
            delivery_method={"delivery_type": "use_file_transfer"},
        )
    except Exception as exc:
        raise exc
    test_file_path = "directory/file.txt"
    result = reader.get_file(RemoteFile(uri="", last_modified=datetime.now()), test_file_path, logger)

    assert result == {"bytes": 100, "file_relative_path": ANY, "file_url": ANY}
    assert result["file_url"].endswith(test_file_path)


def test_get_s3_client_without_config_raises_exception():
    with pytest.raises(ValueError):
        SourceS3StreamReader().s3_client


def test_cannot_set_wrong_config_type():
    stream_reader = SourceS3StreamReader()

    class OtherConfig(AbstractFileBasedSpec):
        def documentation_url(cls) -> AnyUrl:
            return AnyUrl("https://fake.com", scheme="https")

    other_config = OtherConfig(streams=[])
    with pytest.raises(AssertionError):
        stream_reader.config = other_config


@mock_sts
@patch("source_s3.v4.stream_reader.boto3.client")
def test_get_iam_s3_client(boto3_client_mock):
    # Mock the STS client assume_role method
    boto3_client_mock.return_value.assume_role.return_value = {
        "Credentials": {
            "AccessKeyId": "assumed_access_key_id",
            "SecretAccessKey": "assumed_secret_access_key",
            "SessionToken": "assumed_session_token",
            "Expiration": datetime.now(),
        }
    }

    # Instantiate your stream reader and set the config
    reader = SourceS3StreamReader()
    reader.config = Config(
        bucket="test",
        role_arn="arn:aws:iam::123456789012:role/my-role",
        streams=[],
        endpoint=None,
    )

    # Call _get_iam_s3_client
    with Stubber(reader.s3_client):
        s3_client = reader._get_iam_s3_client({})

    # Assertions to validate the s3 client
    assert s3_client is not None


@pytest.mark.parametrize(
    "start_date, last_modified_date, expected_result",
    (
        # True when file is new or modified after given start_date
        (datetime.now() - timedelta(days=180), datetime.now(), True),
        (
            datetime.strptime("2024-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2024-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            True,
        ),
        # False when file is older than given start_date
        (datetime.now(), datetime.now() - timedelta(days=180), False),
    ),
)
def test_filter_file_by_start_date(start_date: datetime, last_modified_date: datetime, expected_result: bool) -> None:
    reader = SourceS3StreamReader()

    reader.config = Config(
        bucket="test",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        streams=[],
        start_date=start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    assert expected_result == reader.is_modified_after_start_date(last_modified_date)
