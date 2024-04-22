#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import logging
from typing import Optional

import backoff
import paramiko
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType
from paramiko.ssh_exception import AuthenticationException

# set default timeout to 300 seconds
REQUEST_TIMEOUT = 300

logger = logging.getLogger("airbyte")


def handle_backoff(details):
    logger.warning("SSH Connection closed unexpectedly. Waiting {wait} seconds and retrying...".format(**details))


class SFTPClient:
    _connection: paramiko.SFTPClient = None

    def __init__(
        self,
        host: str,
        username: str,
        password: str = None,
        private_key: Optional[str] = None,
        port: Optional[int] = None,
        timeout: Optional[int] = REQUEST_TIMEOUT,
    ):
        self.host = host
        self.username = username
        self.password = password
        self.port = int(port) or 22

        self.key = paramiko.RSAKey.from_private_key(io.StringIO(private_key)) if private_key else None
        self.timeout = float(timeout) if timeout else REQUEST_TIMEOUT

        self._connect()

    # If connection is snapped during connect flow, retry up to a
    # minute for SSH connection to succeed. 2^6 + 2^5 + ...
    @backoff.on_exception(backoff.expo, EOFError, max_tries=6, on_backoff=handle_backoff, jitter=None, factor=2)
    def _connect(self):
        if self._connection is not None:
            return

        try:
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.use_compression(True)
            self.transport.connect(username=self.username, password=self.password, hostkey=None, pkey=self.key)
            self._connection = paramiko.SFTPClient.from_transport(self.transport)

            # get 'socket' to set the timeout
            socket = self._connection.get_channel()
            # set request timeout
            socket.settimeout(self.timeout)

        except AuthenticationException as ex:
            raise AirbyteTracedException(
                failure_type=FailureType.config_error,
                message="SSH Authentication failed, please check username, password or private key and try again",
                internal_message="Authentication failed: %s" % ex,
            )

    def __del__(self):
        if self._connection is not None:
            try:
                self._connection.close()
                self.transport.close()
                self._connection = None
            # Known paramiko issue: https://github.com/paramiko/paramiko/issues/1617
            except Exception as e:
                if str(e) != "'NoneType' object has no attribute 'time'":
                    raise

    @property
    def sftp_connection(self) -> paramiko.SFTPClient:
        return self._connection
