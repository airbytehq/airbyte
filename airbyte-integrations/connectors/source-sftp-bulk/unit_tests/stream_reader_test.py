# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import bz2
import datetime
import gzip
import io
import logging
from unittest.mock import MagicMock, patch

import freezegun
import paramiko
import pytest
from source_sftp_bulk.spec import SourceSFTPBulkSpec
from source_sftp_bulk.stream_reader import SFTPBulkUploadableRemoteFile, SourceSFTPBulkStreamReader

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.file_based.exceptions import FileSizeLimitError
from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode


logger = logging.Logger("")


@freezegun.freeze_time("2024-01-02T00:00:00")
def test_stream_reader_files_read_and_filter_by_date():
    fake_client = MagicMock()
    fake_client.from_transport = MagicMock(return_value=fake_client)
    files_on_server = [
        [
            MagicMock(filename="sample_file_1.csv", st_mode=180, st_mtime=1704067200),
            MagicMock(filename="sample_file_2.csv", st_mode=180, st_mtime=1704060200),
        ]
    ]
    fake_client.listdir_iter = MagicMock(side_effect=files_on_server)
    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            start_date="2024-01-01T00:00:00.000000Z",
        )
        reader.config = config
        files = list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))
        assert len(files) == 1
        assert files[0].uri == "//sample_file_1.csv"
        assert files[0].last_modified == datetime.datetime(2024, 1, 1, 0, 0)


def test_upload_file_size_error():
    reader = SourceSFTPBulkStreamReader()
    config = SourceSFTPBulkSpec(
        host="localhost",
        username="username",
        credentials={"auth_type": "password", "password": "password"},
        port=123,
        streams=[],
        start_date="2024-01-01T00:00:00.000000Z",
    )
    reader.config = config

    class SizeOverWriteSFTPBulkUploadableRemoteFile(SFTPBulkUploadableRemoteFile):
        @property
        def size(self) -> int:
            return SourceSFTPBulkStreamReader.FILE_SIZE_LIMIT + 1

    file = SizeOverWriteSFTPBulkUploadableRemoteFile(
        uri="//sample_file_1.csv",
        last_modified=datetime.datetime(2024, 1, 1, 0, 0),
        config=config,
        sftp_client=MagicMock(),
        logger=logger,
    )
    with pytest.raises(FileSizeLimitError) as err:
        reader.upload(file, "/test", MagicMock())
    assert str(err.value) == "File size exceeds the 1.5 GB limit. File URI: //sample_file_1.csv"


def test_get_matching_files_reraises_airbyte_traced_exception():
    """AirbyteTracedException must propagate and not be swallowed as a warning."""
    fake_client = MagicMock()
    fake_client.from_transport = MagicMock(return_value=fake_client)
    fake_client.listdir_iter = MagicMock(
        side_effect=AirbyteTracedException(
            message="Private key format is not recognized. Supported types: RSA, Ed25519, ECDSA, DSS.",
            internal_message="Failed to parse private key",
            failure_type=FailureType.config_error,
        )
    )
    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            start_date="2024-01-01T00:00:00.000000Z",
        )
        reader.config = config
        with pytest.raises(AirbyteTracedException) as exc_info:
            list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))
        assert "Private key format is not recognized" in exc_info.value.message


def _make_reader_with_remote_bytes(uri: str, payload: bytes) -> tuple[SourceSFTPBulkStreamReader, SFTPBulkUploadableRemoteFile, MagicMock]:
    reader = SourceSFTPBulkStreamReader()
    reader.config = SourceSFTPBulkSpec(
        host="localhost",
        username="username",
        credentials={"auth_type": "password", "password": "password"},
        port=123,
        streams=[],
        start_date="2024-01-01T00:00:00.000000Z",
    )

    fake_sftp_client = MagicMock()
    fake_sftp_client.sftp_connection.open = MagicMock(return_value=io.BytesIO(payload))
    reader._sftp_client = fake_sftp_client

    remote_file = SFTPBulkUploadableRemoteFile(
        uri=uri,
        last_modified=datetime.datetime(2024, 1, 1, 0, 0),
        config=reader.config,
        sftp_client=fake_sftp_client,
        logger=logger,
    )
    return reader, remote_file, fake_sftp_client


def test_open_file_gzip_text_mode_decompresses():
    csv_text = "id,name\n1,alice\n2,bob\n"
    payload = gzip.compress(csv_text.encode("utf-8"))
    reader, remote_file, fake_client = _make_reader_with_remote_bytes("/data/sample.csv.gz", payload)

    result = reader.open_file(remote_file, FileReadMode.READ, "utf-8", logger)

    assert result.read() == csv_text
    fake_client.sftp_connection.open.assert_called_once_with("/data/sample.csv.gz", mode="rb")


def test_open_file_gzip_binary_mode_decompresses():
    payload = gzip.compress(b"\x00\x01\x02binary-content")
    reader, remote_file, _ = _make_reader_with_remote_bytes("/data/blob.bin.gz", payload)

    result = reader.open_file(remote_file, FileReadMode.READ_BINARY, None, logger)

    assert result.read() == b"\x00\x01\x02binary-content"


def test_open_file_bzip2_text_mode_decompresses():
    csv_text = "col\nvalue\n"
    payload = bz2.compress(csv_text.encode("utf-8"))
    reader, remote_file, _ = _make_reader_with_remote_bytes("/data/sample.csv.bz2", payload)

    result = reader.open_file(remote_file, FileReadMode.READ, "utf-8", logger)

    assert result.read() == csv_text


def test_open_file_case_insensitive_extension():
    csv_text = "a,b\n1,2\n"
    payload = gzip.compress(csv_text.encode("utf-8"))
    reader, remote_file, _ = _make_reader_with_remote_bytes("/data/SAMPLE.CSV.GZ", payload)

    result = reader.open_file(remote_file, FileReadMode.READ, "utf-8", logger)

    assert result.read() == csv_text


def test_open_file_uncompressed_passthrough_unchanged():
    """Uncompressed files must be returned exactly as paramiko hands them back, unwrapped."""
    reader, remote_file, fake_client = _make_reader_with_remote_bytes("/data/sample.csv", b"id,name\n1,a\n")
    paramiko_handle = io.BytesIO(b"id,name\n1,a\n")
    fake_client.sftp_connection.open = MagicMock(return_value=paramiko_handle)

    result = reader.open_file(remote_file, FileReadMode.READ, "utf-8", logger)

    assert result is paramiko_handle
    fake_client.sftp_connection.open.assert_called_once_with("/data/sample.csv", mode="r")
