#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import io
import logging
from datetime import datetime
from itertools import product
from typing import Any, Dict, List, Optional, Set
from unittest.mock import patch

import pytest
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.exceptions import ErrorListingFiles, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from botocore.stub import Stubber
from moto import mock_sts
from pydantic import AnyUrl
from source_s3.v4.config import Config
from source_s3.v4.stream_reader import SourceS3StreamReader

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

    stub = set_stub(reader, mocked_response, multiple_pages)
    files = list(reader.get_matching_files(globs, None, logger))
    stub.deactivate()
    assert set(f.uri for f in files) == expected_uris


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

    smart_open_mock.assert_called_once_with(
        "s3://test/", transport_params={"client": reader.s3_client}, mode=FileReadMode.READ.value, encoding=encoding
    )


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


def set_stub(reader: SourceS3StreamReader, contents: List[Dict[str, Any]], multiple_pages: bool) -> Stubber:
    s3_stub = Stubber(reader.s3_client)
    split_contents_idx = int(len(contents) / 2) if multiple_pages else -1
    page1, page2 = contents[:split_contents_idx], contents[split_contents_idx:]
    resp = {
        "KeyCount": len(page1),
        "Contents": page1,
    }
    if page2:
        resp["NextContinuationToken"] = "token"
    s3_stub.add_response("list_objects_v2", resp)
    if page2:
        s3_stub.add_response(
            "list_objects_v2",
            {
                "KeyCount": len(page2),
                "Contents": page2,
            },
        )
    s3_stub.activate()
    return s3_stub


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
