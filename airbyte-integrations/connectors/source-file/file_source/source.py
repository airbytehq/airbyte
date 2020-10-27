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

from datetime import datetime
from typing import Generator

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
from smart_open import smart_open


class FileSource(Source):
    """This source aims to provide support for readers of different file formats stored in various locations.

    It is optionally using s3fs, gcfs or smart_open libraries to handle efficient streaming of very large files
    (either compressed or not).

    Supported examples of URL this can accept are as follows:
    ```
        s3://my_bucket/my_key
        s3://my_key:my_secret@my_bucket/my_key
        s3://my_key:my_secret@my_server:my_port@my_bucket/my_key
        gs://my_bucket/my_blob
        azure://my_bucket/my_blob
        hdfs:///path/file
        hdfs://path/file
        webhdfs://host:port/path/file
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

    This reading supports primarily `read_csv` primitive but will be extended to readers of different formats for more
    potential sources as described below:
    https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html
    - read_json
    - read_html
    - read_excel
    - read_feather
    - read_parquet
    - read_orc
    - read_pickle

    All the options of the pandas readers are exposed to the configuration file of this connector so it is possible to
    override header names, types, encoding

    Note that this implementation is handling `data_url` target as a single file at the moment.
    We will expand the capabilities to load either glob of multiple files, content of directories, etc in a latter
    iteration.

    read more:
    https://gitlab.com/meltano/tap-csv
    https://github.com/robertjmoore/tap-csv
    https://gitlab.com/tjb-bnb/tap-csv
    https://github.com/fishtown-analytics/tap-s3-csv
    https://github.com/datamill-co/tap-files
    """

    def check(self, logger, config_container) -> AirbyteConnectionStatus:
        """Check involves verifying that the specified file is reachable with
        our credentials.

        :param logger:
        :param config_container:
        :return:
        """
        config = config_container.rendered_config
        data_url = config["data_url"]
        logger.info(f"Checking access to {data_url}...")
        try:
            self.load_dataframe(config, skip_data=True)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            reason = f"Failed to load {data_url}: {repr(err)}"
            logger.error(reason)
            return AirbyteConnectionStatus(status=Status.FAILED, message=reason)

    def discover(self, logger, config_container) -> AirbyteCatalog:
        """

        :param logger:
        :param config_container:
        :return:
        """
        config = config_container.rendered_config
        data_url = config["data_url"]
        logger.info(f"Discovering schema of {data_url}...")
        streams = []
        try:
            # TODO handle discovery of directories of files?
            # Don't skip data when discovering in order to infer column types
            df = self.load_dataframe(config, skip_data=False)
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {field: {"type": self.convert_dtype(df[field].dtype)} for field in df.columns},
            }
            streams.append(AirbyteStream(name=data_url, json_schema=json_schema))
        except Exception as err:
            reason = f"Failed to discover schemas of {data_url}: {repr(err)}"
            logger.error(reason)
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
        data_url = config["data_url"]
        logger.info(f"Reading ({data_url}, {catalog_path}, {state_path})...")
        try:
            df = self.load_dataframe(config)
            # TODO get subset of columns from catalog
            for data in df.to_dict(orient="records"):
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=data_url, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                )
        except Exception as err:
            reason = f"Failed to discover schemas of {data_url}: {repr(err)}"
            logger.error(reason)
            raise err

    @staticmethod
    def load_dataframe(config, skip_data=False) -> pd.DataFrame:
        """From a Airbyte Configuration file, load and return the pandas
        dataframe.

        :param skip_data:
        :param config:
        :return:
        """
        data_url = config["data_url"]

        reader = "read_csv"
        if "reader" in config:
            reader = config["reader"]

        reader_arg = {}
        if "reader_arguments" in config:
            reader_arg = config["reader_arguments"]
        if skip_data:
            reader_arg["nrows"] = 0
            reader_arg["index_col"] = 0

        gcs_file = None
        if "use_smart_open" in config and config["use_smart_open"]:
            if "gcs_service_account.json" in config and (data_url.startswith("gcs://") or data_url.startswith("gs://")):
                client = Client.from_service_account_json(config["gcs_service_account.json"])
                data_url = smart_open(data_url, transport_params=dict(client=client))
            else:
                data_url = smart_open(data_url)
        else:
            if "gcs_service_account.json" in config and (data_url.startswith("gcs://") or data_url.startswith("gs://")):
                fs = gcsfs.GCSFileSystem(token=config["gcs_service_account.json"])
                gcs_file = fs.open(data_url)
                data_url = gcs_file

        try:
            if reader == "read_csv":
                # pandas.read_csv additional arguments can be passed to customize how to parse csv.
                # see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
                return pd.read_csv(data_url, **reader_arg)
            else:
                raise Exception(f"Reader {reader} is not supported")
        finally:
            if gcs_file:
                gcs_file.close()

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
