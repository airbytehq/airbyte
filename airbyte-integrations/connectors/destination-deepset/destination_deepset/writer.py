# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from airbyte_cdk.models import AirbyteMessage
from destination_deepset.api import APIError, DeepsetCloudApi
from destination_deepset.models import DeepsetCloudFile


class DeepsetCloudFileWriter:
    def __init__(self, api_client: DeepsetCloudApi) -> None:
        self.client = api_client

    def write(self, message: AirbyteMessage) -> AirbyteMessage:
        """Write a record to deepset cloud workspace.

        Args:
            message (AirbyteMessage): The Airbyte message to write

        Returns:
            AirbyteMessage: Returns an Airbyte message with a suitable status.
        """
        try:
            file_id = self.client.upload_file(DeepsetCloudFile.from_message(message))
        except APIError:
            # @todo[abraham]: return a message signifying the failure
            raise
        else:
            # @todo[abraham]: return a message signifying success with the file id as additional context
            pass

        return message
