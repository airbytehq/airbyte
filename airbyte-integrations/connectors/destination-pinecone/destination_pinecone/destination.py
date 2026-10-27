#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dataclasses
import io
import logging
import time
import traceback
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
    AirbyteErrorTraceMessage,
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteStateMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    FailureType,
    Level,
    Status,
    TraceType,
    Type,
)
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from destination_pinecone.config import ConfigModel
from destination_pinecone.indexer import PineconeIndexer


logger = logging.getLogger("airbyte")

BATCH_SIZE = 32
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


class DestinationPinecone(Destination):
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
        try:
            self.embedder = create_from_config(config.embedding, config.processing)
            self.indexer = PineconeIndexer(config.indexing, self.embedder.embedding_dimensions)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

    def _log(self, level, message: str) -> AirbyteMessage:
        from airbyte_cdk.models import AirbyteLogMessage

        return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=level, message=message))

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        yield self._log(Level.INFO, "Starting Pinecone destination write...")
        try:
            yield self._log(Level.INFO, "Parsing configuration...")
            config_model = ConfigModel.parse_obj(config)

            yield self._log(Level.INFO, "Initializing embedder and indexer...")
            init_status = self._init_indexer(config_model)
            if init_status and init_status.status == Status.FAILED:
                yield self._log(Level.ERROR, f"Initialization failed: {init_status.message}")
                return

            yield self._log(Level.INFO, "Creating writer and starting sync...")
            writer = Writer(
                config_model.processing, self.indexer, self.embedder, batch_size=BATCH_SIZE, omit_raw_text=config_model.omit_raw_text
            )
            yield from writer.write(configured_catalog, input_messages)
            yield self._log(Level.INFO, "Write operation completed.")
        except Exception as e:
            yield AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.ERROR,
                    emitted_at=time.time() * 1000,
                    error=AirbyteErrorTraceMessage(
                        message=f"Pinecone destination write failed: {e}",
                        internal_message=traceback.format_exc(),
                        failure_type=FailureType.system_error,
                    ),
                ),
            )

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        logger.info("Starting Pinecone destination check...")
        try:
            logger.info("Parsing configuration...")
            parsed_config = ConfigModel.parse_obj(config)

            logger.info("Initializing embedder and indexer...")
            init_status = self._init_indexer(parsed_config)
            if init_status and init_status.status == Status.FAILED:
                logger.error(f"Initialization failed with message: {init_status.message}")
                return init_status

            logger.info("Running embedder check...")
            embedder_check_result = self.embedder.check()

            logger.info("Running indexer check...")
            indexer_check_result = self.indexer.check()

            logger.info("Running document processor config check...")
            processor_check_result = DocumentProcessor.check_config(parsed_config.processing)

            checks = [embedder_check_result, indexer_check_result, processor_check_result]
            errors = [error for error in checks if error is not None]
            if len(errors) > 0:
                error_message = "\n".join(errors)
                logger.error(f"Configuration check failed: {error_message}")
                return AirbyteConnectionStatus(status=Status.FAILED, message=error_message)
            else:
                logger.info("Configuration check succeeded.")
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.error(f"Exception during configuration check: {str(e)}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/destinations/pinecone",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
