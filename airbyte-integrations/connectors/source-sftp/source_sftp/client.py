import ast
import os
import re
import socket
import stat
from datetime import datetime

import backoff
import pandas as pd
import paramiko
import pytz
from airbyte_cdk.entrypoint import logger

# set default timeout to 300 seconds
REQUEST_TIMEOUT = 300
CHUNK_SIZE = 10000


def handle_backoff(details):
    logger.warning(
        "SSH Connection closed unexpectedly. Waiting {wait} seconds and retrying...".format(
            **details
        )
    )


class Client:
    def __init__(self, host, username, password=None, port=None, timeout=REQUEST_TIMEOUT, reader_config=None):
        self.host = host
        self.username = username
        self.password = password
        self.port = int(port) or 22
        self.__active_connection = False
        self.key = None
        self.reader_config = reader_config or {}
        self.transport : paramiko.Transport = None

        if timeout and float(timeout):
            # set the request timeout for the requests
            # if value is 0,"0", "" or None then it will set default to default to 300.0 seconds if not passed in config.
            self.request_timeout = float(timeout)
        else:
            # set the default timeout of 300 seconds
            self.request_timeout = REQUEST_TIMEOUT

    # If connection is snapped during connect flow, retry up to a
    # minute for SSH connection to succeed. 2^6 + 2^5 + ...
    @backoff.on_exception(
        backoff.expo, (EOFError), max_tries=6, on_backoff=handle_backoff, jitter=None, factor=2
    )
    def __try_connect(self):
        if not self.__active_connection:
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.use_compression(True)
            self.transport.connect(
                username=self.username, password=self.password, hostkey=None, pkey=None
            )
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            self.__active_connection = True
            # get 'socket' to set the timeout
            _socket = self.sftp.get_channel()
            # set request timeout
            _socket.settimeout(self.request_timeout)

    @property
    def sftp(self) -> paramiko.SFTPClient:
        self.__try_connect()
        return self.__sftp

    @sftp.setter
    def sftp(self, sftp):
        self.__sftp = sftp

    def __enter__(self):
        self.__try_connect()
        return self

    def __del__(self):
        """Clean up the socket when this class gets garbage collected."""
        self.close()

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Clean up the socket when this class gets garbage collected."""
        self.close()

    def close(self):
        if self.__active_connection:
            logger.info("Close SFTP connection")
            self.sftp.close()
            self.transport.close()
            self.__active_connection = False

    def match_files_for_table(self, files, table_name, search_pattern):
        logger.info(
            "Searching for files for table '%s', matching pattern: %s", table_name, search_pattern
        )
        matcher = re.compile(search_pattern)
        return [f for f in files if matcher.search(f["filepath"])]

    # backoff for 60 seconds as there is possibility the request will backoff again in 'discover.get_schema'
    @backoff.on_exception(backoff.constant, (socket.timeout), max_time=60, interval=10, jitter=None)
    def get_files_by_prefix(self, prefix):
        """
        Accesses the underlying file system and gets all files that match "prefix", in this case, a directory path.

        Returns a list of filepaths from the root.
        """
        files = []

        if prefix is None or prefix == "":
            prefix = "."

        try:
            result = self.sftp.listdir_attr(prefix)
        except FileNotFoundError as exc:
            raise Exception("Directory '{}' does not exist".format(prefix)) from exc

        for file_attr in result:
            # NB: This only looks at the immediate level beneath the prefix directory
            if stat.S_ISDIR(file_attr.st_mode):  # Check if it is a directory
                files += self.get_files_by_prefix(prefix + "/" + file_attr.filename)
            else:
                if file_attr.st_size == 0:  # Check if file is empty
                    continue

                last_modified = file_attr.st_mtime
                if last_modified is None:
                    logger.warning(
                        "Cannot read m_time for file %s, defaulting to current epoch time",
                        os.path.join(prefix, file_attr.filename),
                    )
                    last_modified = datetime.utcnow().timestamp()

                # NB: SFTP specifies path characters to be '/'
                #     https://tools.ietf.org/html/draft-ietf-secsh-filexfer-13#section-6
                files.append(
                    {
                        "filepath": prefix + "/" + file_attr.filename,
                        "last_modified": datetime.utcfromtimestamp(last_modified).replace(
                            tzinfo=pytz.UTC
                        ),
                    }
                )

        return files

    def get_files(self, prefix, search_pattern, modified_since=None):
        files = self.get_files_by_prefix(prefix)
        if files:
            logger.info('Found %s files in "%s"', len(files), prefix)
        else:
            logger.warning('Found no files on specified SFTP server at "%s"', prefix)

        matching_files = self.get_files_matching_pattern(files, search_pattern)

        if matching_files:
            logger.info(
                'Found %s files in "%s" matching "%s"', len(matching_files), prefix, search_pattern
            )
        else:
            logger.warning(
                'Found no files on specified SFTP server at "%s" matching "%s"',
                prefix,
                search_pattern,
            )

        if modified_since is not None:
            logger.info("Select files modified after %s", modified_since)
            matching_files = [f for f in matching_files if f["last_modified"] > modified_since]
            logger.info("Found %s files modified after %s", len(matching_files), modified_since)

        for f in matching_files:
            logger.debug("Found file to sync: %s", f["filepath"])

        # sort files in increasing order of "last_modified"
        sorted_files = sorted(matching_files, key=lambda x: (x["last_modified"]).timestamp())
        return sorted_files

    def get_files_matching_pattern(self, files, pattern):
        """Takes a file dict {"filepath": "...", "last_modified": "..."} and a regex pattern string, and returns files matching that pattern."""
        logger.info("Filter file by pattern: %s", pattern)
        matcher = re.compile(pattern)
        return [f for f in files if matcher.search(f["filepath"])]

    @staticmethod
    def dtype_to_json_type(dtype) -> str:
        """Convert Pandas Dataframe types to Airbyte Types.

        :param dtype: Pandas Dataframe type
        :return: Corresponding Airbyte Type
        """
        if dtype == object:
            return "string"
        elif dtype in ("int64", "float64"):
            return "number"
        elif dtype == "bool":
            return "boolean"
        return "string"

    @backoff.on_exception(backoff.expo, (socket.timeout), max_tries=5, factor=2)
    def load_dataframes(self, file_path, skip_data=False):
        _reader_config = {**self.reader_config}
        _reader_config["chunksize"] = CHUNK_SIZE
        if skip_data:
            _reader_config["nrows"] = 0
            _reader_config["index_col"] = 0
        
        logger.debug("Load dataframe from file %s, with read options: %s", file_path, _reader_config)
        with self.sftp.open(file_path, "r") as file:
            # file.prefetch()
            yield from pd.read_csv(file, **_reader_config)

    def read(self, file_path, fields=None, skip_data=False):
        fields = set(fields) if fields else None
        for dataframe in self.load_dataframes(file_path, skip_data=skip_data):
            sync_columns = fields.intersection(set(dataframe.columns)) if fields else dataframe.columns
            dataframe = dataframe.where(pd.notnull(dataframe), None)
            yield from dataframe[sync_columns].to_dict(orient="records")

    def get_file_properties(self, file_path):
        logger.info("Get file properties")
        fields = {}
        for dataframe in self.load_dataframes(file_path, skip_data=False):
            for column in dataframe.columns:
                fields[column] = self.dtype_to_json_type(dataframe[column].dtype)
        return {k: {"type": [v, "null"]} for k, v in fields.items()}


def get_client(config):
    return Client(
        config["host"],
        config["user"],
        password=config.get("password"),
        port=config.get("port"),
        timeout=config.get("request_timeout"),
        reader_config=ast.literal_eval(config.get("reader_config", "{}")),
    )
