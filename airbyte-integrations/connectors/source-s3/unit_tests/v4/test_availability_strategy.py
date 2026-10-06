#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest
from source_s3.v4.availability_strategy import SourceS3AvailabilityStrategy
from source_s3.v4.config import S3FileBasedStreamConfig

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources.file_based.exceptions import CheckAvailabilityError, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_types.parquet_parser import ParquetParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


logger = logging.getLogger("test")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_stream(skip_full_check_for_parquet: bool = False, parser=None, files=None):
    """Build a mock stream with the minimal surface used by the strategy."""
    stream = MagicMock()
    stream.name = "test_stream"
    stream.config = MagicMock(spec=S3FileBasedStreamConfig)
    stream.config.skip_full_check_for_parquet = skip_full_check_for_parquet

    if parser is None:
        parser = MagicMock(spec=ParquetParser)
        parser.file_read_mode = "rb"
        parser.check_config.return_value = (True, None)
    stream.get_parser.return_value = parser

    if files is not None:
        stream.get_files.return_value = iter(files)

    return stream


def _make_remote_file(uri: str = "s3://bucket/data.parquet") -> RemoteFile:
    return MagicMock(spec=RemoteFile, uri=uri)


def _make_strategy():
    stream_reader = MagicMock()
    return SourceS3AvailabilityStrategy(stream_reader)


# ---------------------------------------------------------------------------
# check_availability_and_parsability – delegation tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "skip_full_check_for_parquet,parser_cls",
    [
        pytest.param(False, ParquetParser, id="flag-off-parquet-parser"),
        pytest.param(True, None, id="flag-on-non-parquet-parser"),
        pytest.param(False, None, id="flag-off-non-parquet-parser"),
    ],
)
def test_delegates_to_super_when_skip_not_applicable(skip_full_check_for_parquet, parser_cls):
    """When skip_full_check_for_parquet is False or parser is not ParquetParser, super() is called."""
    if parser_cls is ParquetParser:
        parser = MagicMock(spec=ParquetParser)
        parser.check_config.return_value = (True, None)
    else:
        parser = MagicMock()  # not a ParquetParser instance
        parser.check_config.return_value = (True, None)

    stream = _make_stream(skip_full_check_for_parquet=skip_full_check_for_parquet, parser=parser)
    strategy = _make_strategy()

    with patch.object(
        SourceS3AvailabilityStrategy.__bases__[0],
        "check_availability_and_parsability",
        return_value=(True, None),
    ) as super_mock:
        result = strategy.check_availability_and_parsability(stream, logger, None)

    assert super_mock.called
    assert result == (True, None)


# ---------------------------------------------------------------------------
# Parquet skip-check path tests (flag=True)
# ---------------------------------------------------------------------------


def test_parquet_skips_full_parse_and_opens_file():
    """When skip_full_check_for_parquet is True and parser is ParquetParser, the strategy skips _check_parse_record and only opens the file."""
    parser = MagicMock(spec=ParquetParser)
    parser.file_read_mode = "rb"
    parser.check_config.return_value = (True, None)

    file = _make_remote_file()
    stream = _make_stream(skip_full_check_for_parquet=True, parser=parser, files=[file])
    handle_mock = MagicMock()
    stream.stream_reader.open_file.return_value = handle_mock

    strategy = _make_strategy()

    with patch.object(strategy, "_check_list_files", return_value=file) as list_mock:
        result = strategy.check_availability_and_parsability(stream, logger, None)

    list_mock.assert_called_once_with(stream)
    stream.stream_reader.open_file.assert_called_once_with(file, "rb", None, logger)
    handle_mock.close.assert_called_once()
    assert result == (True, None)


def test_parquet_returns_false_when_config_check_fails():
    """When parser.check_config returns False for a parquet stream with skip enabled, availability returns False."""
    parser = MagicMock(spec=ParquetParser)
    parser.check_config.return_value = (False, "bad config")

    stream = _make_stream(skip_full_check_for_parquet=True, parser=parser)
    strategy = _make_strategy()

    result = strategy.check_availability_and_parsability(stream, logger, None)

    assert result == (False, "bad config")


def test_parquet_returns_false_on_check_availability_error():
    """When _check_list_files raises CheckAvailabilityError, availability returns False."""
    parser = MagicMock(spec=ParquetParser)
    parser.check_config.return_value = (True, None)

    stream = _make_stream(skip_full_check_for_parquet=True, parser=parser)
    strategy = _make_strategy()

    with patch.object(
        strategy, "_check_list_files", side_effect=CheckAvailabilityError(FileBasedSourceError.EMPTY_STREAM, stream="test_stream")
    ):
        available, msg = strategy.check_availability_and_parsability(stream, logger, None)

    assert available is False
    assert msg is not None


def test_parquet_reraises_airbyte_traced_exception():
    """AirbyteTracedException propagates out of the parquet skip path."""
    parser = MagicMock(spec=ParquetParser)
    parser.check_config.return_value = (True, None)

    stream = _make_stream(skip_full_check_for_parquet=True, parser=parser)
    strategy = _make_strategy()

    exc = AirbyteTracedException(message="traced")
    with patch.object(strategy, "_check_list_files", side_effect=exc):
        with pytest.raises(AirbyteTracedException):
            strategy.check_availability_and_parsability(stream, logger, None)


def test_parquet_wraps_unexpected_exception_in_check_availability_error():
    """Unexpected exceptions from open_file are wrapped in CheckAvailabilityError."""
    parser = MagicMock(spec=ParquetParser)
    parser.file_read_mode = "rb"
    parser.check_config.return_value = (True, None)

    file = _make_remote_file()
    stream = _make_stream(skip_full_check_for_parquet=True, parser=parser)
    stream.stream_reader.open_file.side_effect = RuntimeError("unexpected failure")

    strategy = _make_strategy()

    with patch.object(strategy, "_check_list_files", return_value=file):
        with pytest.raises(CheckAvailabilityError) as exc_info:
            strategy.check_availability_and_parsability(stream, logger, None)

    assert isinstance(exc_info.value.__cause__, RuntimeError)


# ---------------------------------------------------------------------------
# S3FileBasedStreamConfig – skip_full_check_for_parquet field
# ---------------------------------------------------------------------------


def test_s3_stream_config_skip_full_check_for_parquet_defaults_false():
    """The skip_full_check_for_parquet field defaults to False."""
    cfg = S3FileBasedStreamConfig(name="test", format={"filetype": "parquet"}, globs=["**/*.parquet"], validation_policy="Emit Record")
    assert cfg.skip_full_check_for_parquet is False


def test_s3_stream_config_skip_full_check_for_parquet_set_true():
    """The skip_full_check_for_parquet field can be set to True."""
    cfg = S3FileBasedStreamConfig(
        name="test",
        format={"filetype": "parquet"},
        globs=["**/*.parquet"],
        validation_policy="Emit Record",
        skip_full_check_for_parquet=True,
    )
    assert cfg.skip_full_check_for_parquet is True
