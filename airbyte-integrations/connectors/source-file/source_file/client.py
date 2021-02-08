"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import traceback
from typing import Iterable, List
from urllib.parse import urlparse

import google
import numpy as np
import pandas as pd
import smart_open
from airbyte_protocol import AirbyteStream
from base_python.entrypoint import logger
from botocore import UNSIGNED
from botocore.config import Config
from genson import SchemaBuilder
from google.cloud.storage import Client as GCSClient
from google.oauth2 import service_account


class ConfigurationError(Exception):
    """Client mis-configured"""


class PermissionsError(Exception):
    """User don't have enough permissions"""


class URLFile:
    """Class to manage read from file located at different providers

    Supported examples of URL this class can accept are as follows:
    ```
        s3://my_bucket/my_key
        s3://my_key:my_secret@my_bucket/my_key
        gs://my_bucket/my_blob
        hdfs:///path/file (not tested)
        hdfs://path/file (not tested)
        webhdfs://host:port/path/file (not tested)
        ./local/path/file
        ~/local/path/file
        local/path/file
        ./local/path/file.gz
        file:///home/user/file
        file:///home/user/file.bz2
        [ssh|scp|sftp]://username@host//path/file
        [ssh|scp|sftp]://username@host/path/file
        [ssh|scp|sftp]://username:password@host/path/file
    ```
    """

    def __init__(self, url: str, provider: dict):
        self._url = url
        self._provider = provider
        self._file = None

    def __enter__(self):
        return self._file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def full_url(self):
        return f"{self.storage_scheme}{self.url}"

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def open(self, binary=False):
        self.close()
        try:
            self._file = self._open(binary=binary)
        except google.api_core.exceptions.NotFound as err:
            raise FileNotFoundError(self.url) from err
        return self

    def _open(self, binary):
        mode = "rb" if binary else "r"
        storage = self.storage_scheme
        url = self.url

        if storage == "gs://":
            return self._open_gcs_url(binary=binary)
        elif storage == "s3://":
            return self._open_aws_url(binary=binary)
        elif storage == "webhdfs://":
            host = self._provider["host"]
            port = self._provider["port"]
            return smart_open.open(f"webhdfs://{host}:{port}/{url}", mode=mode)
        elif storage in ("ssh://", "scp://", "sftp://"):
            user = self._provider["user"]
            host = self._provider["host"]
            port = self._provider.get("port", 22)
            # Explicitly turn off ssh keys stored in ~/.ssh
            transport_params = {"connect_kwargs": {"look_for_keys": False}}
            if "password" in self._provider:
                password = self._provider["password"]
                uri = f"{storage}{user}:{password}@{host}:{port}/{url}"
            else:
                uri = f"{storage}{user}@{host}:{port}/{url}"
            return smart_open.open(uri, transport_params=transport_params, mode=mode)
        return smart_open.open(self.full_url, mode=mode)

    @property
    def url(self) -> str:
        """Convert URL to remove the URL prefix (scheme)
        :return: the corresponding URL without URL prefix / scheme
        """
        parse_result = urlparse(self._url)
        if parse_result.scheme:
            return self._url.split("://")[-1]
        else:
            return self._url

    @property
    def storage_scheme(self) -> str:
        """Convert Storage Names to the proper URL Prefix
        :return: the corresponding URL prefix / scheme
        """
        storage_name = self._provider["storage"].upper()
        parse_result = urlparse(self._url)
        if storage_name == "GCS":
            return "gs://"
        elif storage_name == "S3":
            return "s3://"
        elif storage_name == "HTTPS":
            return "https://"
        elif storage_name == "SSH" or storage_name == "SCP":
            return "scp://"
        elif storage_name == "SFTP":
            return "sftp://"
        elif storage_name == "WEBHDFS":
            return "webhdfs://"
        elif storage_name == "LOCAL":
            return "file://"
        elif parse_result.scheme:
            return parse_result.scheme

        logger.error(f"Unknown Storage provider in: {self.full_url}")
        return ""

    def _open_gcs_url(self, binary) -> object:
        mode = "rb" if binary else "r"
        service_account_json = self._provider.get("service_account_json")
        credentials = None
        if service_account_json:
            try:
                credentials = json.loads(self._provider["service_account_json"])
            except json.decoder.JSONDecodeError as err:
                error_msg = f"Failed to parse gcs service account json: {repr(err)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                raise ConfigurationError(error_msg) from err

        if credentials:
            credentials = service_account.Credentials.from_service_account_info(credentials)
            client = GCSClient(credentials=credentials, project=credentials._project_id)
        else:
            client = GCSClient.create_anonymous_client()
        file_to_close = smart_open.open(self.full_url, transport_params=dict(client=client), mode=mode)

        return file_to_close

    def _open_aws_url(self, binary):
        mode = "rb" if binary else "r"
        aws_access_key_id = self._provider.get("aws_access_key_id")
        aws_secret_access_key = self._provider.get("aws_secret_access_key")
        use_aws_account = aws_access_key_id and aws_secret_access_key

        if use_aws_account:
            aws_access_key_id = self._provider.get("aws_access_key_id", "")
            aws_secret_access_key = self._provider.get("aws_secret_access_key", "")
            result = smart_open.open(f"{self.storage_scheme}{aws_access_key_id}:{aws_secret_access_key}@{self.url}", mode=mode)
        else:
            config = Config(signature_version=UNSIGNED)
            params = {
                "resource_kwargs": {"config": config},
            }
            result = smart_open.open(self.full_url, transport_params=params, mode=mode)
        return result


