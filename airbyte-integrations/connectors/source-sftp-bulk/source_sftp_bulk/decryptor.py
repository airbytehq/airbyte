# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import os
import tempfile
from abc import ABC, abstractmethod
from typing import Optional

import gnupg

from airbyte_cdk import AirbyteTracedException, FailureType


logger = logging.getLogger("airbyte")


class Decryptor(ABC):
    """
    Abstract base class for file decryptors
    """

    @abstractmethod
    def decrypt_file(self, encrypted_file_path: str, output_file_path: Optional[str] = None) -> str:
        """
        Decrypt a file.

        Args:
            encrypted_file_path: Path to the encrypted file
            output_file_path: Path where the decrypted file should be saved. If None, will use implementation default.

        Returns:
            Path to the decrypted file
        """
        pass

    @abstractmethod
    def can_decrypt(self, file_path: str) -> bool:
        """
        Check if this decryptor can decrypt the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if this decryptor can decrypt the file, False otherwise
        """
        pass


class GPGDecryptor(Decryptor):
    """
    Decryptor implementation for GPG encrypted files
    """

    def __init__(self, gpg_private_key: str, gpg_passphrase: Optional[str] = None):
        """
        Initialize GPG decryptor using python-gnupg.

        Args:
            gpg_private_key: GPG private key content as string
            gpg_passphrase: Passphrase for GPG private key (if required)
        """
        self.gpg_private_key = gpg_private_key
        self.gpg_passphrase = gpg_passphrase

        # Create a temporary directory for gnupg home
        self.gnupghome = tempfile.mkdtemp(prefix="gnupg_")

        # Initialize GPG with our temporary home directory
        self.gpg = gnupg.GPG(gnupghome=self.gnupghome)

        # Import the private key
        import_result = self.gpg.import_keys(gpg_private_key)
        if not import_result.count:
            raise AirbyteTracedException(
                failure_type=FailureType.config_error,
                message="Failed to import GPG private key",
                internal_message=f"GPG key import failed. No keys were imported.",
            )

        # Store the key fingerprints for later use
        self.fingerprints = [key["fingerprint"] for key in import_result.results]

        logger.info(f"Successfully imported {import_result.count} GPG keys")

    def __del__(self):
        """Clean up the temporary GPG home directory when the object is destroyed."""
        try:
            # Clean up the temporary directory
            if hasattr(self, "gnupghome") and os.path.exists(self.gnupghome):
                import shutil

                shutil.rmtree(self.gnupghome)
        except Exception as e:
            logger.warning(f"Failed to clean up GPG temporary directory: {e}")

    def decrypt_file(self, encrypted_file_path: str, output_file_path: Optional[str] = None) -> str:
        """
        Decrypt a GPG encrypted file.

        Args:
            encrypted_file_path: Path to the encrypted file
            output_file_path: Path where the decrypted file should be saved. If None, will use the same path without .gpg extension

        Returns:
            Path to the decrypted file
        """
        if not output_file_path:
            # Remove .gpg, .pgp or .asc extension if present
            for ext in [".gpg", ".pgp", ".asc"]:
                if encrypted_file_path.endswith(ext):
                    output_file_path = encrypted_file_path[: -len(ext)]
                    break
            else:
                # If no recognized extension, append .decrypted
                output_file_path = f"{encrypted_file_path}.decrypted"

        logger.info(f"Decrypting {encrypted_file_path} to {output_file_path}")

        try:
            # Read the encrypted file
            with open(encrypted_file_path, "rb") as f:
                encrypted_data = f.read()

            # Decrypt the data
            decrypted_data = self.gpg.decrypt(encrypted_data, passphrase=self.gpg_passphrase, output=output_file_path)

            if not decrypted_data.ok:
                raise AirbyteTracedException(
                    failure_type=FailureType.config_error,
                    message=f"Failed to decrypt file: {encrypted_file_path}",
                    internal_message=f"GPG decryption failed with status: {decrypted_data.status}, stderr: {decrypted_data.stderr}",
                )

            logger.info(f"Successfully decrypted file to {output_file_path}")
            return output_file_path

        except Exception as e:
            if isinstance(e, AirbyteTracedException):
                raise e
            else:
                raise AirbyteTracedException(
                    failure_type=FailureType.system_error,
                    message="An error occurred during GPG decryption",
                    internal_message=f"Error: {str(e)}",
                )

    def can_decrypt(self, file_path: str) -> bool:
        """
        Check if a file is GPG encrypted based on extension.

        Args:
            file_path: Path to the file

        Returns:
            True if the file appears to be GPG encrypted, False otherwise
        """
        return file_path.endswith((".gpg", ".pgp", ".asc"))


def create_decryptor(decryption_config) -> Optional[Decryptor]:
    """
    Create a decryptor based on the provided configuration

    Args:
        decryption_config: Decryption configuration from the source spec

    Returns:
        An appropriate decryptor instance or None if no decryption is configured
    """
    decryption_type = getattr(decryption_config, "decryption_type", "none")

    if decryption_type == "none":
        return None
    elif decryption_type == "gpg":
        return GPGDecryptor(
            gpg_private_key=decryption_config.private_key,
            gpg_passphrase=decryption_config.passphrase,
        )
    else:
        raise AirbyteTracedException(
            failure_type=FailureType.config_error,
            message=f"Unsupported decryption type: {decryption_type}",
            internal_message=f"No decryptor implementation available for {decryption_type}",
        )
