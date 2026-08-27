# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import datetime
import logging
from unittest.mock import MagicMock, patch

import freezegun
import paramiko
import pytest
from source_sftp_bulk.spec import SourceSFTPBulkSpec
from source_sftp_bulk.stream_reader import SFTPBulkUploadableRemoteFile, SourceSFTPBulkStreamReader

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.file_based.exceptions import FileSizeLimitError


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


def test_upload_rejected_when_not_enough_disk_space():
    """
    There is no fixed byte ceiling anymore: a 2 GB file (bigger than the old hardcoded 1.5GB
    FILE_SIZE_LIMIT) is rejected only because the mocked disk doesn't have room for it.
    """
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

    class SizeOverwriteSFTPBulkUploadableRemoteFile(SFTPBulkUploadableRemoteFile):
        @property
        def size(self) -> int:
            return 2_000_000_000  # 2 GB

    file = SizeOverwriteSFTPBulkUploadableRemoteFile(
        uri="//sample_file_1.csv",
        last_modified=datetime.datetime(2024, 1, 1, 0, 0),
        config=config,
        sftp_client=MagicMock(),
        logger=logger,
    )

    file_size = 2_000_000_000  # 2 GB
    available_free_bytes = 1_000_000_000  # only 1 GB free: not enough with the 1.2x safety margin

    with patch("source_sftp_bulk.stream_reader.psutil.disk_usage") as mock_disk_usage:
        mock_disk_usage.return_value = MagicMock(free=available_free_bytes)
        with pytest.raises(FileSizeLimitError) as err:
            reader.upload(file, "/test", MagicMock())
    assert "Not enough disk space" in str(err.value)
    # Message reports GB (1024^3 bytes), not the file's round GB-decimal size - derive the
    # expected substrings from the same math the implementation uses, rather than hardcoding
    # rounded literals that are easy to get wrong (e.g. 2_000_000_000 bytes is 1.86 GiB, not 2.00).
    assert f"{file_size / (1024 ** 3):.2f} GB" in str(err.value)
    assert f"{available_free_bytes / (1024 ** 3):.2f} GB" in str(err.value)


def test_upload_succeeds_above_old_1_5gb_limit_when_disk_space_available(tmp_path):
    """
    A file bigger than the old hardcoded 1.5GB FILE_SIZE_LIMIT now succeeds because there's
    plenty of (mocked) disk space; the size check is disk-space-based, not a fixed byte count.

    Unlike the rejection test above, this one runs far enough into upload() to reach
    _get_file_transfer_paths(), which calls os.makedirs() on the staging directory - use
    pytest's tmp_path fixture rather than a literal path so the test doesn't depend on "/test"
    being writable in whatever environment it runs in.
    """
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

    class SizeOverwriteSFTPBulkUploadableRemoteFile(SFTPBulkUploadableRemoteFile):
        @property
        def size(self) -> int:
            return 2_000_000_000  # 2 GB

        def download_to_local_directory(self, local_file_path: str) -> None:
            pass  # no-op: this test only cares whether the size check rejects the file

    file = SizeOverwriteSFTPBulkUploadableRemoteFile(
        uri="//sample_file_1.csv",
        last_modified=datetime.datetime(2024, 1, 1, 0, 0),
        config=config,
        sftp_client=MagicMock(),
        logger=logger,
    )

    with patch("source_sftp_bulk.stream_reader.psutil.disk_usage") as mock_disk_usage:
        mock_disk_usage.return_value = MagicMock(free=100_000_000_000)  # 100 GB free
        file_record_data, file_reference = reader.upload(file, str(tmp_path), MagicMock())
    assert file_record_data.bytes == 2_000_000_000
    assert file_reference.file_size_bytes == 2_000_000_000


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
