#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Optional

import asyncssh
import backoff
from airbyte_cdk import AirbyteTracedException, FailureType
from asyncssh.connection import SFTPClient, SSHClientConnection

# set default timeout to 300 seconds
REQUEST_TIMEOUT = 300

logger = logging.getLogger("airbyte")


def handle_backoff(details):
    logger.warning("SSH Connection closed unexpectedly. Waiting {wait} seconds and retrying...".format(**details))


class SFTPFileTransferClient:
    _connection: Optional[SFTPClient] = None
    conn: Optional[SSHClientConnection] = None

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

        self.key = asyncssh.import_private_key(private_key) if private_key else None
        self.timeout = float(timeout) if timeout else REQUEST_TIMEOUT

    # If connection is snapped during connect flow, retry up to a
    # minute for SSH connection to succeed. 2^6 + 2^5 + ...
    @backoff.on_exception(backoff.expo, EOFError, max_tries=6, on_backoff=handle_backoff, jitter=None, factor=2)
    async def _connect(self):
        if self._connection is not None:
            return self._connection

        try:

            self.conn = await asyncssh.connect(
                self.host, username=self.username, client_keys=[self.key] if self.key else None, password=self.password
            )
            # Start the SFTP client
            self._connection = await self.conn.start_sftp_client()
            return self._connection

        except asyncssh.Error as ex:
            raise AirbyteTracedException(
                failure_type=FailureType.config_error,
                message="SSH Authentication failed, please check username, password or private key and try again",
                internal_message="Authentication failed: %s" % ex,
            )
        except Exception as ex:
            raise ex

    def __del__(self):
        """Async method to clean up and close connections."""
        if self._connection:
            self._connection.exit()
        if self.conn:
            self.conn.close()
            self.conn.wait_closed()
        self._connection = None
        self.conn = None

    @property
    async def sftp_connection(self) -> SFTPClient:
        if self._connection is not None:
            return self._connection
        return await self._connect()
