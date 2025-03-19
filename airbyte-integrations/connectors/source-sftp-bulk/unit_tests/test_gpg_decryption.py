# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import gnupg
from source_sftp_bulk.gpg_decryptor import GPGDecryptor
from source_sftp_bulk.spec import GPGEncryptionConfig, SourceSFTPBulkSpec
from source_sftp_bulk.stream_reader import SourceSFTPBulkStreamReader


class TestGPGDecryption(unittest.TestCase):
    TEST_PRIVATE_KEY = """-----BEGIN PGP PRIVATE KEY BLOCK-----
    
    lQVYBGNkZWYBDAC7atnc6iQPjTwEqBECFa+UdDbEDzaEMCDEVZ1GSFWOvoJELW5L
    DzEgJVIkuHK+Ej5DESvF5c0CNjxOAaI8B9Cfj/xhxQ5KzKFIjiVQhfBbScOAxlTT
    n9JsSMREJaLs0gGZmXdYvAwLTiY0tTC5Rai5SLwURXKXQUODMGw9FgGPXeUqudsc
    SIzYszc6q7HCdY+KRRfK/+/2Mcv8iUXYkV8lQmNGIEpU9GdtWmjJE9qqEGKT3VgL
    XlQXQyAh3LnBvlS9xg==
    -----END PGP PRIVATE KEY BLOCK-----"""

    TEST_PASSPHRASE = "test-passphrase"

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        # Create a mock config with GPG decryption enabled
        self.config = SourceSFTPBulkSpec(
            host="sftp.example.com",
            username="user",
            credentials={"auth_type": "password", "password": "pass"},
            port=22,
            folder_path="/",
            # Add an empty streams list to satisfy the requirement
            streams=[],
            gpg_config=GPGEncryptionConfig(enabled=True, private_key=self.TEST_PRIVATE_KEY, passphrase=self.TEST_PASSPHRASE),
        )

    def tearDown(self):
        # Clean up temp directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    @patch("gnupg.GPG")
    def test_gpg_decryptor_initialization(self, mock_gpg_class):
        # Setup the mock
        mock_gpg = MagicMock()
        mock_gpg_class.return_value = mock_gpg

        # Mock import_keys result
        mock_import_result = MagicMock()
        mock_import_result.count = 1
        mock_import_result.results = [{"fingerprint": "ABCD1234"}]
        mock_gpg.import_keys.return_value = mock_import_result

        # Initialize decryptor
        decryptor = GPGDecryptor(gpg_private_key=self.TEST_PRIVATE_KEY, gpg_passphrase=self.TEST_PASSPHRASE)

        # Verify GPG was initialized with a temp directory
        self.assertTrue(mock_gpg_class.called)
        self.assertTrue("gnupghome" in mock_gpg_class.call_args[1])
        self.assertTrue(mock_gpg.import_keys.called)
        mock_gpg.import_keys.assert_called_once_with(self.TEST_PRIVATE_KEY)

        # Verify fingerprints were captured
        self.assertEqual(decryptor.fingerprints, ["ABCD1234"])

    @patch("gnupg.GPG")
    def test_gpg_decryption(self, mock_gpg_class):
        # Setup the mock
        mock_gpg = MagicMock()
        mock_gpg_class.return_value = mock_gpg

        # Mock import_keys result
        mock_import_result = MagicMock()
        mock_import_result.count = 1
        mock_import_result.results = [{"fingerprint": "ABCD1234"}]
        mock_gpg.import_keys.return_value = mock_import_result

        # Mock decrypt result
        mock_decrypt_result = MagicMock()
        mock_decrypt_result.ok = True
        mock_decrypt_result.status = "decryption ok"
        mock_gpg.decrypt.return_value = mock_decrypt_result

        # Create a test encrypted file
        encrypted_file_path = os.path.join(self.temp_dir, "test.csv.gpg")
        with open(encrypted_file_path, "w") as f:
            f.write("This is mock encrypted content")

        # Expected output path
        expected_output_path = os.path.join(self.temp_dir, "test.csv")

        # Initialize decryptor and test decryption
        decryptor = GPGDecryptor(gpg_private_key=self.TEST_PRIVATE_KEY, gpg_passphrase=self.TEST_PASSPHRASE)
        output_path = decryptor.decrypt_file(encrypted_file_path)

        # Assertions
        self.assertEqual(output_path, expected_output_path)
        self.assertTrue(mock_gpg.decrypt.called)

        # Verify decrypt was called with correct parameters
        decrypt_args = mock_gpg.decrypt.call_args
        self.assertEqual(decrypt_args[1]["passphrase"], self.TEST_PASSPHRASE)
        self.assertEqual(decrypt_args[1]["output"], expected_output_path)

    @patch("gnupg.GPG")
    def test_gpg_decryption_failure(self, mock_gpg_class):
        # Setup the mock
        mock_gpg = MagicMock()
        mock_gpg_class.return_value = mock_gpg

        # Mock import_keys result
        mock_import_result = MagicMock()
        mock_import_result.count = 1
        mock_import_result.results = [{"fingerprint": "ABCD1234"}]
        mock_gpg.import_keys.return_value = mock_import_result

        # Mock decrypt result - failure
        mock_decrypt_result = MagicMock()
        mock_decrypt_result.ok = False
        mock_decrypt_result.status = "decryption failed"
        mock_decrypt_result.stderr = "Bad passphrase"
        mock_gpg.decrypt.return_value = mock_decrypt_result

        # Create a test encrypted file
        encrypted_file_path = os.path.join(self.temp_dir, "test.csv.gpg")
        with open(encrypted_file_path, "w") as f:
            f.write("This is mock encrypted content")

        # Initialize decryptor
        decryptor = GPGDecryptor(gpg_private_key=self.TEST_PRIVATE_KEY, gpg_passphrase=self.TEST_PASSPHRASE)

        # Test that decryption failure raises AirbyteTracedException
        from airbyte_cdk import AirbyteTracedException

        with self.assertRaises(AirbyteTracedException) as context:
            decryptor.decrypt_file(encrypted_file_path)

        self.assertIn("GPG decryption failed", str(context.exception))

    def test_is_gpg_encrypted(self):
        # Initialize decryptor with mocks
        with patch("gnupg.GPG") as mock_gpg_class:
            # Mock import_keys result
            mock_gpg = MagicMock()
            mock_gpg_class.return_value = mock_gpg
            mock_import_result = MagicMock()
            mock_import_result.count = 1
            mock_import_result.results = [{"fingerprint": "ABCD1234"}]
            mock_gpg.import_keys.return_value = mock_import_result

            decryptor = GPGDecryptor(gpg_private_key=self.TEST_PRIVATE_KEY, gpg_passphrase=self.TEST_PASSPHRASE)

            # Test various file extensions
            self.assertTrue(decryptor.is_gpg_encrypted("file.gpg"))
            self.assertTrue(decryptor.is_gpg_encrypted("file.pgp"))
            self.assertTrue(decryptor.is_gpg_encrypted("file.asc"))
            self.assertFalse(decryptor.is_gpg_encrypted("file.csv"))
            self.assertFalse(decryptor.is_gpg_encrypted("file.txt"))

    @patch("gnupg.GPG")
    @patch("source_sftp_bulk.stream_reader.SourceSFTPBulkStreamReader._get_file_transfer_paths")
    @patch("source_sftp_bulk.stream_reader.os.path.getsize")
    def test_stream_reader_decrypt_integration(self, mock_getsize, mock_get_paths, mock_gpg_class):
        # Setup mock GPG
        mock_gpg = MagicMock()
        mock_gpg_class.return_value = mock_gpg

        # Mock import_keys result
        mock_import_result = MagicMock()
        mock_import_result.count = 1
        mock_import_result.results = [{"fingerprint": "ABCD1234"}]
        mock_gpg.import_keys.return_value = mock_import_result

        # Mock decrypt result
        mock_decrypt_result = MagicMock()
        mock_decrypt_result.ok = True
        mock_decrypt_result.status = "decryption ok"
        mock_gpg.decrypt.return_value = mock_decrypt_result

        # Setup mock stream reader
        stream_reader = SourceSFTPBulkStreamReader()
        stream_reader.config = self.config

        # Mock SFTP client
        stream_reader._sftp_client = MagicMock()
        stream_reader.sftp_client.sftp_connection = MagicMock()
        stream_reader.sftp_client.sftp_connection.get = MagicMock()

        # Setup mock file paths
        encrypted_path = os.path.join(self.temp_dir, "test.csv.gpg")
        decrypted_path = os.path.join(self.temp_dir, "test.csv")
        relative_path = "test.csv.gpg"
        decrypted_relative_path = "test.csv"

        # Create the encrypted file
        with open(encrypted_path, "w") as f:
            f.write("Mock encrypted content")

        # Mock file_size method
        stream_reader.file_size = MagicMock(return_value=100)

        # Mock _get_file_transfer_paths
        mock_get_paths.return_value = (relative_path, encrypted_path, os.path.abspath(encrypted_path))

        # Mock getsize
        mock_getsize.return_value = 50

        # Create RemoteFile mock
        remote_file = MagicMock()
        remote_file.uri = "/remote/path/test.csv.gpg"

        # Call get_file
        result = stream_reader.get_file(remote_file, self.temp_dir, MagicMock())

        # Verify decryption was attempted
        self.assertTrue(mock_gpg.decrypt.called)

        # Verify result contains decrypted file info
        self.assertIn("file_url", result)
        self.assertIn("bytes", result)
        self.assertIn("file_relative_path", result)
        self.assertEqual(result["bytes"], 50)
