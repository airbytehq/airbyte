#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError, ConnectTimeoutError, EndpointConnectionError
from source_s3.v4.availability_strategy import SourceS3AvailabilityStrategy
from source_s3.v4.config import Config
from source_s3.v4.source import SourceS3
from source_s3.v4.stream_reader import SourceS3StreamReader

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.file_based.exceptions import CheckAvailabilityError, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


@pytest.mark.parametrize(
    "error,hint",
    [
        (ClientError({"Error": {"Code": "InvalidAccessKeyId"}}, "ListObjectsV2"), "access key ID"),
        (ClientError({"Error": {"Code": "SignatureDoesNotMatch"}}, "ListObjectsV2"), "secret access key"),
        (ClientError({"Error": {"Code": "AccessDenied"}}, "GetObject"), "s3:ListBucket and s3:GetObject"),
        (ClientError({"Error": {"Code": "NoSuchBucket"}}, "ListObjectsV2"), "bucket name and AWS region"),
        (EndpointConnectionError(endpoint_url="https://private.example"), "network allowlist"),
        (ConnectTimeoutError(endpoint_url="https://private.example"), "network allowlist"),
    ],
)
@pytest.mark.parametrize("phase", ["list", "parse", "open"])
def test_aws_check_errors(error, hint, phase):
    reader = MagicMock()
    strategy = SourceS3AvailabilityStrategy(reader)
    stream = MagicMock()
    stream.get_files.return_value = [MagicMock()]
    stream.get_parser.return_value.check_config.return_value = (True, None)
    if phase == "list":
        stream.get_files.side_effect = error
        check = strategy.check_availability
    elif phase == "parse":
        stream.get_parser.return_value.parse_records.side_effect = error
        check = strategy.check_availability_and_parsability
    else:
        stream.get_parser.return_value.parser_max_n_files_for_parsability = 0
        stream.stream_reader.open_file.side_effect = error
        check = strategy.check_availability_and_parsability
    with pytest.raises(AirbyteTracedException) as raised:
        check(stream, logging.getLogger(), None)
    assert raised.value.failure_type == FailureType.config_error
    assert hint in raised.value.message
    assert "private.example" not in raised.value.message


def test_parse_error_is_not_reported_as_connection_error():
    stream = MagicMock()
    stream.get_files.return_value = [MagicMock()]
    stream.get_parser.return_value.check_config.return_value = (True, None)
    stream.get_parser.return_value.parse_records.side_effect = ValueError("sensitive file contents")
    strategy = SourceS3AvailabilityStrategy(MagicMock())
    with pytest.raises(AirbyteTracedException) as raised:
        strategy.check_availability_and_parsability(stream, logging.getLogger(), None)
    assert raised.value.failure_type == FailureType.config_error
    assert "configured format" in raised.value.message
    assert "sensitive" not in raised.value.message


def test_empty_stream_already_fails_check():
    stream = MagicMock()
    stream.name = "empty"
    stream.get_files.return_value = iter([])
    available, reason = SourceS3AvailabilityStrategy(MagicMock()).check_availability(stream, logging.getLogger(), None)
    assert not available
    assert reason


@pytest.mark.parametrize("bucket", ["bucket", " s3://bucket/ ", "https://bucket.s3.amazonaws.com"])
def test_normalize_bucket(bucket):
    config = Config(bucket=bucket, credentials={"auth_type": "default_credentials"}, streams=[])
    assert config.bucket == "bucket"


@pytest.mark.parametrize(
    "bucket",
    [
        "",
        None,
        "s3://bucket/path",
        "https://bucket.s3.amazonaws.com/path",
        "https://example.com",
        "s3://user:secret@bucket",
        "bucket/path",
        "s3://bucket?token=secret",
        "s3://bucket:bad",
    ],
)
def test_invalid_bucket_fails_before_connection(bucket):
    source = SourceS3.__new__(SourceS3)
    with patch("airbyte_cdk.sources.file_based.file_based_source.FileBasedSource.check_connection") as check:
        with pytest.raises(AirbyteTracedException) as raised:
            source.check_connection(logging.getLogger(), {"bucket": bucket})
    check.assert_not_called()
    assert raised.value.failure_type == FailureType.config_error
    assert "Move any path" in raised.value.message
    assert "secret" not in raised.value.message


def test_normalized_bucket_is_used_by_live_check():
    source = SourceS3.__new__(SourceS3)
    with patch("airbyte_cdk.sources.file_based.file_based_source.FileBasedSource.check_connection", return_value=(True, None)) as check:
        assert source.check_connection(logging.getLogger(), {"bucket": "s3://bucket"}) == (True, None)
    assert check.call_args.args[1]["bucket"] == "bucket"


def test_wrapped_reader_error_reaches_check():
    reader = SourceS3StreamReader()
    reader.config = Config(bucket="bucket", credentials={"auth_type": "default_credentials"}, streams=[])
    reader._s3_client = MagicMock()
    reader._s3_client.list_objects_v2.side_effect = ClientError({"Error": {"Code": "AccessDenied"}}, "ListObjectsV2")
    stream = MagicMock()
    stream.get_files.side_effect = lambda: reader.get_matching_files(["**"], None, logging.getLogger())
    with pytest.raises(AirbyteTracedException) as raised:
        SourceS3AvailabilityStrategy(reader).check_availability(stream, logging.getLogger(), None)
    assert "s3:ListBucket" in raised.value.message


def test_open_file_preserves_os_error():
    reader = SourceS3StreamReader()
    reader.config = Config(bucket="bucket", credentials={"auth_type": "default_credentials"}, streams=[])
    reader._s3_client = MagicMock()
    file = RemoteFile(uri="file.csv", last_modified=datetime.now(timezone.utc))
    error = OSError("Cannot open object")
    with patch("smart_open.open", side_effect=error):
        with pytest.raises(OSError) as raised:
            reader.open_file(file, FileReadMode.READ, None, logging.getLogger())
    assert raised.value is error


def test_unknown_aws_error_is_not_misclassified():
    error = ClientError({"Error": {"Code": "SlowDown"}}, "ListObjectsV2")
    assert SourceS3AvailabilityStrategy._raise_aws_error(error) is None
