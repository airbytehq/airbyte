# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import logging
from io import IOBase
from typing import Iterable, List, Optional, Union

import pytz
from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from azure.core.credentials import AccessToken
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContainerClient
from smart_open import open

from .spec import SourceAzureBlobStorageSpec


class AzureOauth2Authenticator(Oauth2Authenticator):
    """
    Authenticator for Azure Blob Storage SDK to align with azure.core.credentials.TokenCredential protocol
    """

    def get_token(self, *args, **kwargs) -> AccessToken:
        """Parent class handles Oauth Refresh token logic.
        `expires_on` is ignored and set to year 2222 to align with protocol.
        """
        return AccessToken(token=self.get_access_token(), expires_on=7952342400)


class SourceAzureBlobStorageStreamReader(AbstractFileBasedStreamReader):
    _credentials = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = None

    @property
    def config(self) -> SourceAzureBlobStorageSpec:
        return self._config

    @config.setter
    def config(self, value: SourceAzureBlobStorageSpec) -> None:
        self._config = value

    @property
    def account_url(self) -> str:
        if not self.config.azure_blob_storage_endpoint:
            return f"https://{self.config.azure_blob_storage_account_name}.blob.core.windows.net"
        return self.config.azure_blob_storage_endpoint

    @property
    def azure_container_client(self):
        return ContainerClient(
            self.account_url, container_name=self.config.azure_blob_storage_container_name, credential=self.azure_credentials
        )

    @property
    def azure_blob_service_client(self):
        return BlobServiceClient(self.account_url, credential=self._credentials)

    @property
    def azure_credentials(self) -> Union[str, AzureOauth2Authenticator]:
        if not self._credentials:
            if self.config.credentials.auth_type == "storage_account_key":
                self._credentials = self.config.credentials.azure_blob_storage_account_key
            else:
                self._credentials = AzureOauth2Authenticator(
                    token_refresh_endpoint=f"https://login.microsoftonline.com/{self.config.credentials.tenant_id}/oauth2/v2.0/token",
                    client_id=self.config.credentials.client_id,
                    client_secret=self.config.credentials.client_secret,
                    refresh_token=self.config.credentials.refresh_token,
                )
        return self._credentials

    def get_matching_files(
        self,
        globs: List[str],
        prefix: Optional[str],
        logger: logging.Logger,
    ) -> Iterable[RemoteFile]:
        prefixes = [prefix] if prefix else self.get_prefixes_from_globs(globs)
        prefixes = prefixes or [None]
        try:
            for prefix in prefixes:
                for blob in self.azure_container_client.list_blobs(name_starts_with=prefix):
                    remote_file = RemoteFile(uri=blob.name, last_modified=blob.last_modified.astimezone(pytz.utc).replace(tzinfo=None))
                    yield from self.filter_files_by_globs_and_start_date([remote_file], globs)
        except ResourceNotFoundError as e:
            raise AirbyteTracedException(failure_type=FailureType.config_error, internal_message=e.message, message=e.reason or e.message)

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
        return result
