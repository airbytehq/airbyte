#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dataclasses
import io
import logging
from typing import Any, Iterable, List, Mapping

import orjson

from airbyte_cdk.destinations import Destination
from airbyte_cdk.destinations.vector_db_based.document_processor import DocumentProcessor
from airbyte_cdk.destinations.vector_db_based.embedder import Embedder, create_from_config
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.writer import Writer
from airbyte_cdk.exception_handler import init_uncaught_exception_handler
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    DestinationSyncMode,
    Status,
    Type,
)
from destination_milvus.config import ConfigModel
from destination_milvus.indexer import MilvusIndexer


logger = logging.getLogger("airbyte")

BATCH_SIZE = 128
_STATE_ADDITIONAL_PROPERTIES_ATTR = "_airbyte_additional_properties"
_AIRBYTE_STATE_MESSAGE_WIRE_KEYS = {
    "global" if field.name == "global_" else field.name for field in dataclasses.fields(AirbyteStateMessage)
}


def serialize_airbyte_message(message: AirbyteMessage) -> dict[str, Any]:
    """Work around airbytehq/airbyte-python-cdk#1134 until the CDK preserves state extras."""
    serialized_message = AirbyteMessageSerializer.dump(message)
    if message.type == Type.STATE and message.state is not None:
        additional_properties = getattr(message.state, _STATE_ADDITIONAL_PROPERTIES_ATTR, {})
        if additional_properties:
            state = serialized_message.setdefault("state", {})
            for key, value in additional_properties.items():
                state.setdefault(key, value)
    return serialized_message


class DestinationMilvus(Destination):
    indexer: Indexer
    embedder: Embedder

    def _parse_input_stream(self, input_stream: io.TextIOWrapper) -> Iterable[AirbyteMessage]:
        """Preserve state extras until airbytehq/airbyte-python-cdk#1134 is fixed upstream."""
        for line in input_stream:
            try:
                raw = orjson.loads(line)
            except orjson.JSONDecodeError:
                logger.info(f"ignoring input which can't be deserialized as Airbyte Message: {line}")
                continue

            message = AirbyteMessageSerializer.load(raw)
            if message.type == Type.STATE and isinstance(raw.get("state"), dict) and message.state is not None:
                additional_properties = {key: value for key, value in raw["state"].items() if key not in _AIRBYTE_STATE_MESSAGE_WIRE_KEYS}
                if additional_properties:
                    setattr(message.state, _STATE_ADDITIONAL_PROPERTIES_ATTR, additional_properties)
            yield message

    def run(self, args: List[str]) -> None:
        init_uncaught_exception_handler(logger)
        parsed_args = self.parse_args(args)
        output_messages = self.run_cmd(parsed_args)
        for message in output_messages:
            print(orjson.dumps(serialize_airbyte_message(message)).decode())

    def _init_indexer(self, config: ConfigModel):
        self.embedder = create_from_config(config.embedding, config.processing)
        self.indexer = MilvusIndexer(config.indexing, self.embedder.embedding_dimensions)

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        config_model = ConfigModel.parse_obj(config)
        self._init_indexer(config_model)
        writer = Writer(
            config_model.processing, self.indexer, self.embedder, batch_size=BATCH_SIZE, omit_raw_text=config_model.omit_raw_text
        )
        yield from writer.write(configured_catalog, input_messages)

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        parsed_config = ConfigModel.parse_obj(config)
        self._init_indexer(parsed_config)
        checks = [self.embedder.check(), self.indexer.check(), DocumentProcessor.check_config(parsed_config.processing)]
        errors = [error for error in checks if error is not None]
        if len(errors) > 0:
            return AirbyteConnectionStatus(status=Status.FAILED, message="\n".join(errors))
        else:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/destinations/milvus",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
