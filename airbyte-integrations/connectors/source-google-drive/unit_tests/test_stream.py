#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
from typing import Callable, Dict, Optional
from unittest.mock import MagicMock

import pytest  # type: ignore[import-not-found]

from airbyte_cdk.sources.file_based.config.avro_format import AvroFormat
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.excel_format import ExcelFormat
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from airbyte_cdk.sources.file_based.config.parquet_format import ParquetFormat
from airbyte_cdk.sources.file_based.config.unstructured_format import UnstructuredFormat

from source_google_drive.stream import GoogleDriveFileBasedStream
from source_google_drive.stream_reader import GoogleDriveRemoteFile


def _make_remote_file(
    uri: str,
    mime_type: str,
    original_mime_type: Optional[str] = None,
) -> GoogleDriveRemoteFile:
    now = datetime.datetime.utcnow()
    return GoogleDriveRemoteFile(
        uri=uri,
        id=f"id-{uri}",
        mime_type=mime_type,
        original_mime_type=original_mime_type or mime_type,
        last_modified=now,
        created_at=now,
        view_link=f"https://example.com/{uri}",
    )


@pytest.mark.parametrize(
    "format_factory, matching_kwargs, mismatched_kwargs",
    [
        pytest.param(
            CsvFormat,
            {"uri": "valid.csv", "mime_type": "text/csv"},
            {"uri": "invalid.pdf", "mime_type": "application/pdf"},
            id="csv",
        ),
        pytest.param(
            JsonlFormat,
            {"uri": "valid.jsonl", "mime_type": "application/json"},
            {"uri": "invalid.csv", "mime_type": "text/csv"},
            id="jsonl",
        ),
        pytest.param(
            ParquetFormat,
            {"uri": "valid.parquet", "mime_type": "application/x-parquet"},
            {"uri": "invalid.csv", "mime_type": "text/csv"},
            id="parquet",
        ),
        pytest.param(
            AvroFormat,
            {"uri": "valid.avro", "mime_type": "application/avro"},
            {"uri": "invalid.csv", "mime_type": "text/csv"},
            id="avro",
        ),
        pytest.param(
            ExcelFormat,
            {
                "uri": "valid.xlsx",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
            {"uri": "invalid.csv", "mime_type": "text/csv"},
            id="excel",
        ),
        pytest.param(
            UnstructuredFormat,
            {
                "uri": "Meeting Notes",
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "original_mime_type": "application/vnd.google-apps.document",
            },
            {"uri": "invalid.csv", "mime_type": "text/csv"},
            id="unstructured",
        ),
    ],
)
def test_google_drive_stream_filters_mismatched_files(
    format_factory: Callable[[], object],
    matching_kwargs: Dict[str, str],
    mismatched_kwargs: Dict[str, str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    format_config = format_factory()
    matching_file = _make_remote_file(**matching_kwargs)
    mismatched_file = _make_remote_file(**mismatched_kwargs)

    stream_reader = MagicMock()
    stream_reader.get_matching_files.return_value = [matching_file, mismatched_file]

    stream = GoogleDriveFileBasedStream(
        config=FileBasedStreamConfig(name="drive_stream", format=format_config, globs=["**"]),
        catalog_schema=None,
        stream_reader=stream_reader,
        availability_strategy=MagicMock(),
        discovery_policy=MagicMock(),
        parsers={type(format_config): MagicMock()},
        validation_policy=MagicMock(),
        errors_collector=MagicMock(),
        cursor=MagicMock(),
    )

    with caplog.at_level(logging.INFO):
        files = list(stream.get_files())

    assert [f.uri for f in files] == [matching_file.uri]
    assert mismatched_file.uri in caplog.text
    assert "Skipping file" in caplog.text
    assert "Modify the stream's glob pattern" in caplog.text
    assert format_config.filetype in caplog.text


def test_google_drive_stream_accepts_google_docs_when_configured(caplog: pytest.LogCaptureFixture) -> None:
    format_config = UnstructuredFormat()
    google_doc = _make_remote_file(
        uri="Project Plan",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        original_mime_type="application/vnd.google-apps.document",
    )
    stream_reader = MagicMock()
    stream_reader.get_matching_files.return_value = [google_doc]

    stream = GoogleDriveFileBasedStream(
        config=FileBasedStreamConfig(name="unstructured_stream", format=format_config, globs=["**"]),
        catalog_schema=None,
        stream_reader=stream_reader,
        availability_strategy=MagicMock(),
        discovery_policy=MagicMock(),
        parsers={type(format_config): MagicMock()},
        validation_policy=MagicMock(),
        errors_collector=MagicMock(),
        cursor=MagicMock(),
    )

    with caplog.at_level(logging.INFO):
        files = list(stream.get_files())

    assert [f.uri for f in files] == [google_doc.uri]
    assert caplog.text == ""
