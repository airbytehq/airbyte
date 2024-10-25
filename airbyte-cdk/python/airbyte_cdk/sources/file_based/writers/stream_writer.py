#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Mapping, Union

from airbyte_cdk.sources.file_based.config.clients_config.base_sync_config import BaseSyncConfig
from airbyte_cdk.sources.file_based.writers.file_based_stream_writer import AbstractFileBasedStreamWriter
from airbyte_cdk.sources.file_based.writers.local_file_client import LocalFileTransferClient


class FileTransferStreamWriter(AbstractFileBasedStreamWriter):
    def __init__(self, client_cls=LocalFileTransferClient):
        super().__init__()
        self._client_cls = client_cls
        self._config = {}

    @property
    def config(self) -> Union[BaseSyncConfig, Mapping[str, Any]]:
        return self._config

    @config.setter
    def config(self, value: Union[BaseSyncConfig, Mapping[str, Any]]):
        self._config = value

    @property
    def client(self):
        if self._client is None:
            self._client = self._client_cls(self.config)
        return self._client

    def write(self, file_uri: str, fp, file_size: int, logger: logging.Logger):
        yield self.client.write(file_uri, fp, file_size, logger)
