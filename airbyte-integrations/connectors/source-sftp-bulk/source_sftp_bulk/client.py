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

    def __init__(self, host, username, password=None, private_key=None, port=None, timeout=REQUEST_TIMEOUT):
        self.host = host
        self.username = username
        self.password = password
        self.port = int(port) or 22

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

    @staticmethod
    def get_files_matching_pattern(files, pattern) -> List[File]:
        """Takes a file dict {"filepath": "...", "last_modified": "..."} and a regex pattern string, and returns files matching that pattern."""
        matcher = re.compile(pattern)
        return [f for f in files if matcher.search(f["filepath"])]

    # backoff for 60 seconds as there is possibility the request will backoff again in 'discover.get_schema'
    @backoff.on_exception(backoff.constant, (socket.timeout), max_time=60, interval=10, jitter=None)
    def get_files_by_prefix(self, prefix: str) -> List[File]:
        def is_empty(a):
            return a.st_size == 0

        def is_directory(a):
            return stat.S_ISDIR(a.st_mode)

        files = []

        if prefix is None or prefix == "":
            prefix = "."

        try:
            result = self._connection.listdir_attr(prefix)
        except FileNotFoundError as e:
            raise Exception("Directory '{}' does not exist".format(prefix)) from e

        for file_attr in result:
            # NB: This only looks at the immediate level beneath the prefix directory
            if is_directory(file_attr):
                logger.info("Skipping directory: %s", file_attr.filename)
            else:
                if is_empty(file_attr):
                    logger.info("Skipping empty file: %s", file_attr.filename)
                    continue

                last_modified = file_attr.st_mtime
                if last_modified is None:
                    logger.warning(
                        "Cannot read m_time for file %s, defaulting to current epoch time", os.path.join(prefix, file_attr.filename)
                    )
                    last_modified = datetime.utcnow().timestamp()

                files.append(
                    {
                        "filepath": prefix + "/" + file_attr.filename,
                        "last_modified": datetime.utcfromtimestamp(last_modified).replace(tzinfo=None),
                    }
                )

        return files

    def get_files(self, prefix, search_pattern=None, modified_since=None, most_recent_only=False) -> List[File]:
        files = self.get_files_by_prefix(prefix)

        if files:
            logger.info('Found %s files in "%s"', len(files), prefix)
        else:
            logger.warning('Found no files on specified SFTP server at "%s"', prefix)

        matching_files = files

        if search_pattern is not None:
            matching_files = self.get_files_matching_pattern(files, search_pattern)

        if matching_files and search_pattern:
            logger.info('Found %s files in "%s" matching "%s"', len(matching_files), prefix, search_pattern)

        if not matching_files and search_pattern:
            logger.warning('Found no files on specified SFTP server at "%s" matching "%s"', prefix, search_pattern)

        if modified_since is not None:
            matching_files = [f for f in matching_files if f["last_modified"] > modified_since]

        # sort files in increasing order of "last_modified"
        sorted_files = sorted(matching_files, key=lambda x: (x["last_modified"]).timestamp())

        if most_recent_only:
            logger.info(f"Returning only the most recently modified file: {sorted_files[-1]}.")
            sorted_files = sorted_files[-1:]

        return sorted_files

    @backoff.on_exception(backoff.expo, (socket.timeout), max_tries=5, factor=2)
    def fetch_file(self, fn: Mapping[str, Any], file_type="csv") -> pd.DataFrame:
        try:
            with self._connection.open(fn["filepath"], "rb") as f:
                df: pd.DataFrame = None

                # Using pandas to make reading files in different formats easier
                if file_type == "csv":
                    df = pd.read_csv(f)
                elif file_type == "json":
                    df = pd.read_json(f, lines=True)
                else:
                    raise Exception("Unsupported file type: %s" % file_type)

                # Replace nan with None for correct
                # json serialization when emitting records
                df = df.replace({np.nan: None})
                df["last_modified"] = fn["last_modified"]
                return df

        except OSError as e:
            if "Permission denied" in str(e):
                logger.warning("Skipping %s file because you do not have enough permissions.", f["filepath"])
            else:
                logger.warning("Skipping %s file because it is unable to be read.", f["filepath"])

            raise Exception("Unable to read file: %s" % e) from e

    def fetch_files(self, files, file_type="csv") -> Tuple[datetime, Dict[str, Any]]:
        logger.info("Fetching %s files", len(files))
        for fn in files:
            records = self.fetch_file(fn, file_type)
            yield (fn["last_modified"], records.to_dict("records"))

        self.close()
