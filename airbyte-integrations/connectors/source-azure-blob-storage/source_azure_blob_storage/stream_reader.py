# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
from contextlib import contextmanager
from io import IOBase
from typing import Iterable, List, Optional

import pytz
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from azure.storage.blob import BlobServiceClient, ContainerClient
from smart_open import open

from .config import Config


class SourceAzureBlobStorageStreamReader(AbstractFileBasedStreamReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = None

    @property
    def config(self) -> Config:
        return self._config

    @config.setter
    def config(self, value: Config) -> None:
        self._config = value

    @property
    def account_url(self) -> str:
        if not self.config.azure_blob_storage_endpoint:
            return f"https://{self.config.azure_blob_storage_account_name}.blob.core.windows.net"
        return self.config.azure_blob_storage_endpoint

    @property
    def azure_container_client(self):
        return ContainerClient(
            self.account_url,
            container_name=self.config.azure_blob_storage_container_name,
            credential=self.config.azure_blob_storage_account_key,
        )

    @property
    def azure_blob_service_client(self):
        return BlobServiceClient(self.account_url, credential=self.config.azure_blob_storage_account_key)

    def get_matching_files(
        self,
        globs: List[str],
        prefix: Optional[str],
        logger: logging.Logger,
    ) -> Iterable[RemoteFile]:
        prefixes = [prefix] if prefix else self.get_prefixes_from_globs(globs)
        prefixes = prefixes or [None]
        for prefix in prefixes:
            for blob in self.azure_container_client.list_blobs(name_starts_with=prefix):
                remote_file = RemoteFile(uri=blob.name, last_modified=blob.last_modified.astimezone(pytz.utc).replace(tzinfo=None))
                if not globs or self.file_matches_globs(remote_file, globs):
                    yield remote_file

    @contextmanager
    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        try:
            result = open(
                f"azure://{self.config.azure_blob_storage_container_name}/{file.uri}",
                transport_params={"client": self.azure_blob_service_client},
                mode=mode.value,
                encoding=encoding,
            )
        except OSError:
            logger.warning(
                f"We don't have access to {file.uri}. The file appears to have become unreachable during sync."
                f"Check whether key {file.uri} exists in `{self.config.azure_blob_storage_container_name}` container and/or has proper ACL permissions"
            )
        # see https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager for why we do this
        try:
            yield result
        finally:
            result.close()