class Client:
    """Class that manages reading and parsing data from streams"""

    reader_class = URLFile

    def __init__(self, dataset_name: str, url: str, provider: dict, format: str = None, reader_options: str = None):
        self._dataset_name = dataset_name
        self._url = url
        self._provider = provider
        self._reader_format = format or "csv"
        self._reader_options = {}
        if reader_options:
            try:
                self._reader_options = json.loads(reader_options)
            except json.decoder.JSONDecodeError as err:
                error_msg = f"Failed to parse reader options {repr(err)}\n{reader_options}\n{traceback.format_exc()}"
                logger.error(error_msg)
                raise ConfigurationError(error_msg) from err

    @property
    def stream_name(self) -> str:
        if self._dataset_name:
            return self._dataset_name
        return f"file_{self._provider['storage']}.{self._reader_format}"

    @staticmethod
    def load_nested_json_schema(fp) -> dict:
        # Use Genson Library to take JSON objects and generate schemas that describe them,
        builder = SchemaBuilder()
        builder.add_object(json.load(fp))
        result = builder.to_schema()
        if "items" in result and "properties" in result["items"]:
            result = result["items"]["properties"]
        return result

    @staticmethod
    def load_nested_json(fp) -> list:
        result = json.load(fp)
        if not isinstance(result, list):
            result = [result]
        return result

    def load_dataframes(self, fp, skip_data=False) -> List:
        """load and return the appropriate pandas dataframe.

        :param fp: file-like object to read from
        :param skip_data: limit reading data
        :return: a list of dataframe loaded from files described in the configuration
        """
        readers = {
            # pandas.read_csv additional arguments can be passed to customize how to parse csv.
            # see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
            "csv": pd.read_csv,
            # We can add option to call to pd.normalize_json to normalize semi-structured JSON data into a flat table
            # by asking user to specify how to flatten the nested columns
            "flat_json": pd.read_json,
            "html": pd.read_html,
            "excel": pd.read_excel,
            "feather": pd.read_feather,
            "parquet": pd.read_parquet,
            "orc": pd.read_orc,
            "pickle": pd.read_pickle,
        }

        try:
            reader = readers[self._reader_format]
        except KeyError as err:
            error_msg = f"Reader {self._reader_format} is not supported\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg) from err

        reader_options = {**self._reader_options}
        if skip_data and self._reader_format == "csv":
            reader_options["nrows"] = 0
            reader_options["index_col"] = 0

        return [reader(fp, **reader_options)]

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

    @property
    def reader(self) -> reader_class:
        return self.reader_class(url=self._url, provider=self._provider)

    @property
    def binary_source(self):
        binary_formats = {"excel", "feather", "parquet", "orc", "pickle"}
        return self._reader_format in binary_formats

    def read(self, fields: Iterable = None) -> Iterable[dict]:
        """Read data from the stream"""
        with self.reader.open(binary=self.binary_source) as fp:
            if self._reader_format == "json":
                yield from self.load_nested_json(fp)
            else:
                for df in self.load_dataframes(fp):
                    columns = set(fields).intersection(set(df.columns)) if fields else df.columns
                    df = df.replace(np.nan, "NaN", regex=True)
                    yield from df[columns].to_dict(orient="records")

    def _stream_properties(self):
        with self.reader.open(binary=self.binary_source) as fp:
            if self._reader_format == "json":
                return self.load_nested_json_schema(fp)

            df_list = self.load_dataframes(fp, skip_data=False)
            fields = {}
            for df in df_list:
                for col in df.columns:
                    fields[col] = self.dtype_to_json_type(df[col].dtype)
            return {field: {"type": fields[field]} for field in fields}

    @property
    def streams(self) -> Iterable:
        """Discovers available streams"""
        # TODO handle discovery of directories of multiple files instead
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": self._stream_properties(),
        }
        yield AirbyteStream(name=self.stream_name, json_schema=json_schema)
