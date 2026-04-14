#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import io
import logging
from contextlib import contextmanager
from typing import List
from unittest.mock import MagicMock, patch

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from source_s3.v4.availability_strategy import SourceS3AvailabilityStrategy
from source_s3.v4.config import S3FileBasedStreamConfig

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources.file_based.exceptions import CheckAvailabilityError, CustomFileBasedException, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_types.parquet_parser import ParquetParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


logger = logging.getLogger("test")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_stream(light_parquet_check: bool = False, parser=None, files=None):
    """Build a mock stream with the minimal surface used by the strategy."""
    stream = MagicMock()
    stream.name = "test_stream"
    stream.config = MagicMock(spec=S3FileBasedStreamConfig)
    stream.config.light_parquet_check = light_parquet_check

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


def _write_parquet_to_buffer(column_names: List[str], rows: int) -> "pa.Buffer":
    """Write a minimal Parquet file into an in-memory buffer."""
    arrays = [pa.array(list(range(rows))) for _ in column_names]
    table = pa.table(dict(zip(column_names, arrays)))
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink)
    return sink.getvalue()


@contextmanager
def _parquet_fp(column_names: List[str], rows: int):
    """Context-manager that yields a file-like backed by a Parquet buffer."""
    buf = _write_parquet_to_buffer(column_names, rows)
    fp = io.BytesIO(buf.to_pybytes())
    yield fp


def _make_strategy():
    stream_reader = MagicMock()
    return SourceS3AvailabilityStrategy(stream_reader)


# ---------------------------------------------------------------------------
# check_availability_and_parsability – delegation tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "light_parquet_check,parser_cls,expected_delegates",
    [
        pytest.param(False, ParquetParser, True, id="flag-off-parquet-parser"),
        pytest.param(True, None, True, id="flag-on-non-parquet-parser"),
        pytest.param(False, None, True, id="flag-off-non-parquet-parser"),
    ],
)
def test_delegates_to_super_when_light_check_not_applicable(light_parquet_check, parser_cls, expected_delegates):
    """When light_parquet_check is False or parser is not ParquetParser, super() is called."""
    if parser_cls is ParquetParser:
        parser = MagicMock(spec=ParquetParser)
        parser.check_config.return_value = (True, None)
    else:
        parser = MagicMock()  # not a ParquetParser instance
        parser.check_config.return_value = (True, None)

    stream = _make_stream(light_parquet_check=light_parquet_check, parser=parser)
    strategy = _make_strategy()

    with patch.object(
        SourceS3AvailabilityStrategy.__bases__[0],
        "check_availability_and_parsability",
        return_value=(True, None),
    ) as super_mock:
        result = strategy.check_availability_and_parsability(stream, logger, None)

    assert super_mock.called == expected_delegates
    assert result == (True, None)


def test_uses_light_path_when_enabled_and_parquet():
    """When light_parquet_check is True and parser is ParquetParser, the light path is used."""
    parser = MagicMock(spec=ParquetParser)
    parser.file_read_mode = "rb"
    parser.check_config.return_value = (True, None)

    file = _make_remote_file()
    stream = _make_stream(light_parquet_check=True, parser=parser, files=[file])

    strategy = _make_strategy()

    with (
        patch.object(strategy, "_check_list_files", return_value=file) as list_mock,
        patch.object(strategy, "_check_parse_record_light") as parse_mock,
    ):
        result = strategy.check_availability_and_parsability(stream, logger, None)

    list_mock.assert_called_once_with(stream)
    parse_mock.assert_called_once_with(stream, file, logger)
    assert result == (True, None)


def test_light_path_returns_false_when_config_check_fails():
    """When parser.check_config returns False, availability returns False."""
    parser = MagicMock(spec=ParquetParser)
    parser.check_config.return_value = (False, "bad config")

    stream = _make_stream(light_parquet_check=True, parser=parser)
    strategy = _make_strategy()

    result = strategy.check_availability_and_parsability(stream, logger, None)

    assert result == (False, "bad config")


def test_light_path_returns_false_on_check_availability_error():
    """When _check_list_files raises CheckAvailabilityError, availability returns False."""
    parser = MagicMock(spec=ParquetParser)
    parser.check_config.return_value = (True, None)

    stream = _make_stream(light_parquet_check=True, parser=parser)
    strategy = _make_strategy()

    with patch.object(
        strategy, "_check_list_files", side_effect=CheckAvailabilityError(FileBasedSourceError.EMPTY_STREAM, stream="test_stream")
    ):
        available, msg = strategy.check_availability_and_parsability(stream, logger, None)

    assert available is False
    assert msg is not None


