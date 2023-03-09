#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Any, Mapping, Union

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


class ConnectorBuilderHandler:
    def __init__(self, source: ManifestDeclarativeSource):
        self.source = source

    def list_streams(self) -> AirbyteRecordMessage:
        raise NotImplementedError

    def stream_read(self, command_config) -> AirbyteRecordMessage:
        raise NotImplementedError

    @staticmethod
    def _emitted_at():
        return int(datetime.now().timestamp()) * 1000

    def resolve_manifest(self) -> Union[AirbyteMessage, AirbyteRecordMessage]:
        try:
            return AirbyteRecordMessage(
                data={"manifest": self.source.resolved_manifest},
                emitted_at=self._emitted_at(),
                stream="",
            )
        except Exception as exc:
            error = AirbyteTracedException.from_exception(exc, message="Error resolving manifest.")
            return error.as_airbyte_message()

    def handle_request(self, config: Mapping[str, Any]) -> Union[AirbyteMessage, AirbyteRecordMessage]:
        command = config.get("__command")
        if command == "resolve_manifest":
            return self.resolve_manifest()
        raise ValueError(f"Unrecognized command {command}.")
