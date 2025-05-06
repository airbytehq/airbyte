# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from source_sftp_bulk.decryptor import GPGDecryptor

from airbyte_cdk import AirbyteTracedException


class TestGPGDecryptor(unittest.TestCase):
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

    def tearDown(self):
        # Clean up temp directory
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    @patch("gnupg.GPG")
    def test_gpg_decryptor_initialization(self, mock_gpg_class):
        """Test GPGDecryptor initialization with mocked GPG"""
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
        """Test decryption with mocked GPG"""
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
        """Test handling of decryption failures"""
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
        with self.assertRaises(AirbyteTracedException) as context:
            decryptor.decrypt_file(encrypted_file_path)

        self.assertIn("GPG decryption failed", str(context.exception))

    @patch("gnupg.GPG")
    def test_can_decrypt(self, mock_gpg_class):
        """Test the can_decrypt method"""
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

        # Test various file extensions
        self.assertTrue(decryptor.can_decrypt("file.gpg"))
        self.assertTrue(decryptor.can_decrypt("file.pgp"))
        self.assertTrue(decryptor.can_decrypt("file.asc"))
        self.assertFalse(decryptor.can_decrypt("file.csv"))
        self.assertFalse(decryptor.can_decrypt("file.txt"))

    @patch("gnupg.GPG")
    def test_gpg_key_import_failure(self, mock_gpg_class):
        """Test handling of key import failures"""
        # Setup the mock
        mock_gpg = MagicMock()
        mock_gpg_class.return_value = mock_gpg

        # Mock import_keys result - failure
        mock_import_result = MagicMock()
        mock_import_result.count = 0  # No keys imported
        mock_import_result.results = []
        mock_gpg.import_keys.return_value = mock_import_result

        # Initialize decryptor - should raise exception
        with self.assertRaises(AirbyteTracedException) as context:
            GPGDecryptor(gpg_private_key="Invalid key", gpg_passphrase=self.TEST_PASSPHRASE)

        # Update assertion to match the actual error message
        self.assertIn("GPG key import failed", str(context.exception))
