# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import datetime
import logging
import os
from unittest.mock import MagicMock, patch

import freezegun
import paramiko
from source_sftp_bulk.decryptor import Decryptor
from source_sftp_bulk.spec import GPGDecryption, NoDecryption, SourceSFTPBulkSpec
from source_sftp_bulk.stream_reader import SourceSFTPBulkStreamReader

from airbyte_cdk import AirbyteTracedException


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
    fake_client.listdir_attr = MagicMock(side_effect=files_on_server)
    with (
        patch.object(paramiko, "Transport", MagicMock()),
        patch.object(paramiko, "SFTPClient", fake_client),
    ):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            start_date="2024-01-01T00:00:00.000000Z",
            decryption=NoDecryption(decryption_type="none"),
        )
        reader.config = config
        files = list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))
        assert len(files) == 1
        assert files[0].uri == "//sample_file_1.csv"
        assert files[0].last_modified == datetime.datetime(2024, 1, 1, 0, 0)


class TestStreamReaderDecryption:
    @patch("source_sftp_bulk.stream_reader.create_decryptor")
    def test_config_setter_creates_decryptor(self, mock_create_decryptor):
        """Test that setting config creates a decryptor if decryption is enabled"""
        # Setup
        mock_decryptor = MagicMock(spec=Decryptor)
        mock_create_decryptor.return_value = mock_decryptor

        # Create a config with GPG decryption
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            decryption=GPGDecryption(
                decryption_type="gpg",
                private_key="mock-key",
                passphrase="mock-passphrase",
            ),
        )

        # Set the config on the stream reader
        reader = SourceSFTPBulkStreamReader()
        reader.config = config

        # Verify the decryptor factory was called
        mock_create_decryptor.assert_called_once_with(config.decryption)

        # Verify the decryptor was set on the stream reader
        assert reader._decryptor == mock_decryptor

    @patch("source_sftp_bulk.stream_reader.SourceSFTPBulkStreamReader._get_file_transfer_paths")
    @patch("source_sftp_bulk.stream_reader.os.path.getsize")
    def test_get_file_with_decryption(self, mock_getsize, mock_get_paths):
        """Test get_file method with decryption enabled"""
        # Setup
        reader = SourceSFTPBulkStreamReader()
        reader._sftp_client = MagicMock()
        reader.sftp_client.sftp_connection = MagicMock()
        reader.sftp_client.sftp_connection.get = MagicMock()

        # Create a mock decryptor
        mock_decryptor = MagicMock(spec=Decryptor)
        mock_decryptor.can_decrypt.return_value = True
        mock_decryptor.decrypt_file.return_value = "/path/to/decrypted/file.csv"
        reader._decryptor = mock_decryptor

        # Mock file size method
        reader.file_size = MagicMock(return_value=100)

        # Mock _get_file_transfer_paths
        mock_get_paths.return_value = (
            "relative/path/file.gpg",
            "/path/to/local/file.gpg",
            "/absolute/path/to/local/file.gpg",
        )

        # Mock getsize
        mock_getsize.return_value = 80

        # Create a remote file
        remote_file = MagicMock()
        remote_file.uri = "/remote/path/file.gpg"

        # Call get_file
        result = reader.get_file(remote_file, "/local/dir", logger)

        # Verify the decryptor was used
        mock_decryptor.can_decrypt.assert_called_once_with("/path/to/local/file.gpg")
        mock_decryptor.decrypt_file.assert_called_once_with("/path/to/local/file.gpg")

        # Verify the result contains the decrypted file info
        assert result["file_url"] == "/path/to/decrypted/file.csv"
        assert result["bytes"] == 80
        assert "file_relative_path" in result

    @patch("source_sftp_bulk.stream_reader.SourceSFTPBulkStreamReader._get_file_transfer_paths")
    def test_get_file_without_decryption(self, mock_get_paths):
        """Test get_file method without decryption"""
        # Setup
        reader = SourceSFTPBulkStreamReader()
        reader._sftp_client = MagicMock()
        reader.sftp_client.sftp_connection = MagicMock()
        reader.sftp_client.sftp_connection.get = MagicMock()

        # No decryptor
        reader._decryptor = None

        # Mock file size method
        reader.file_size = MagicMock(return_value=100)

        # Mock _get_file_transfer_paths
        mock_get_paths.return_value = (
            "relative/path/file.csv",
            "/path/to/local/file.csv",
            "/absolute/path/to/local/file.csv",
        )

        # Create a remote file
        remote_file = MagicMock()
        remote_file.uri = "/remote/path/file.csv"

        # Call get_file
        result = reader.get_file(remote_file, "/local/dir", logger)

        # Verify the result contains the original file info
        assert result["file_url"] == "/absolute/path/to/local/file.csv"
        assert result["bytes"] == 100
        assert result["file_relative_path"] == "relative/path/file.csv"

    @patch("source_sftp_bulk.stream_reader.SourceSFTPBulkStreamReader._get_file_transfer_paths")
    def test_get_file_with_decryptor_not_encrypted(self, mock_get_paths):
        """Test get_file method with decryptor but file is not encrypted"""
        # Setup
        reader = SourceSFTPBulkStreamReader()
        reader._sftp_client = MagicMock()
        reader.sftp_client.sftp_connection = MagicMock()
        reader.sftp_client.sftp_connection.get = MagicMock()

        # Create a mock decryptor that reports file is not encrypted
        mock_decryptor = MagicMock(spec=Decryptor)
        mock_decryptor.can_decrypt.return_value = False
        reader._decryptor = mock_decryptor

        # Mock file size method
        reader.file_size = MagicMock(return_value=100)

        # Mock _get_file_transfer_paths
        mock_get_paths.return_value = (
            "relative/path/file.csv",
            "/path/to/local/file.csv",
            "/absolute/path/to/local/file.csv",
        )

        # Create a remote file
        remote_file = MagicMock()
        remote_file.uri = "/remote/path/file.csv"

        # Call get_file
        result = reader.get_file(remote_file, "/local/dir", logger)

        # Verify the decryptor was consulted but not used
        mock_decryptor.can_decrypt.assert_called_once_with("/path/to/local/file.csv")
        assert not mock_decryptor.decrypt_file.called

        # Verify the result contains the original file info
        assert result["file_url"] == "/absolute/path/to/local/file.csv"
        assert result["bytes"] == 100
        assert result["file_relative_path"] == "relative/path/file.csv"
