#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import io
import logging
import os
import re
import socket
import stat
from datetime import datetime
from typing import Any, Dict, List, Mapping, Tuple

import backoff
import numpy as np
import pandas as pd
import paramiko
from paramiko.ssh_exception import AuthenticationException

# set default timeout to 300 seconds
REQUEST_TIMEOUT = 300

logger = logging.getLogger("airbyte")

File = Dict[str, Any]


class SFTPClient:
    _connection = None

    def __init__(self, host, username, destination_path, password=None, private_key=None, port=None, timeout=REQUEST_TIMEOUT):
        self.host = host
        self.username = username
        self.password = password
        self.port = int(port) or 22
        self.destination_path = destination_path
        self.key = paramiko.RSAKey.from_private_key(io.StringIO(private_key)) if private_key else None
        self.timeout = float(timeout) if timeout else REQUEST_TIMEOUT

        if not self.password and not self.key:
            raise Exception("Either password or private key must be provided")

        self._connect()

    def handle_backoff(details):
        logger.warning("SSH Connection closed unexpectedly. Waiting {wait} seconds and retrying...".format(**details))

    # If connection is snapped during connect flow, retry up to a
    # minute for SSH connection to succeed. 2^6 + 2^5 + ...
    @backoff.on_exception(backoff.expo, (EOFError), max_tries=6, on_backoff=handle_backoff, jitter=None, factor=2)
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

        except (AuthenticationException) as ex:
            raise Exception("Authentication failed: %s" % ex)
        except Exception as ex:
            raise Exception("SSH Connection failed: %s" % ex)

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self):
        """Clean up the socket when this class gets garbage collected."""
        self.close()

    def _get_path(self, stream: str) -> str:
        return f"{self.destination_path}/airbyte_csv_{stream}.csv"

    def close(self):
        if self._connection is not None:
            try:
                self._connection.close()
                self.transport.close()
                self._connection = None
            # Known paramiko issue: https://github.com/paramiko/paramiko/issues/1617
            except Exception as e:
                if str(e) != "'NoneType' object has no attribute 'time'":
                    raise

    # write csv file to SFTP server
    def write_csv(self, stream: str, record: Dict):
        if self._connection is not None:
            try:
                path = self._get_path(stream)
                csv = pd.DataFrame(record)
                csv = csv.to_csv(index=False, header=True)
                self._connection.putfo(io.StringIO(csv), path)
            except Exception as ex:
                raise Exception("SFTP write failed: %s" % ex)

    # delete file from SFTP server
    def delete_file(self, file_name):
        if self._connection is not None:
            try:
                self._connection.remove(file_name)
            except Exception as ex:
                raise Exception("SFTP delete failed: %s" % ex)




