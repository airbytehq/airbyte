#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import errno
import io
import json
from typing import Dict, List, Mapping, Optional, TextIO

import paramiko


class SshKeyError(Exception):
    """Raised when an SSH private key cannot be parsed."""


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
    for key_class in _supported_key_classes():
        try:
            return key_class.from_private_key(io.StringIO(key_str))
        except paramiko.SSHException as err:
            last_error = err
    raise SshKeyError("Could not parse the provided SSH private key. Supported formats: RSA, Ed25519, ECDSA, DSA.") from last_error


class SftpClient:
    PASSWORD_AUTH = "SSH_PASSWORD_AUTH"
    KEY_AUTH = "SSH_KEY_AUTH"

    def __init__(
        self,
        host: str,
        username: str,
        credentials: Mapping[str, str],
        destination_path: str,
        port: int = 22,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.credentials = credentials
        self.destination_path = destination_path
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

    def _connect(self) -> None:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs: Dict[str, object] = {
            "hostname": self.host,
            "port": self.port,
            "username": self.username,
        }

        auth_method = self.credentials.get("auth_method")
        if auth_method == self.PASSWORD_AUTH:
            connect_kwargs["password"] = self.credentials["auth_user_password"]
            connect_kwargs["look_for_keys"] = False
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
