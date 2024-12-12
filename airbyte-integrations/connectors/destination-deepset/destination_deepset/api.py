# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from uuid import UUID

import httpx
from httpx import HTTPError, HTTPStatusError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from destination_deepset.models import SUPPORTED_FILE_EXTENSIONS, DeepsetCloudConfig, DeepsetCloudFile, WriteMode


class APIError(RuntimeError):
    pass


class ConfigurationError(ValueError, APIError):
    """Raised when the configuration is missing or incorrect."""

    def __str__(self) -> str:
        return "Configuration is missing, cannot create an HTTP client."


class FileTypeError(APIError):
    """Raised when the file's extension does not match one of the supported file types."""

    def __str__(self) -> str:
        return f"File type not supported. Supported file extensions: {SUPPORTED_FILE_EXTENSIONS}"


class FileUploadError(APIError):
    """Raised when the server is unable to successfully upload the file."""

    def __str__(self) -> str:
        return "File upload failed."


class DeepsetCloudApi:
    def __init__(self, config: DeepsetCloudConfig) -> None:
        self.config = config
        self._client: httpx.Client | None = None

        # retry settings in seconds
        self.max = 60
        self.multiplier = 0.5

    @property
    def client(self) -> httpx.Client:
        if not self.config:
            raise ConfigurationError

        if self._client is None:
            self._client = httpx.Client(
                base_url=self.config.base_url,
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.config.api_key}",
                    "X-Client-Source": "deepset-cloud-airbyte",
                },
                follow_redirects=True,
            )

        return self._client

    def health_check(self) -> bool:
        """Check the health of deepset cloud API

        Returns:
            bool: Returns `True` if the health check was successful, `False` otherwise
        """
        try:
            with retry(
                retry=retry_if_exception_type(HTTPError),
                stop=stop_after_attempt(self.config.retries),
                wait=wait_random_exponential(multiplier=self.multiplier, max=self.max),
                reraise=True,
            ):
                response = self.client.get("/health")
                response.raise_for_status()
        except Exception:
            return False
        else:
            return True

    def upload(self, file: DeepsetCloudFile, write_mode: WriteMode = WriteMode.KEEP) -> UUID:
        """Upload file to deepset Cloud.

        Args:
            file (DeepsetCloudFile): The file to upload

        Raises:
            APIError: Raised whenever the file upload fails

        Returns:
            UUID: The unique identifier of the uploaded file
        """
        if file.extension not in SUPPORTED_FILE_EXTENSIONS:
            raise FileTypeError

        try:
            with retry(
                retry=retry_if_exception_type(HTTPError),
                stop=stop_after_attempt(self.config.retries),
                wait=wait_random_exponential(multiplier=self.multiplier, max=self.max),
                reraise=True,
            ):
                response = self.client.post(
                    f"/api/v1/workspaces/{self.config.workspace}/files",
                    files={"file": (file.name, file.content)},
                    data={"meta": file.meta_as_string},
                    params={"write_mode": write_mode},
                )
                response.raise_for_status()

            if file_id := response.json().get("file_id"):
                return UUID(file_id)

        except HTTPStatusError as ex:
            status_code, response_text = ex.response.status_code, ex.response.text
            message = f"File upload failed: {status_code = }, {response_text = }."
            raise FileUploadError(message) from ex
        except Exception as ex:
            raise FileUploadError from ex

        raise FileUploadError
