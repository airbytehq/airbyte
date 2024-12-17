# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import traceback
from time import time
from typing import TYPE_CHECKING, Any

from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteLogMessage, AirbyteMessage, AirbyteTraceMessage, Level, TraceType, Type
from destination_deepset.api import APIError, DeepsetCloudApi
from destination_deepset.models import DeepsetCloudConfig, DeepsetCloudFile
from pipelines.airbyte_ci.connectors.migrate_to_manifest_only.declarative_component_schema import FailureType

if TYPE_CHECKING:
    from collections.abc import Mapping


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
            parsed_config = DeepsetCloudConfig.parse_obj(config)
        except ValueError as ex:
            msg = "Failed to parse configuration into deepset cloud configuration."
            raise WriterError(msg) from ex
        else:
            return cls(api_client=DeepsetCloudApi(config=parsed_config))

    def write(self, file: DeepsetCloudFile) -> AirbyteMessage:
        """Write a record to deepset cloud workspace.

        Args:
            message (AirbyteMessage): The Airbyte message to write

        Returns:
            AirbyteMessage: Returns an Airbyte message with a suitable status.
        """
        try:
            file_id = self.client.upload(file)
        except APIError as ex:
            workspace = self.client.config.workspace
            return AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.ERROR,
                    emitted_at=time(),
                    error=AirbyteErrorTraceMessage(
                        message=f"Failed to upload a record to deepset cloud workspace, {workspace = }.",
                        internal_message=str(ex),
                        stack_trace=traceback.format_exc(),
                        failure_type=FailureType.transient_error.value,
                    ),
                ),
            )
        else:
            workspace = self.client.config.workspace
            return AirbyteMessage(
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message=f"File uploaded, file_name = {file.name}, {file_id = }, {workspace = }.",
                ),
            )
