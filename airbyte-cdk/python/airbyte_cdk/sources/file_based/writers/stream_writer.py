#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

from airbyte_cdk.sources.file_based.writers.local_file_client import LocalFileTransferClient


class FileTransferStreamWriter:
    def __init__(self, client_cls=LocalFileTransferClient):
        self._client = None
        self._client_cls = client_cls

    @property
    def client(self):
        if self._client is None:
            self._client = self._client_cls()
        return self._client

    def write(self, file_uri: str, file_pointer, file_size: int, logger: logging.Logger):
        yield self.client.write(file_uri, file_pointer, file_size, logger)
