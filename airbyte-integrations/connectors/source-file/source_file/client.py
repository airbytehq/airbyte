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
from typing import Iterable, List
from urllib.parse import urlparse

import numpy as np
import panda as pd
from airbyte_protocol import AirbyteStream
from base_python.entrypoint import logger

from botocore import UNSIGNED
from botocore.config import Config
from genson import SchemaBuilder
from google.cloud.storage import Client as GCSClient
from s3fs import S3FileSystem
import smart_open


class Client:
    def __init__(self, dataset_name: str, url: str, provider: dict, format: str = None, reader_options: str = None):
        self._dataset_name = dataset_name
        self._url = url
        self._provider = provider
        self._format = format
        self._reader_options = {}
        if reader_options:
            try:
                self._reader_options = json.loads(reader_options)
            except json.decoder.JSONDecodeError as err:
                logger.error(f"Failed to parse reader options {repr(err)}\n{reader_options}\n{traceback.format_exc()}")

    @property
    # FIXME:
    def stream_name(self) -> str:
        if self._dataset_name:
            return self._dataset_name
        else:
            reader_format = "csv"
            if self._format:
                reader_format = self._format
            name = f"file_{self._provider['storage']}.{reader_format}"
        return name

    def open_file_url(self):
        storage = self.storage_scheme
        url = self.url

        file_to_close = None
        if storage == "gs://":
            result, file_to_close = self.open_gcs_url(storage, url)
        elif storage == "s3://":
            result = self.open_aws_url(storage, url)
        elif storage == "webhdfs://":
            host = self._provider["host"]
            port = self._provider["port"]
            result = smart_open.open(f"webhdfs://{host}:{port}/{url}")
        elif storage == "ssh://" or storage == "scp://" or storage == "sftp://":
            user = self._provider["user"]
            host = self._provider["host"]
            if "password" in self._provider:
                password = self._provider["password"]
                # Explicitly turn off ssh keys stored in ~/.ssh
                transport_params = {"connect_kwargs": {"look_for_keys": False}}
                result = smart_open.open(f"{storage}{user}:{password}@{host}/{url}", transport_params=transport_params)
            else:
                result = smart_open.open(f"{storage}{user}@{host}/{url}")
            file_to_close = result
        else:
            result =smart_open.open(f"{storage}{url}")
        return result, file_to_close

    def open_gcs_url(self, storage, url):
        use_gcs_service_account = "service_account_json" in self._provider and storage == "gs://"
        file_to_close = None
        if self.reader_impl == "gcsfs":
            if use_gcs_service_account:
                try:
                    token_dict = json.loads(self._provider["service_account_json"])
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
                    credentials = json.dumps(json.loads(self._provider["service_account_json"]))
                    tmp_service_account = tempfile.NamedTemporaryFile(delete=False)
                    with smart_open.open(tmp_service_account, "w") as f:
                        f.write(credentials)
                    tmp_service_account.close()
                    client = GCSClient.from_service_account_json(tmp_service_account.name)
                    result = smart_open.open(f"gs://{url}", transport_params=dict(client=client))
                    os.remove(tmp_service_account.name)
                except json.decoder.JSONDecodeError as err:
                    logger.error(f"Failed to parse gcs service account json: {repr(err)}\n{traceback.format_exc()}")
                    raise err
            else:
                client = GCSClient.create_anonymous_client()
                result = smart_open.open(f"{storage}{url}", transport_params=dict(client=client))
        return result, file_to_close

    def open_aws_url(self, storage, url):
        use_aws_account = "aws_access_key_id" in self._provider and "aws_secret_access_key" in self._provider and storage == "s3://"
        if self.reader_impl == "s3fs":
            if use_aws_account:
                aws_access_key_id = None
                if "aws_access_key_id" in self._provider:
                    aws_access_key_id = self._provider["aws_access_key_id"]
                aws_secret_access_key = None
                if "aws_secret_access_key" in self._provider:
                    aws_secret_access_key = self._provider["aws_secret_access_key"]
                s3 = S3FileSystem(anon=False, key=aws_access_key_id, secret=aws_secret_access_key)
                result = s3.open(f"s3://{url}", mode="r")
            else:
                s3 = S3FileSystem(anon=True)
                result = s3.open(f"s3://{url}", mode="r")
        else:
            if use_aws_account:
                aws_access_key_id = self._provider.get("aws_access_key_id", "")
                aws_secret_access_key = self._provider.get("aws_secret_access_key", "")
                result = smart_open.open(f"s3://{aws_access_key_id}:{aws_secret_access_key}@{url}")
            else:
                config = Config(signature_version=UNSIGNED)
                params = {
                    "resource_kwargs": {"config": config},
                }
                result = smart_open.open(f"{storage}{url}", transport_params=params)
        return result

    @property
    def reader_impl(self):
        return self._provider.get("reader_impl", "")

    def load_nested_json_schema(self) -> dict:
        url, file_to_close = self.open_file_url()
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

    def load_nested_json(self) -> list:
        url, file_to_close = self.open_file_url()
        try:
            result = json.load(url)
            if isinstance(result, dict):
                result = [result]
        finally:
            if file_to_close:
                file_to_close.close()
        return result

    def load_dataframes(self, skip_data=False) -> List:
        """From an Airbyte Configuration file, load and return the appropriate pandas dataframe.

        :param skip_data: limit reading data
        :return: a list of dataframe loaded from files described in the configuration
        """
        # default format reader
        reader_format = self._format or "csv"
        reader_options = {**self._reader_options}
        if skip_data and reader_format == "csv":
            reader_options["nrows"] = 0
            reader_options["index_col"] = 0
        url, file_to_close = self.open_file_url()
        try:
            result = self.parse_file(reader_format, url, reader_options)
        finally:
            if file_to_close:
                file_to_close.close()
        return result

    @staticmethod
    def parse_file(reader_format: str, url: str, reader_options: dict) -> List:
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

    @property
    def storage_scheme(self) -> str:
        """Convert Storage Names to the proper URL Prefix
        :return: the corresponding URL prefix / scheme
        """
        storage_name = self._provider["storage_name"].upper()
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
        logger.error(f"Unknown Storage provider in: {storage_name} {self._url}")
        return ""

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
            return "bool"
        return "string"

    def read(self, fields: Iterable = None) -> Iterable[dict]:
        if self._format == "json":
            yield from self.load_nested_json()
        else:
            for df in self.load_dataframes():
                columns = set(fields).intersection(set(df.columns)) if fields else df.columns
                df = df.replace(np.nan, "NaN", regex=True)
                yield from df[columns].to_dict(orient="records")

    @property
    def streams(self) -> Iterable:
        # TODO handle discovery of directories of multiple files instead
        if self._format == "json":
            schema = self.load_nested_json_schema()
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": schema,
            }
        else:
            # Don't skip data when discovering in order to infer column types
            df_list = self.load_dataframes(skip_data=False)
            fields = {}
            for df in df_list:
                for col in df.columns:
                    fields[col] = self.dtype_to_json_type(df[col].dtype)
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {field: {"type": fields[field]} for field in fields},
            }
        yield AirbyteStream(name=self.stream_name, json_schema=json_schema)
