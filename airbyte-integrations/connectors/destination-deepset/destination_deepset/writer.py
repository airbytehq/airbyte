# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import Any, Mapping

from airbyte_cdk.models import AirbyteMessage, DestinationSyncMode
from destination_deepset import util
from destination_deepset.api import APIError, DeepsetCloudApi
from destination_deepset.models import DeepsetCloudConfig, DeepsetCloudFile


class WriterError:
    """Raised when an error is encountered by the writer"""


class DeepsetCloudFileWriter:
    def __init__(self, api_client: DeepsetCloudApi) -> None:
        self.client = api_client

    @classmethod
    def factory(cls, config: Mapping[str, Any]) -> DeepsetCloudFileWriter:
        """Create an instance of this writer using a mapping of config values.

        Args:
            config (Mapping[str, Any]): the configuration values as defined in `spec.json`.

        Returns:
            DeepsetCloudFileWriter: An instance of this class.
        """
        try:
            parsed_config = DeepsetCloudConfig.model_validate(config)
        except ValueError as ex:
            msg = "Failed to parse configuration into deepset cloud configuration."
            raise WriterError(msg) from ex
        else:
            return cls(api_client=DeepsetCloudApi(config=parsed_config))

    def write(
        self,
        file: DeepsetCloudFile,
        destination_sync_mode: DestinationSyncMode = DestinationSyncMode.append_dedup,
    ) -> AirbyteMessage:
        """Write a record to deepset cloud workspace.

        Args:
            message (AirbyteMessage): The Airbyte message to write
            destination_sync_mode (DestinationSyncMode, Optional): The destination sync mode. Defaults to
                `append_dedup`.

        Returns:
            AirbyteMessage: Returns an Airbyte message with a suitable status.
        """
        write_mode = util.get_file_write_mode(destination_sync_mode)
        try:
            file_id = self.client.upload(file, write_mode=write_mode)
        except APIError as ex:
            return util.get_trace_message(
                f"Failed to upload a record to deepset cloud workspace, workspace = {self.client.config.workspace}.",
                exception=ex,
            )
        else:
            return util.get_log_message(
                f"File uploaded, file_name = {file.name}, {file_id = }, workspace = {self.client.config.workspace}."
            )
