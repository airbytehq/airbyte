# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import datetime
import logging
from unittest.mock import MagicMock, patch

import freezegun
import paramiko
import pytest
from source_sftp_bulk.spec import SourceSFTPBulkSpec
from source_sftp_bulk.stream_reader import SFTPBulkUploadableRemoteFile, SourceSFTPBulkStreamReader

from airbyte_cdk.sources.file_based.exceptions import FileSizeLimitError
from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


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


def test_open_file_with_windows_1252_encoding():
    """Test that files with Windows-1252 encoding are properly decoded."""

    # Windows-1252 specific characters:
    # 0xb2 = \u00b2 (superscript 2), 0xd0 = \u00d0 (Latin capital Eth)
    superscript_two = "\u00b2"
    latin_eth = "\u00d0"

    # Create sample data with Windows-1252 specific characters
    windows_1252_bytes = b"Product_ID,Price\xb2,Supplier\xd0Name\n1,29.99,TechCorp\n2,15.50,Global\xd0Supply\n"
    expected_text = f"Product_ID,Price{superscript_two},Supplier{latin_eth}Name\n1,29.99,TechCorp\n2,15.50,Global{latin_eth}Supply\n"

    # Create a mock file object that behaves like SFTP file
    mock_sftp_file = MagicMock()
    mock_sftp_file.read.return_value = windows_1252_bytes
    mock_sftp_file.prefetch = MagicMock()
    mock_sftp_file.closed = False  # Ensure file appears open  # Add prefetch method

    # Mock SFTP connection
    mock_sftp_connection = MagicMock()
    mock_sftp_connection.open.return_value = mock_sftp_file

    # Mock SFTP client
    fake_client = MagicMock()
    fake_client.sftp_connection = mock_sftp_connection

    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", MagicMock(return_value=fake_client)):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
        )
        reader.config = config
        reader._sftp_client = fake_client

        # Create a mock RemoteFile
        remote_file = RemoteFile(uri="/test.csv", last_modified=datetime.datetime.now())

        # Open file with Windows-1252 encoding
        file_handle = reader.open_file(file=remote_file, mode=FileReadMode.READ, encoding="windows-1252", logger=logger)

        # Read the content
        content = file_handle.read()

        # Verify the content was decoded correctly
        assert content == expected_text
        assert f"Price{superscript_two}" in content  # Check superscript 2 decoded properly
        assert f"Supplier{latin_eth}Name" in content  # Check Eth character decoded properly

        # Verify the SFTP file was opened in binary mode
        mock_sftp_connection.open.assert_called_once_with("/test.csv", mode="rb")