def test_light_path_reraises_airbyte_traced_exception():
    """AirbyteTracedException propagates out of the light path."""
    parser = MagicMock(spec=ParquetParser)
    parser.check_config.return_value = (True, None)

    stream = _make_stream(light_parquet_check=True, parser=parser)
    strategy = _make_strategy()

    exc = AirbyteTracedException(message="traced")
    with patch.object(strategy, "_check_list_files", side_effect=exc):
        with pytest.raises(AirbyteTracedException):
            strategy.check_availability_and_parsability(stream, logger, None)


# ---------------------------------------------------------------------------
# _check_parse_record_light – Parquet-level tests
# ---------------------------------------------------------------------------


def test_light_parse_succeeds_with_valid_parquet():
    """A well-formed Parquet file with at least one column and one row succeeds."""
    parser = MagicMock(spec=ParquetParser)
    parser.file_read_mode = "rb"

    file = _make_remote_file()
    stream = _make_stream(light_parquet_check=True, parser=parser)

    strategy = _make_strategy()

    # Wire up the open_file context manager to return an in-memory Parquet buffer.
    @contextmanager
    def _open(*_args, **_kwargs):
        with _parquet_fp(["col_a", "col_b"], rows=5) as fp:
            yield fp

    stream.stream_reader.open_file = _open

    # Should not raise
    strategy._check_parse_record_light(stream, file, logger)


def test_light_parse_succeeds_on_empty_data():
    """A Parquet file with columns but zero rows is treated as available (empty-file case)."""
    parser = MagicMock(spec=ParquetParser)
    parser.file_read_mode = "rb"

    file = _make_remote_file()
    stream = _make_stream(light_parquet_check=True, parser=parser)

    strategy = _make_strategy()

    @contextmanager
    def _open(*_args, **_kwargs):
        with _parquet_fp(["col_a"], rows=0) as fp:
            yield fp

    stream.stream_reader.open_file = _open

    # Should not raise – empty file is acceptable
    strategy._check_parse_record_light(stream, file, logger)


def test_light_parse_raises_on_empty_schema():
    """A Parquet file with no columns raises CheckAvailabilityError."""
    parser = MagicMock(spec=ParquetParser)
    parser.file_read_mode = "rb"

    file = _make_remote_file()
    stream = _make_stream(light_parquet_check=True, parser=parser)

    strategy = _make_strategy()

    # Build a Parquet file with an empty schema
    @contextmanager
    def _open(*_args, **_kwargs):
        schema = pa.schema([])
        table = pa.table({}, schema=schema)
        sink = pa.BufferOutputStream()
        pq.write_table(table, sink)
        fp = io.BytesIO(sink.getvalue().to_pybytes())
        yield fp

    stream.stream_reader.open_file = _open

    with pytest.raises(CheckAvailabilityError):
        strategy._check_parse_record_light(stream, file, logger)


def test_light_parse_raises_on_custom_file_based_exception():
    """CustomFileBasedException is wrapped in CheckAvailabilityError."""
    parser = MagicMock(spec=ParquetParser)
    parser.file_read_mode = "rb"

    file = _make_remote_file()
    stream = _make_stream(light_parquet_check=True, parser=parser)

    strategy = _make_strategy()

    @contextmanager
    def _open(*_args, **_kwargs):
        raise CustomFileBasedException("boom")

    stream.stream_reader.open_file = _open

    with pytest.raises(CheckAvailabilityError):
        strategy._check_parse_record_light(stream, file, logger)


def test_light_parse_reraises_airbyte_traced_exception():
    """AirbyteTracedException inside _check_parse_record_light propagates unchanged."""
    parser = MagicMock(spec=ParquetParser)
    parser.file_read_mode = "rb"

    file = _make_remote_file()
    stream = _make_stream(light_parquet_check=True, parser=parser)

    strategy = _make_strategy()

    exc = AirbyteTracedException(message="traced-inner")

    @contextmanager
    def _open(*_args, **_kwargs):
        raise exc

    stream.stream_reader.open_file = _open

    with pytest.raises(AirbyteTracedException):
        strategy._check_parse_record_light(stream, file, logger)


# ---------------------------------------------------------------------------
# S3FileBasedStreamConfig – light_parquet_check field
# ---------------------------------------------------------------------------


def test_s3_stream_config_light_parquet_check_defaults_false():
    """The light_parquet_check field defaults to False."""
    cfg = S3FileBasedStreamConfig(name="test", format={"filetype": "parquet"}, globs=["**/*.parquet"], validation_policy="Emit Record")
    assert cfg.light_parquet_check is False


def test_s3_stream_config_light_parquet_check_set_true():
    """The light_parquet_check field can be set to True."""
    cfg = S3FileBasedStreamConfig(
        name="test",
        format={"filetype": "parquet"},
        globs=["**/*.parquet"],
        validation_policy="Emit Record",
        light_parquet_check=True,
    )
    assert cfg.light_parquet_check is True
