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
from datetime import datetime
from typing import Generator, List

import gcsfs
import pandas as pd
from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    Source,
    Status,
    Type,
)
from google.cloud.storage import Client
from s3fs.core import S3FileSystem
from smart_open import open


class FileSource(Source):
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

    def check(self, logger, config_container) -> AirbyteConnectionStatus:
        """Check involves verifying that the specified file is reachable with
        our credentials.

        :param logger:
        :param config_container:
        :return:
        """
        config = config_container.rendered_config
        url = config["url"]
        logger.info(f"Checking access to {url}...")
        try:
            self.load_dataframes(config, skip_data=True)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            reason = f"Failed to load {url}: {repr(err)}"
            logger.error(reason)
            return AirbyteConnectionStatus(status=Status.FAILED, message=reason)

    def discover(self, logger, config_container) -> AirbyteCatalog:
        """

        :param logger:
        :param config_container:
        :return:
        """
        config = config_container.rendered_config
        url = config["url"]
        logger.info(f"Discovering schema of {url}...")
        streams = []
        try:
            # TODO handle discovery of directories of multiple files instead
            # Don't skip data when discovering in order to infer column types
            df_list = self.load_dataframes(config, skip_data=False)
            fields = {}
            for df in df_list:
                for col in df.columns:
                    fields[col] = self.convert_dtype(df[col].dtype)
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {field: {"type": fields[field]} for field in fields},
            }
            streams.append(AirbyteStream(name=url, json_schema=json_schema))
        except Exception as err:
            reason = f"Failed to discover schemas of {url}: {repr(err)}"
            logger.error(reason)
            raise err
        return AirbyteCatalog(streams=streams)

    def read(self, logger, config_container, catalog_path, state_path=None) -> Generator[AirbyteMessage, None, None]:
        """

        :param logger:
        :param config_container:
        :param catalog_path:
        :param state_path:
        :return:
        """
        config = config_container.rendered_config
        url = config["url"]
        logger.info(f"Reading ({url}, {catalog_path}, {state_path})...")
        try:
            df_list = self.load_dataframes(config)
            # TODO get subset of columns from catalog
            for df in df_list:
                for data in df.to_dict(orient="records"):
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(stream=url, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                    )
        except Exception as err:
            reason = f"Failed to discover schemas of {url}: {repr(err)}"
            logger.error(reason)
            raise err

    @staticmethod
    def load_dataframes(config, skip_data=False) -> List:
        """From an Airbyte Configuration file, load and return the appropriate pandas dataframe.

        :param skip_data: limit reading data
        :param config:
        :return: a list of dataframe loaded from files described in the configuration
        """
        storage = config["storage"]
        url = config["url"]

        gcs_file = None
        use_gcs_service_account = "service_account_json" in config and storage == "gs://"
        use_aws_account = "aws_secret_access_key_id" in config and "aws_secret_access_key" in config and storage == "s3://"

        # default format reader
        reader_format = "csv"
        if "format" in config:
            reader_format = config["format"]

        reader_options = {}
        if "reader_options" in config:
            reader_options = json.loads(config["reader_options"])
        if skip_data and reader_format == "csv":
            reader_options["nrows"] = 0
            reader_options["index_col"] = 0

        # default reader impl
        reader_impl = ""
        if "reader_impl" in config:
            reader_impl = config["reader_impl"]

        if reader_impl == "gcsfs":
            if use_gcs_service_account:
                token_dict = json.loads(config["service_account_json"])
                fs = gcsfs.GCSFileSystem(token=token_dict)
                gcs_file = fs.open(f"gs://{url}")
                url = gcs_file
        elif reader_impl == "s3fs":
            if use_aws_account:
                aws_secret_access_key_id = None
                if "aws_secret_access_key_id" in config:
                    aws_secret_access_key_id = config["aws_secret_access_key_id"]
                aws_secret_access_key = None
                if "aws_secret_access_key" in config:
                    aws_secret_access_key = config["aws_secret_access_key"]
                s3 = S3FileSystem(anon=False, key=aws_secret_access_key_id, secret=aws_secret_access_key)
                url = s3.open(f"s3://{url}", mode="rb")
        else:  # using smart_open
            if use_gcs_service_account:
                credentials = json.dumps(json.loads(config["service_account_json"]))
                tmp_service_account = tempfile.NamedTemporaryFile(delete=False)
                with open(tmp_service_account, "w") as f:
                    f.write(credentials)
                tmp_service_account.close()
                client = Client.from_service_account_json(tmp_service_account.name)
                url = open(f"gs://{url}", transport_params=dict(client=client))
                os.remove(tmp_service_account.name)
            elif use_aws_account:
                aws_secret_access_key_id = ""
                if "aws_secret_access_key_id" in config:
                    aws_secret_access_key_id = config["aws_secret_access_key_id"]
                aws_secret_access_key = ""
                if "aws_secret_access_key" in config:
                    aws_secret_access_key = config["aws_secret_access_key"]
                url = open(f"s3://{aws_secret_access_key_id}:{aws_secret_access_key}@{url}")
            elif storage == "webhdfs":
                host = config["host"]
                port = config["port"]
                url = open(f"webhdfs://{host}:{port}/{url}")
            elif storage == "ssh" or storage == "scp" or storage == "sftp":
                user = config["user"]
                host = config["host"]
                password = None
                if "password" in config:
                    password = config["password"]
                if password:
                    url = open(f"{storage}{user}:{password}@{host}/{url}")
                else:
                    url = open(f"{storage}{user}@{host}/{url}")
            else:
                url = open(f"{storage}{url}")
        try:
            result = FileSource.parse_file(reader_format, url, reader_options)
        finally:
            if gcs_file:
                gcs_file.close()
        return result

    @staticmethod
    def parse_file(reader_format: str, url, reader_options: dict) -> List:
        result = []
        if reader_format == "csv":
            # pandas.read_csv additional arguments can be passed to customize how to parse csv.
            # see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
            result.append(pd.read_csv(url, **reader_options))
        elif reader_format == "json":
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
            raise Exception(f"Reader {reader_format} is not supported")
        return result

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
