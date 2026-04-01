# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from io import StringIO
from unittest.mock import MagicMock, patch

import paramiko
import pytest
from cryptography.hazmat.primitives.asymmetric.ec import SECP256R1
from cryptography.hazmat.primitives.asymmetric.ec import generate_private_key as ec_generate
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
from paramiko.ssh_exception import SSHException
from source_sftp_bulk.client import SFTPClient


def test_client_exception():
    with pytest.raises(SSHException):
        SFTPClient(
            host="localhost",
            username="username",
            password="password",
            port=123,
        )


def test_client_connection():
    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", MagicMock()):
        SFTPClient(
            host="localhost",
            username="username",
            password="password",
            port=123,
        )
        assert SFTPClient


def _paramiko_key_to_str(key: paramiko.PKey) -> str:
    buf = StringIO()
    key.write_private_key(buf)
    return buf.getvalue()


def _cryptography_key_to_str(key) -> str:
    return key.private_bytes(Encoding.PEM, PrivateFormat.OpenSSH, NoEncryption()).decode()


def test_client_rsa_key_parsed():
    rsa_key = paramiko.RSAKey.generate(2048)
    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", MagicMock()):
        client = SFTPClient(host="localhost", username="username", private_key=_paramiko_key_to_str(rsa_key), port=22)
        assert isinstance(client.key, paramiko.RSAKey)


def test_client_ed25519_key_parsed():
    ed25519_key = Ed25519PrivateKey.generate()
    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", MagicMock()):
        client = SFTPClient(host="localhost", username="username", private_key=_cryptography_key_to_str(ed25519_key), port=22)
        assert isinstance(client.key, paramiko.Ed25519Key)


def test_client_ecdsa_key_parsed():
    ecdsa_key = ec_generate(SECP256R1())
    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", MagicMock()):
        client = SFTPClient(host="localhost", username="username", private_key=_cryptography_key_to_str(ecdsa_key), port=22)
        assert isinstance(client.key, paramiko.ECDSAKey)
