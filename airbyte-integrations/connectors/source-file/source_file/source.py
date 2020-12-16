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
import os
import tempfile
import traceback
from datetime import datetime
from typing import Dict, Generator, List
from urllib.parse import urlparse

import gcsfs
import numpy as np
import pandas as pd
from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from base_python import Source
from botocore import UNSIGNED
from botocore.config import Config
from genson import SchemaBuilder
from google.cloud.storage import Client
from s3fs import S3FileSystem
from smart_open import open


class SourceFile(Source):
    """This source aims to provide support for readers of different file formats stored in various locations.

    It is optionally using s3fs, gcfs or smart_open libraries to handle efficient streaming of very large files
    (either compressed or not).

    Supported examples of URL this can accept are as follows:
    ```
        s3://my_bucket/my_key
        s3://my_key:my_secret@my_bucket/my_key
        gs://my_bucket/my_blob
        azure://my_bucket/my_blob (not tested)
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

    The source reader currently leverages `read_csv` but will be extended to readers of different formats for
    more potential sources as described below:
    https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html
    - read_json
    - read_html
    - read_excel
    - read_feather
    - read_parquet
    - read_orc
    - read_pickle

    All the options of the readers are exposed to the configuration file of this connector so it is possible to
    override header names, types, encoding, etc

    Note that this implementation is handling `url` target as a single file at the moment.
    We will expand the capabilities of this source to discover and load either glob of multiple files,
    content of directories, etc in a latter iteration.
    """

    def check(self, logger, config: json) -> AirbyteConnectionStatus:
        """
        Check involves verifying that the specified file is reachable with
        our credentials.
        """
        storage = SourceFile.get_storage_scheme(logger, config["provider"]["storage"], config["url"])
        url = SourceFile.get_simple_url(config["url"])
        logger.info(f"Checking access to {storage}{url}...")
        try:
            SourceFile.open_file_url(config, logger)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            reason = f"Failed to load {storage}{url}: {repr(err)}\n{traceback.format_exc()}"
            logger.error(reason)
            return AirbyteConnectionStatus(status=Status.FAILED, message=reason)

    def discover(self, logger, config: json) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams and fields in this integration. For example, given valid credentials to a
        Remote CSV File, returns an Airbyte catalog where each csv file is a stream, and each column is a field.
        """
        storage = SourceFile.get_storage_scheme(logger, config["provider"]["storage"], config["url"])
        url = SourceFile.get_simple_url(config["url"])
        name = SourceFile.get_stream_name(config)
        logger.info(f"Discovering schema of {name} at {storage}{url}...")
        streams = []
        try:
            # TODO handle discovery of directories of multiple files instead
            if "format" in config and config["format"] == "json":
                schema = SourceFile.load_nested_json_schema(config, logger)
                json_schema = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": schema,
                }
            else:
                # Don't skip data when discovering in order to infer column types
                df_list = SourceFile.load_dataframes(config, logger, skip_data=False)
                fields = {}
                for df in df_list:
                    for col in df.columns:
                        fields[col] = SourceFile.convert_dtype(df[col].dtype)
                json_schema = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {field: {"type": fields[field]} for field in fields},
                }
            streams.append(AirbyteStream(name=name, json_schema=json_schema))
        except Exception as err:
            reason = f"Failed to discover schemas of {name} at {storage}{url}: {repr(err)}\n{traceback.format_exc()}"
            logger.error(reason)
            raise err
        return AirbyteCatalog(streams=streams)

    def read(self, logger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]) -> Generator[AirbyteMessage, None, None]:
        """
        Returns a generator of the AirbyteMessages generated by reading the source with the given configuration, catalog, and state.
        """
        storage = SourceFile.get_storage_scheme(logger, config["provider"]["storage"], config["url"])
        url = SourceFile.get_simple_url(config["url"])
        name = SourceFile.get_stream_name(config)
        logger.info(f"Reading {name} ({storage}{url})...")
        selection = SourceFile.parse_catalog(catalog)
        try:
            if "format" in config and config["format"] == "json":
                data_list = SourceFile.load_nested_json(config, logger)
                for data in data_list:
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(stream=name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                    )
            else:
                df_list = SourceFile.load_dataframes(config, logger)
                for df in df_list:
                    if len(selection) > 0:
                        columns = selection.intersection(set(df.columns))
                    else:
                        columns = df.columns
                    df = df.replace(np.nan, "NaN", regex=True)
                    for data in df[columns].to_dict(orient="records"):
                        yield AirbyteMessage(
                            type=Type.RECORD,
                            record=AirbyteRecordMessage(stream=name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                        )
        except Exception as err:
            reason = f"Failed to read data of {name} at {storage}{url}: {repr(err)}\n{traceback.format_exc()}"
            logger.error(reason)
            raise err

    @staticmethod
    def get_stream_name(config) -> str:
        if "dataset_name" in config:
            name = config["dataset_name"]
        else:
            reader_format = "csv"
            if "format" in config:
                reader_format = config["format"]
            name = f"file_{config['provider']['storage']}.{reader_format}"
        return name

    @staticmethod
    def open_file_url(config, logger):
        storage = SourceFile.get_storage_scheme(logger, config["provider"]["storage"], config["url"])
        url = SourceFile.get_simple_url(config["url"])

        file_to_close = None
        if storage == "gs://":
            result, file_to_close = SourceFile.open_gcs_url(config, logger, storage, url)
        elif storage == "s3://":
            result = SourceFile.open_aws_url(config, logger, storage, url)
        elif storage == "webhdfs://":
            host = config["provider"]["host"]
            port = config["provider"]["port"]
            result = open(f"webhdfs://{host}:{port}/{url}")
        elif storage == "ssh://" or storage == "scp://" or storage == "sftp://":
            user = config["provider"]["user"]
            host = config["provider"]["host"]
            if "password" in config["provider"]:
                password = config["provider"]["password"]
                # Explicitly turn off ssh keys stored in ~/.ssh
                transport_params = {"connect_kwargs": {"look_for_keys": False}}
                result = open(f"{storage}{user}:{password}@{host}/{url}", transport_params=transport_params)
            else:
                result = open(f"{storage}{user}@{host}/{url}")
            file_to_close = result
        else:
            result = open(f"{storage}{url}")
        return result, file_to_close

    @staticmethod
    def open_gcs_url(config, logger, storage, url):
        reader_impl = SourceFile.extract_reader_impl(config)
        use_gcs_service_account = "service_account_json" in config["provider"] and storage == "gs://"
        file_to_close = None
        if reader_impl == "gcsfs":
            if use_gcs_service_account:
                try:
                    token_dict = json.loads(config["provider"]["service_account_json"])
                except json.decoder.JSONDecodeError as err:
                    logger.error(f"Failed to parse gcs service account json: {repr(err)}\n{traceback.format_exc()}")
                    raise err
            else:
                token_dict = "anon"
            fs = gcsfs.GCSFileSystem(token=token_dict)
            file_to_close = fs.open(f"gs://{url}")
            result = file_to_close
        else:
            if use_gcs_service_account:
                try:
                    credentials = json.dumps(json.loads(config["provider"]["service_account_json"]))
                    tmp_service_account = tempfile.NamedTemporaryFile(delete=False)
                    with open(tmp_service_account, "w") as f:
                        f.write(credentials)
                    tmp_service_account.close()
                    client = Client.from_service_account_json(tmp_service_account.name)
                    result = open(f"gs://{url}", transport_params=dict(client=client))
                    os.remove(tmp_service_account.name)
                except json.decoder.JSONDecodeError as err:
                    logger.error(f"Failed to parse gcs service account json: {repr(err)}\n{traceback.format_exc()}")
                    raise err
            else:
                client = Client.create_anonymous_client()
                result = open(f"{storage}{url}", transport_params=dict(client=client))
        return result, file_to_close

    @staticmethod
    def open_aws_url(config, _, storage, url):
        reader_impl = SourceFile.extract_reader_impl(config)
        use_aws_account = "aws_access_key_id" in config["provider"] and "aws_secret_access_key" in config["provider"] and storage == "s3://"
        if reader_impl == "s3fs":
            if use_aws_account:
                aws_access_key_id = None
                if "aws_access_key_id" in config["provider"]:
                    aws_access_key_id = config["provider"]["aws_access_key_id"]
                aws_secret_access_key = None
                if "aws_secret_access_key" in config["provider"]:
                    aws_secret_access_key = config["provider"]["aws_secret_access_key"]
                s3 = S3FileSystem(anon=False, key=aws_access_key_id, secret=aws_secret_access_key)
                result = s3.open(f"s3://{url}", mode="r")
            else:
                s3 = S3FileSystem(anon=True)
                result = s3.open(f"s3://{url}", mode="r")
        else:
            if use_aws_account:
                aws_access_key_id = ""
                if "aws_access_key_id" in config["provider"]:
                    aws_access_key_id = config["provider"]["aws_access_key_id"]
                aws_secret_access_key = ""
                if "aws_secret_access_key" in config["provider"]:
                    aws_secret_access_key = config["provider"]["aws_secret_access_key"]
                result = open(f"s3://{aws_access_key_id}:{aws_secret_access_key}@{url}")
            else:
                config = Config(signature_version=UNSIGNED)
                params = {
                    "resource_kwargs": {"config": config},
                }
                result = open(f"{storage}{url}", transport_params=params)
        return result

    @staticmethod
    def extract_reader_impl(config):
        # default reader impl
        reader_impl = ""
        if "reader_impl" in config["provider"]:
            reader_impl = config["provider"]["reader_impl"]
        return reader_impl

    @staticmethod
    def load_nested_json_schema(config, logger) -> dict:
        url, file_to_close = SourceFile.open_file_url(config, logger)
        try:
            # Use Genson Library to take JSON objects and generate schemas that describe them,
            builder = SchemaBuilder()
            builder.add_object(json.load(url))
            result = builder.to_schema()
            if "items" in result and "properties" in result["items"]:
                result = result["items"]["properties"]
        finally:
            if file_to_close:
                file_to_close.close()
        return result

    @staticmethod
    def load_nested_json(config, logger) -> list:
        url, file_to_close = SourceFile.open_file_url(config, logger)
        try:
            result = json.load(url)
            if isinstance(result, dict):
                result = [result]
        finally:
            if file_to_close:
                file_to_close.close()
        return result

    @staticmethod
    def load_dataframes(config, logger, skip_data=False) -> List:
        """From an Airbyte Configuration file, load and return the appropriate pandas dataframe.

        :param skip_data: limit reading data
        :param config:
        :param logger:
        :return: a list of dataframe loaded from files described in the configuration
        """
        # default format reader
        reader_format = "csv"
        if "format" in config:
            reader_format = config["format"]
        reader_options: dict = {}
        if "reader_options" in config:
            try:
                reader_options = json.loads(config["reader_options"])
            except json.decoder.JSONDecodeError as err:
                logger.error(f"Failed to parse reader options {repr(err)}\n{config['reader_options']}\n{traceback.format_exc()}")
        if skip_data and reader_format == "csv":
            reader_options["nrows"] = 0
            reader_options["index_col"] = 0
        url, file_to_close = SourceFile.open_file_url(config, logger)
        try:
            result = SourceFile.parse_file(logger, reader_format, url, reader_options)
        finally:
            if file_to_close:
                file_to_close.close()
        return result

    @staticmethod
    def parse_file(logger, reader_format: str, url, reader_options: dict) -> List:
        result = []
        if reader_format == "csv":
            # pandas.read_csv additional arguments can be passed to customize how to parse csv.
            # see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
            result.append(pd.read_csv(url, **reader_options))
        elif reader_format == "flat_json":
            # We can add option to call to pd.normalize_json to normalize semi-structured JSON data into a flat table
            # by asking user to specify how to flatten the nested columns
            result.append(pd.read_json(url, **reader_options))
        elif reader_format == "html":
            result += pd.read_html(url, **reader_options)
        elif reader_format == "excel":
            result.append(pd.read_excel(url, **reader_options))
        elif reader_format == "feather":
            result.append(pd.read_feather(url, **reader_options))
        elif reader_format == "parquet":
            result.append(pd.read_parquet(url, **reader_options))
        elif reader_format == "orc":
            result.append(pd.read_orc(url, **reader_options))
        elif reader_format == "pickle":
            result.append(pd.read_pickle(url, **reader_options))
        else:
            reason = f"Reader {reader_format} is not supported\n{traceback.format_exc()}"
            logger.error(reason)
            raise Exception(reason)
        return result

    @staticmethod
    def get_storage_scheme(logger, storage_name, url) -> str:
        """Convert Storage Names to the proper URL Prefix

        :param logger: Logger for printing messages
        :param storage_name: Name of the Storage Provider
        :param url: URL of the file in case Storage is not provided but included in the URL
        :return: the corresponding URL prefix / scheme
        """
        storage_name = storage_name.upper()
        parse_result = urlparse(url)
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
        logger.error(f"Unknown Storage provider in: {storage_name} {url}")
        return ""

    @staticmethod
    def get_simple_url(url) -> str:
        """Convert URL to remove the URL prefix (scheme)

        :param url: URL of the file
        :return: the corresponding URL without URL prefix / scheme
        """
        parse_result = urlparse(url)
        if parse_result.scheme:
            return url.split("://")[-1]
        else:
            return url

    @staticmethod
    def convert_dtype(dtype) -> str:
        """Convert Pandas Dataframe types to Airbyte Types.

        :param dtype: Pandas Dataframe type
        :return: Corresponding Airbyte Type
        """
        if dtype == object:
            return "string"
        elif dtype in ("int64", "float64"):
            return "number"
        elif dtype == "bool":
            return "bool"
        return "string"

    @staticmethod
    def parse_catalog(catalog: ConfiguredAirbyteCatalog) -> set:
        columns = set()
        for configured_stream in catalog.streams:
            stream = configured_stream.stream
            for key in stream.json_schema["properties"].keys():
                columns.add(key)
        return columns
