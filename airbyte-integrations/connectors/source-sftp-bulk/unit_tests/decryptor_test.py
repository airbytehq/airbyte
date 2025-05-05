# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import unittest
from unittest.mock import MagicMock, patch

from airbyte_cdk import AirbyteTracedException
from source_sftp_bulk.decryptor import Decryptor, GPGDecryptor, create_decryptor
from source_sftp_bulk.spec import GPGDecryption, NoDecryption


class TestDecryptor(unittest.TestCase):
    TEST_PRIVATE_KEY = """-----BEGIN PGP PRIVATE KEY BLOCK-----
    mock-key-content
    -----END PGP PRIVATE KEY BLOCK-----"""

    TEST_PASSPHRASE = "test-passphrase"

    def test_create_decryptor_none(self):
        """Test that no decryptor is created when decryption is disabled"""
        config = NoDecryption(decryption_type="none")
        decryptor = create_decryptor(config)
        self.assertIsNone(decryptor)

    @patch("source_sftp_bulk.decryptor.GPGDecryptor")
    def test_create_decryptor_gpg(self, mock_gpg_decryptor):
        """Test that a GPG decryptor is created when GPG decryption is enabled"""
        # Create a mock GPGDecryptor instance
        mock_instance = MagicMock(spec=Decryptor)
        mock_gpg_decryptor.return_value = mock_instance

        # Create a GPG decryption config
        config = GPGDecryption(
            decryption_type="gpg",
            private_key=self.TEST_PRIVATE_KEY,
            passphrase=self.TEST_PASSPHRASE,
        )

        # Create the decryptor
        decryptor = create_decryptor(config)

        # Verify the GPGDecryptor was created with the correct parameters
        mock_gpg_decryptor.assert_called_once_with(gpg_private_key=self.TEST_PRIVATE_KEY, gpg_passphrase=self.TEST_PASSPHRASE)

        # Verify the correct instance was returned
        self.assertEqual(decryptor, mock_instance)

    def test_create_decryptor_unknown(self):
        """Test that an exception is raised for unknown decryption types"""
        # Create a mock config with an unknown decryption type
        config = MagicMock()
        config.decryption_type = "unknown"

        # Verify that an exception is raised
        with self.assertRaises(AirbyteTracedException) as context:
            create_decryptor(config)

        # Update assertion to match the actual error message
        self.assertIn("No decryptor implementation available for unknown", str(context.exception))
