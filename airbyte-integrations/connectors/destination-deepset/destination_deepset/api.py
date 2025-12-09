# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import logging
from uuid import UUID

import httpx
from httpx import HTTPError, HTTPStatusError
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from destination_deepset import util
from destination_deepset.models import DeepsetCloudConfig, DeepsetCloudFile


logger = logging.getLogger("airbyte")


class APIError(RuntimeError):
    """Raised when any error occurs while using the API."""


class ConfigurationError(ValueError, APIError):
    """Raised when the configuration is missing or incorrect."""


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
                base_url=self.config.base_url.removesuffix("/"),
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.config.api_key}",
                    "X-Client-Source": "airbyte-destination-deepset",
                },
                follow_redirects=True,
            )

        return self._client

    def retry(self) -> Retrying:
        """Retrial configurations

        Returns:
            Retrying: The instance
        """
        return Retrying(
            retry=retry_if_exception_type(HTTPError),
            stop=stop_after_attempt(self.config.retries),
            wait=wait_random_exponential(multiplier=self.multiplier, max=self.max),
            reraise=True,
        )

    def health_check(self) -> None:
        """Check the health of deepset cloud API

        Raises:
            APIError: Raised when an error is encountered.
        """
        logger.info(f"[DEEPSET] Health check: {self.config.base_url}/api/v1/me")
        try:
            for attempt in self.retry():
                with attempt:
                    response = self.client.get("/api/v1/me")
                    response.raise_for_status()

            workspaces = util.get(response.json(), "organization.workspaces", [])
            access = next((True for workspace in workspaces if workspace["name"] == self.config.workspace), False)
            logger.debug(f"[DEEPSET] Available workspaces: {[w['name'] for w in workspaces]}")
        except Exception as ex:
            logger.error(f"[DEEPSET] Health check failed: {ex}")
            raise APIError from ex
        else:
            if access:
                logger.info(f"[DEEPSET] Access confirmed for workspace: {self.config.workspace}")
                return

        error = "User does not have access to the selected workspace!"
        logger.error(f"[DEEPSET] {error}")
        raise ConfigurationError(error)

    def upload(self, file: DeepsetCloudFile, write_mode: str = "KEEP") -> UUID:
        """Upload file to deepset Cloud.

        Args:
            file (DeepsetCloudFile): The file to upload
            write_mode (str, Optional): The write mode. Defaults to `KEEP`.

        Raises:
            APIError: Raised whenever the file upload fails

        Returns:
            UUID: The unique identifier of the uploaded file
        """
        endpoint = f"/api/v1/workspaces/{self.config.workspace}/files"
        logger.debug(f"[DEEPSET] POST {endpoint} (write_mode={write_mode})")

        try:
            for attempt in self.retry():
                with attempt:
                    response = self.client.post(
                        endpoint,
                        files={"file": (file.name, file.content)},
                        data={"meta": file.meta_as_string},
                        params={"write_mode": write_mode},
                    )
                    response.raise_for_status()

            if file_id := response.json().get("file_id"):
                return UUID(file_id)

        except HTTPStatusError as ex:
            status_code, response_text = ex.response.status_code, ex.response.text
            logger.error(f"[DEEPSET] HTTP error: status_code={status_code}, response={response_text}")
            message = f"File upload failed: {status_code = }, {response_text = }."
            raise FileUploadError(message) from ex
        except Exception as ex:
            logger.error(f"[DEEPSET] Unexpected error during upload: {type(ex).__name__}: {ex}")
            raise FileUploadError from ex

        logger.error("[DEEPSET] No file_id in response")
        raise FileUploadError
