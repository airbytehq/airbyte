#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import logging
import traceback
from datetime import datetime
from typing import Any, Iterable, Iterator, Mapping, MutableMapping
from urllib.parse import urlparse

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import Source

from .client import Client, ConfigurationError
from .utils import dropbox_force_download


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

    client_class = Client

    def _get_client(self, config: Mapping):
        """Construct client"""
        client = self.client_class(**config)

        return client

    def _validate_and_transform(self, config: Mapping[str, Any]):
        if "reader_options" in config:
            try:
                config["reader_options"] = json.loads(config["reader_options"])
            except ValueError:
                raise ConfigurationError("reader_options is not valid JSON")
        else:
            config["reader_options"] = {}
        config["url"] = dropbox_force_download(config["url"])

        parse_result = urlparse(config["url"])
        if parse_result.netloc == "docs.google.com" and parse_result.path.lower().startswith("/spreadsheets/"):
            raise ConfigurationError(f'Failed to load {config["url"]}: please use the Official Google Sheets Source connector')
        return config

    def check(self, logger, config: Mapping) -> AirbyteConnectionStatus:
        """
        Check involves verifying that the specified file is reachable with
        our credentials.
        """
        try:
            config = self._validate_and_transform(config)
        except ConfigurationError as e:
            logger.error(str(e))
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

        client = self._get_client(config)
        source_url = client.reader.full_url
        try:
            with client.reader.open():
                list(client.streams)
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except (TypeError, ValueError, ConfigurationError) as err:
            reason = (
                f"Failed to load {source_url}\n Please check File Format and Reader Options are set correctly"
                f"\n{repr(err)}\n{traceback.format_exc()}"
            )
            logger.error(reason)
            return AirbyteConnectionStatus(status=Status.FAILED, message=reason)
        except Exception as err:
            reason = f"Failed to load {source_url}: {repr(err)}\n{traceback.format_exc()}"
            logger.error(reason)
            return AirbyteConnectionStatus(status=Status.FAILED, message=reason)

    def discover(self, logger: AirbyteLogger, config: Mapping) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams and fields in this integration. For example, given valid credentials to a
        Remote CSV File, returns an Airbyte catalog where each csv file is a stream, and each column is a field.
        """
        config = self._validate_and_transform(config)
        client = self._get_client(config)
        name = client.stream_name

        logger.info(f"Discovering schema of {name} at {client.reader.full_url}...")
        try:
            streams = list(client.streams)
        except Exception as err:
            reason = f"Failed to discover schemas of {name} at {client.reader.full_url}: {repr(err)}\n{traceback.format_exc()}"
            logger.error(reason)
            raise err
        return AirbyteCatalog(streams=streams)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] = None,
    ) -> Iterator[AirbyteMessage]:
        """Returns a generator of the AirbyteMessages generated by reading the source with the given configuration, catalog, and state."""
        config = self._validate_and_transform(config)
        client = self._get_client(config)
        fields = self.selected_fields(catalog, config)
        name = client.stream_name

        logger.info(f"Reading {name} ({client.reader.full_url})...")
        try:
            for row in client.read(fields=fields):
                record = AirbyteRecordMessage(stream=name, data=row, emitted_at=int(datetime.now().timestamp()) * 1000)
                yield AirbyteMessage(type=Type.RECORD, record=record)
        except Exception as err:
            reason = f"Failed to read data of {name} at {client.reader.full_url}: {repr(err)}\n{traceback.format_exc()}"
            logger.error(reason)
            raise err

    @staticmethod
    def selected_fields(catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any]) -> Iterable:
        for configured_stream in catalog.streams:
            fields = configured_stream.stream.json_schema["properties"].keys()
            if config["reader_options"].get("header", {}) is None:
                fields = [int(str_col_idx) for str_col_idx in fields]

            yield from fields
