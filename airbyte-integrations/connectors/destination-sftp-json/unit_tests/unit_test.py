#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import io

import paramiko
import pytest
from destination_sftp_json.client import SftpClient, SshKeyError, _load_private_key


@pytest.fixture
def password_credentials() -> dict:
    return {"auth_method": "SSH_PASSWORD_AUTH", "auth_user_password": "sample-password"}


@pytest.fixture
def client(password_credentials) -> SftpClient:
    return SftpClient(
        host="sample-host",
        username="sample-username",
        credentials=password_credentials,
        destination_path="/sample/path",
    )


def test_get_path(client):
    path = client._get_path("mystream")
    assert path == "/sample/path/airbyte_json_mystream.jsonl"


def test_auth_method_constants():
    assert SftpClient.PASSWORD_AUTH == "SSH_PASSWORD_AUTH"
    assert SftpClient.KEY_AUTH == "SSH_KEY_AUTH"


def test_load_private_key_rsa():
    """A freshly generated RSA key, serialized to PEM, should parse back into an RSAKey."""
    generated = paramiko.RSAKey.generate(bits=2048)
    buffer = io.StringIO()
    generated.write_private_key(buffer)

    parsed = _load_private_key(buffer.getvalue())

    assert isinstance(parsed, paramiko.RSAKey)
    assert parsed.get_base64() == generated.get_base64()


def test_load_private_key_invalid():
    with pytest.raises(SshKeyError):
        _load_private_key("not-a-valid-private-key")
