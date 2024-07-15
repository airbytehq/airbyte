# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from unittest.mock import MagicMock, patch

import paramiko
import pytest
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
