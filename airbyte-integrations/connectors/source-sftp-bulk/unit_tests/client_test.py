# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import struct
from unittest.mock import MagicMock, patch

import paramiko
import pytest
from paramiko.ssh_exception import SSHException
from source_sftp_bulk.client import SFTPClient, _parse_private_key

from airbyte_cdk import AirbyteTracedException


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


@pytest.mark.parametrize(
    "failing_classes,succeeding_class",
    [
        pytest.param([], paramiko.RSAKey, id="rsa_key"),
        pytest.param([paramiko.RSAKey], paramiko.Ed25519Key, id="ed25519_key"),
        pytest.param([paramiko.RSAKey, paramiko.Ed25519Key], paramiko.ECDSAKey, id="ecdsa_key"),
        pytest.param([paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey], paramiko.DSSKey, id="dss_key"),
    ],
)
def test_parse_private_key_auto_detects_key_type(failing_classes, succeeding_class):
    """_parse_private_key tries key classes in order and returns the first that succeeds."""
    mock_key = MagicMock(spec=succeeding_class)
    patches = [patch.object(cls, "from_private_key", side_effect=paramiko.SSHException("wrong type")) for cls in failing_classes]
    patches.append(patch.object(succeeding_class, "from_private_key", return_value=mock_key))
    with patches[0] if len(patches) == 1 else patches[0]:
        for p in patches[1:]:
            p.start()
        try:
            result = _parse_private_key("fake-key-content")
            assert result is mock_key
        finally:
            for p in patches[1:]:
                p.stop()


def test_parse_private_key_unrecognized_format_raises_config_error():
    """All key classes fail => AirbyteTracedException with config_error."""
    with (
        patch.object(paramiko.RSAKey, "from_private_key", side_effect=paramiko.SSHException("fail")),
        patch.object(paramiko.Ed25519Key, "from_private_key", side_effect=paramiko.SSHException("fail")),
        patch.object(paramiko.ECDSAKey, "from_private_key", side_effect=paramiko.SSHException("fail")),
        patch.object(paramiko.DSSKey, "from_private_key", side_effect=paramiko.SSHException("fail")),
    ):
        with pytest.raises(AirbyteTracedException) as exc_info:
            _parse_private_key("invalid-key-content")
        assert "Private key format is not recognized" in exc_info.value.message


def test_parse_private_key_catches_value_error():
    """ValueError from a key class is caught and the next class is tried."""
    mock_key = MagicMock(spec=paramiko.Ed25519Key)
    with (
        patch.object(paramiko.RSAKey, "from_private_key", side_effect=ValueError("bad data")),
        patch.object(paramiko.Ed25519Key, "from_private_key", return_value=mock_key),
    ):
        result = _parse_private_key("fake-key-content")
        assert result is mock_key


def test_client_with_private_key_calls_parse():
    """SFTPClient passes private_key through _parse_private_key."""
    mock_key = MagicMock(spec=paramiko.RSAKey)
    with (
        patch("source_sftp_bulk.client._parse_private_key", return_value=mock_key) as mock_parse,
        patch.object(paramiko, "Transport", MagicMock()),
        patch.object(paramiko, "SFTPClient", MagicMock()),
    ):
        client = SFTPClient(
            host="localhost",
            username="username",
            private_key="fake-key",
            port=123,
        )
        mock_parse.assert_called_once_with("fake-key")
        assert client.key is mock_key


def test_client_without_private_key_skips_parse():
    """SFTPClient with no private_key does not call _parse_private_key."""
    with (
        patch("source_sftp_bulk.client._parse_private_key") as mock_parse,
        patch.object(paramiko, "Transport", MagicMock()),
        patch.object(paramiko, "SFTPClient", MagicMock()),
    ):
        client = SFTPClient(
            host="localhost",
            username="username",
            password="password",
            port=123,
        )
        mock_parse.assert_not_called()
        assert client.key is None


def test_parse_private_key_catches_struct_error():
    """struct.error from a key class is caught and the next class is tried."""
    mock_key = MagicMock(spec=paramiko.Ed25519Key)
    with (
        patch.object(paramiko.RSAKey, "from_private_key", side_effect=struct.error("unpack requires a buffer of 4 bytes")),
        patch.object(paramiko.Ed25519Key, "from_private_key", return_value=mock_key),
    ):
        result = _parse_private_key("fake-key-content")
        assert result is mock_key


def test_parse_private_key_all_struct_errors_raises_config_error():
    """All key classes raise struct.error => AirbyteTracedException with config_error."""
    with (
        patch.object(paramiko.RSAKey, "from_private_key", side_effect=struct.error("unpack requires a buffer of 4 bytes")),
        patch.object(paramiko.Ed25519Key, "from_private_key", side_effect=struct.error("bad data")),
        patch.object(paramiko.ECDSAKey, "from_private_key", side_effect=struct.error("bad data")),
        patch.object(paramiko.DSSKey, "from_private_key", side_effect=struct.error("bad data")),
    ):
        with pytest.raises(AirbyteTracedException) as exc_info:
            _parse_private_key("invalid-key-content")
        assert "Private key format is not recognized" in exc_info.value.message
