#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import binascii
import errno
import io
import json
from typing import Dict, List, Mapping, Optional, TextIO

import paramiko


class SshKeyError(Exception):
    """Raised when an SSH private key cannot be parsed."""


class HostKeyError(Exception):
    """Raised when the configured SSH host key cannot be parsed."""


def _supported_key_classes():
    # DSSKey was removed in newer paramiko releases (DSA is deprecated), so only
    # include the key types that the installed paramiko version actually exposes.
    candidates = ("RSAKey", "Ed25519Key", "ECDSAKey", "DSSKey")
    return tuple(getattr(paramiko, name) for name in candidates if hasattr(paramiko, name))


def _load_private_key(key_str: str) -> paramiko.PKey:
    """
    Parse a private key supplied as a PEM/OpenSSH string into a paramiko key object.

    The key type is not known ahead of time, so we attempt each of the key
    classes paramiko supports and return the first one that parses successfully.
    """
    last_error: Optional[Exception] = None
    supported: List[str] = []
    for key_class in _supported_key_classes():
        supported.append(key_class.__name__.removesuffix("Key").replace("DSS", "DSA"))
        try:
            return key_class.from_private_key(io.StringIO(key_str))
        except paramiko.SSHException as err:
            last_error = err
    raise SshKeyError(f"Could not parse the provided SSH private key. Supported formats: {', '.join(supported)}.") from last_error


def _load_host_key(key_type: str, key_str: str) -> paramiko.PKey:
    """
    Parse a server host public key (the ``type`` and ``key`` fields of a
    ``known_hosts`` entry) into a paramiko key object.

    ``key_str`` is the base64-encoded key blob, optionally still carrying the
    leading ``key_type`` token and/or a trailing comment, as is common when
    pasting a line straight out of ``known_hosts``.
    """
    token = key_str.strip().split()
    if not token:
        raise HostKeyError("No SSH host key was provided.")
    # Tolerate a full "<type> <base64> [comment]" line by stripping a leading
    # type token and ignoring any trailing comment.
    if len(token) > 1 and token[0] == key_type:
        token = token[1:]
    key_data = token[0]
    try:
        decoded = base64.b64decode(key_data, validate=True)
    except (binascii.Error, ValueError) as err:
        raise HostKeyError("The configured SSH host key is not valid base64.") from err
    try:
        return paramiko.PKey.from_type_string(key_type, decoded)
    except (paramiko.SSHException, paramiko.UnknownKeyType, ValueError) as err:
        raise HostKeyError(f"Could not parse the configured SSH host key of type {key_type!r}.") from err


