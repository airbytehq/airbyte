#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import io

import paramiko
import pytest
from destination_sftp_json.client import HostKeyError, SftpClient, SshKeyError, _load_host_key, _load_private_key


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


@pytest.fixture
def host_key() -> paramiko.RSAKey:
    """A host key paramiko can serialize to a known_hosts-style public entry."""
    return paramiko.RSAKey.generate(bits=2048)


def test_host_key_constants():
    assert SftpClient.HOST_KEY_AUTO_ADD == "auto_add"
    assert SftpClient.HOST_KEY_STRICT == "strict"


def test_default_host_key_checking_is_auto_add(client):
    assert client.host_key_checking == {"mode": "auto_add"}


def test_auto_add_policy_used_by_default(client):
    ssh = paramiko.SSHClient()
    client._apply_host_key_policy(ssh)
    assert isinstance(ssh._policy, paramiko.AutoAddPolicy)


def test_strict_policy_pins_host_key_and_rejects_unknown(password_credentials, host_key):
    client = SftpClient(
        host="sample-host",
        username="sample-username",
        credentials=password_credentials,
        destination_path="/sample/path",
        host_key_checking={
            "mode": "strict",
            "host_key_type": host_key.get_name(),
            "host_key": host_key.get_base64(),
        },
    )
    ssh = paramiko.SSHClient()
    client._apply_host_key_policy(ssh)

    # Unknown keys must be rejected (no silent trust-on-first-use).
    assert isinstance(ssh._policy, paramiko.RejectPolicy)
    # The configured key is pinned for the host and matches what the server would present.
    pinned = ssh.get_host_keys().lookup("sample-host")
    assert pinned is not None
    assert pinned[host_key.get_name()].get_base64() == host_key.get_base64()


def test_strict_policy_pins_host_key_with_custom_port(password_credentials, host_key):
    client = SftpClient(
        host="sample-host",
        port=2222,
        username="sample-username",
        credentials=password_credentials,
        destination_path="/sample/path",
        host_key_checking={
            "mode": "strict",
            "host_key_type": host_key.get_name(),
            "host_key": host_key.get_base64(),
        },
    )
    ssh = paramiko.SSHClient()
    client._apply_host_key_policy(ssh)

    # Non-default ports are stored under the "[host]:port" token by paramiko.
    assert ssh.get_host_keys().lookup("[sample-host]:2222") is not None
    assert ssh.get_host_keys().lookup("sample-host") is None


def test_strict_policy_requires_key_fields(password_credentials):
    client = SftpClient(
        host="sample-host",
        username="sample-username",
        credentials=password_credentials,
        destination_path="/sample/path",
        host_key_checking={"mode": "strict"},
    )
    with pytest.raises(HostKeyError):
        client._apply_host_key_policy(paramiko.SSHClient())


def test_unknown_host_key_mode_raises(password_credentials):
    client = SftpClient(
        host="sample-host",
        username="sample-username",
        credentials=password_credentials,
        destination_path="/sample/path",
        host_key_checking={"mode": "bogus"},
    )
    with pytest.raises(HostKeyError):
        client._apply_host_key_policy(paramiko.SSHClient())


def test_load_host_key_from_base64(host_key):
    parsed = _load_host_key(host_key.get_name(), host_key.get_base64())
    assert parsed.get_base64() == host_key.get_base64()


def test_load_host_key_from_known_hosts_line(host_key):
    """A full '<type> <base64> [comment]' line (as found in known_hosts) should parse."""
    line = f"{host_key.get_name()} {host_key.get_base64()} user@host"
    parsed = _load_host_key(host_key.get_name(), line)
    assert parsed.get_base64() == host_key.get_base64()


def test_load_host_key_invalid_base64(host_key):
    with pytest.raises(HostKeyError):
        _load_host_key(host_key.get_name(), "not-valid-base64!!!")


def test_load_host_key_unknown_type(host_key):
    """A valid key blob under an unrecognized type string should raise HostKeyError."""
    with pytest.raises(HostKeyError):
        _load_host_key("ssh-bogus", host_key.get_base64())


def test_load_host_key_empty():
    with pytest.raises(HostKeyError):
        _load_host_key("ssh-rsa", "   ")