class SftpClient:
    PASSWORD_AUTH = "SSH_PASSWORD_AUTH"
    KEY_AUTH = "SSH_KEY_AUTH"

    HOST_KEY_AUTO_ADD = "auto_add"
    HOST_KEY_STRICT = "strict"

    def __init__(
        self,
        host: str,
        username: str,
        credentials: Mapping[str, str],
        destination_path: str,
        port: int = 22,
        host_key_checking: Optional[Mapping[str, str]] = None,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.credentials = credentials
        self.destination_path = destination_path
        # Defaults to "auto_add" (trust on first use) for backward compatibility.
        self.host_key_checking: Mapping[str, str] = host_key_checking or {"mode": self.HOST_KEY_AUTO_ADD}
        self._ssh: Optional[paramiko.SSHClient] = None
        self._sftp: Optional[paramiko.SFTPClient] = None
        self._files: Dict[str, TextIO] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def sftp(self) -> paramiko.SFTPClient:
        """Lazily open (and cache) a single SFTP session for this client."""
        if self._sftp is None:
            self._connect()
        return self._sftp

    def _apply_host_key_policy(self, ssh: paramiko.SSHClient) -> None:
        """
        Configure how ``ssh`` verifies the server's host key based on the
        ``host_key_checking`` configuration.

        - ``auto_add`` (default): trust and cache the host key on first use via
          ``AutoAddPolicy``. Convenient, but offers no MITM protection.
        - ``strict``: pre-load the operator-supplied host key and use
          ``RejectPolicy`` so any unknown or mismatched key aborts the
          connection.
        """
        mode = self.host_key_checking.get("mode", self.HOST_KEY_AUTO_ADD)
        if mode == self.HOST_KEY_AUTO_ADD:
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        elif mode == self.HOST_KEY_STRICT:
            key_type = self.host_key_checking.get("host_key_type")
            key_str = self.host_key_checking.get("host_key")
            if not key_type or not key_str:
                raise HostKeyError("Strict host key checking requires both 'host_key_type' and 'host_key'.")
            host_key = _load_host_key(key_type, key_str)
            # Pin the expected key for this host/port and reject anything else.
            host_keys = ssh.get_host_keys()
            host_keys.add(self._host_key_lookup(), host_key.get_name(), host_key)
            ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        else:
            raise HostKeyError(f"Unsupported host key checking mode: {mode!r}")

    def _host_key_lookup(self) -> str:
        """
        Build the hostname token paramiko uses to look up a pinned host key.

        Paramiko stores non-default ports as ``[host]:port`` in its host-key
        registry, so mirror that here when a custom port is in use.
        """
        if self.port and self.port != 22:
            return f"[{self.host}]:{self.port}"
        return self.host

    def _connect(self) -> None:
        ssh = paramiko.SSHClient()
        self._apply_host_key_policy(ssh)
        connect_kwargs: Dict[str, object] = {
            "hostname": self.host,
            "port": self.port,
            "username": self.username,
        }

        auth_method = self.credentials.get("auth_method")
        if auth_method == self.PASSWORD_AUTH:
            connect_kwargs["password"] = self.credentials["auth_user_password"]
            connect_kwargs["look_for_keys"] = False
            connect_kwargs["allow_agent"] = False
        elif auth_method == self.KEY_AUTH:
            connect_kwargs["pkey"] = _load_private_key(self.credentials["auth_ssh_key"])
            connect_kwargs["look_for_keys"] = False
            connect_kwargs["allow_agent"] = False
        else:
            raise ValueError(f"Unsupported SFTP authentication method: {auth_method!r}")

        ssh.connect(**connect_kwargs)
        self._ssh = ssh
        self._sftp = ssh.open_sftp()

    def _get_path(self, stream: str) -> str:
        return f"{self.destination_path}/airbyte_json_{stream}.jsonl"

    def _open(self, stream: str, mode: str = "a+") -> paramiko.SFTPFile:
        path = self._get_path(stream)
        return self.sftp.open(path, mode=mode)

    def close(self):
        for file in self._files.values():
            file.close()
        self._files = {}
        if self._sftp is not None:
            self._sftp.close()
            self._sftp = None
        if self._ssh is not None:
            self._ssh.close()
            self._ssh = None

    def write(self, stream: str, record: Dict) -> None:
        if stream not in self._files:
            # Keep a long-lived append handle per stream so we don't pay the
            # cost of opening a new remote file for every record.
            self._files[stream] = self._open(stream, mode="a+")
        text = json.dumps(record)
        self._files[stream].write(f"{text}\n")

    def read_data(self, stream: str) -> List[Dict]:
        # Flush any buffered writes for this stream so the read reflects them.
        cached = self._files.get(stream)
        if cached is not None:
            cached.flush()
        with self._open(stream, mode="r") as file:
            lines = file.readlines()
        return [json.loads(line.strip()) for line in lines if line.strip()]

    def delete(self, stream: str) -> None:
        # Drop any cached write handle for this stream before removing the file.
        file = self._files.pop(stream, None)
        if file is not None:
            file.close()
        try:
            path = self._get_path(stream)
            self.sftp.remove(path)
        except IOError as err:
            # Ignore the case where the file doesn't exist, only raise the
            # exception if it's something else
            if err.errno != errno.ENOENT:
                raise
