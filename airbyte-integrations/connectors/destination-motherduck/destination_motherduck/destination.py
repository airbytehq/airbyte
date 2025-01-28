# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import datetime
import io
import json
import logging
import os
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Dict, Iterable, List, Mapping, cast
from urllib.parse import urlparse

import orjson
from serpyco_rs import Serializer
from typing_extensions import override

from airbyte_cdk import AirbyteStream, ConfiguredAirbyteStream, SyncMode
from airbyte_cdk.destinations import Destination
from airbyte_cdk.exception_handler import init_uncaught_exception_handler
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStateStats,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.models.airbyte_protocol_serializers import custom_type_resolver
from airbyte_cdk.sql._util.name_normalizers import LowerCaseNormalizer
from airbyte_cdk.sql.constants import AB_EXTRACTED_AT_COLUMN, AB_INTERNAL_COLUMNS, AB_META_COLUMN, AB_RAW_ID_COLUMN
from airbyte_cdk.sql.secrets import SecretString
from airbyte_cdk.sql.shared.catalog_providers import CatalogProvider
from airbyte_cdk.sql.types import SQLTypeConverter
from destination_motherduck.processors.duckdb import DuckDBConfig, DuckDBSqlProcessor
from destination_motherduck.processors.motherduck import MotherDuckConfig, MotherDuckSqlProcessor


logger = getLogger("airbyte")

CONFIG_MOTHERDUCK_API_KEY = "motherduck_api_key"
CONFIG_DEFAULT_SCHEMA = "main"
MAX_STREAM_BATCH_SIZE = 50_000


@dataclass
class PatchedAirbyteStateMessage(AirbyteStateMessage):
    """Declare the `id` attribute that platform sends."""

    id: int | None = None
    """Injected by the platform."""


@dataclass
class PatchedAirbyteMessage(AirbyteMessage):
    """Keep all defaults but override the type used in `state`."""

    state: PatchedAirbyteStateMessage | None = None
    """Override class for the state message only."""


PatchedAirbyteMessageSerializer = Serializer(
    PatchedAirbyteMessage,
    omit_none=True,
    custom_type_resolver=custom_type_resolver,
)
"""Redeclared SerDes class using the patched dataclass."""


def validated_sql_name(sql_name: Any) -> str:
    """Return the input if it is a valid SQL name, otherwise raise an exception."""
    pattern = r"^[a-zA-Z0-9_]*$"
    result = str(sql_name)
    if bool(re.match(pattern, result)):
        return result

    raise ValueError(f"Invalid SQL name: {sql_name}")


class DestinationMotherDuck(Destination):
    type_converter_class = SQLTypeConverter
    normalizer = LowerCaseNormalizer

    @staticmethod
    def _is_motherduck(path: str | None) -> bool:
        return path is not None and "md:" in str(path)

    def _get_sql_processor(
        self,
        configured_catalog: ConfiguredAirbyteCatalog,
        schema_name: str,
        table_prefix: str = "",
        db_path: str = ":memory:",
        motherduck_token: str = "",
    ) -> DuckDBSqlProcessor | MotherDuckSqlProcessor:
        """
        Get sql processor for processing queries
        """
        catalog_provider = CatalogProvider(configured_catalog)
        if self._is_motherduck(db_path):
            return MotherDuckSqlProcessor(
                sql_config=MotherDuckConfig(
                    schema_name=schema_name,
                    table_prefix=table_prefix,
                    db_path=db_path,
                    database=urlparse(db_path).path,
                    api_key=SecretString(motherduck_token),
                ),
                catalog_provider=catalog_provider,
            )
        else:
            return DuckDBSqlProcessor(
                sql_config=DuckDBConfig(schema_name=schema_name, table_prefix=table_prefix, db_path=db_path),
                catalog_provider=catalog_provider,
            )

    @staticmethod
    def _get_destination_path(destination_path: str) -> str:
        """
        Get a normalized version of the destination path.
        Automatically append /local/ to the start of the path
        """
        if destination_path.startswith("md:") or destination_path.startswith("motherduck:"):
            return destination_path

        if not destination_path.startswith("/local"):
            destination_path = os.path.join("/local", destination_path)

        destination_path = os.path.normpath(destination_path)
        if not destination_path.startswith("/local"):
            raise ValueError(
                f"destination_path={destination_path} is not a valid path." "A valid path shall start with /local or no / prefix"
            )

        return destination_path

    def _quote_identifier(self, identifier: str) -> str:
        """Return the given identifier, quoted."""
        return f'"{identifier}"'

    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        """
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param input_messages: The stream of input messages received from the source
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the destination
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """
        streams = {s.stream.name for s in configured_catalog.streams}
        logger.info(f"Starting write to DuckDB with {len(streams)} streams")

        path = str(config.get("destination_path", "md:"))
        path = self._get_destination_path(path)
        schema_name = validated_sql_name(config.get("schema", CONFIG_DEFAULT_SCHEMA))
        motherduck_api_key = str(config.get(CONFIG_MOTHERDUCK_API_KEY, ""))
        processor = self._get_sql_processor(
            configured_catalog=configured_catalog,
            schema_name=schema_name,
            db_path=path,
            motherduck_token=motherduck_api_key,
        )

        for configured_stream in configured_catalog.streams:
            processor.prepare_stream_table(stream_name=configured_stream.stream.name, sync_mode=configured_stream.destination_sync_mode)

        buffer: dict[str, dict[str, list[Any]]] = defaultdict(lambda: defaultdict(list))
        records_buffered: dict[str, int] = defaultdict(int)
        records_processed: dict[str, int] = defaultdict(int)
        records_since_last_checkpoint: dict[str, int] = defaultdict(int)
        legacy_state_messages: list[AirbyteMessage] = []
        for message in input_messages:
            if message.type == Type.STATE and message.state is not None:
                if message.state.stream is None:
                    logger.warning("Cannot process legacy state message, skipping.")
                    # Hold until the end of the stream, and then yield them all at once.
                    legacy_state_messages.append(message)
                    continue
                stream_name = message.state.stream.stream_descriptor.name
                _ = message.state.stream.stream_descriptor.namespace  # Unused currently
                # flush the buffer
                self._flush_buffer(
                    buffer=buffer,
                    configured_catalog=configured_catalog,
                    db_path=path,
                    schema_name=schema_name,
                    motherduck_api_key=motherduck_api_key,
                    stream_name=stream_name,
                )
                buffer = defaultdict(lambda: defaultdict(list))
                records_buffered[stream_name] = 0

                # Annotate the state message with the number of records processed
                message.state.destinationStats = AirbyteStateStats(
                    recordCount=records_since_last_checkpoint[stream_name],
                )
                records_since_last_checkpoint[stream_name] = 0

                yield message
            elif message.type == Type.RECORD and message.record is not None:
                data = message.record.data
                stream_name = message.record.stream
                if stream_name not in streams:
                    logger.debug(f"Stream {stream_name} was not present in configured streams, skipping")
                    continue
                # add to buffer
                record_meta: dict[str, str] = {}
                for column_name in processor._get_sql_column_definitions(stream_name):
                    if column_name in data:
                        buffer[stream_name][column_name].append(data[column_name])
                    elif column_name not in AB_INTERNAL_COLUMNS:
                        buffer[stream_name][column_name].append(None)

                buffer[stream_name][AB_RAW_ID_COLUMN].append(str(uuid.uuid4()))
                buffer[stream_name][AB_EXTRACTED_AT_COLUMN].append(datetime.datetime.now().isoformat())
                buffer[stream_name][AB_META_COLUMN].append(json.dumps(record_meta))
                records_buffered[stream_name] += 1
                records_since_last_checkpoint[stream_name] += 1

                if records_buffered[stream_name] >= MAX_STREAM_BATCH_SIZE:
                    logger.info(
                        f"Loading {records_buffered[stream_name]:,} records from '{stream_name}' stream buffer...",
                    )
                    self._flush_buffer(
                        buffer=buffer,
                        configured_catalog=configured_catalog,
                        db_path=path,
                        schema_name=schema_name,
                        motherduck_api_key=motherduck_api_key,
                        stream_name=stream_name,
                    )
                    buffer = defaultdict(lambda: defaultdict(list))
                    records_processed[stream_name] += records_buffered[stream_name]
                    records_buffered[stream_name] = 0
                    logger.info(
                        f"Records loaded successfully. Total '{stream_name}' records processed: {records_processed[stream_name]:,}",
                    )

            else:
                logger.info(f"Message type {message.type} not supported, skipping")

        # flush any remaining messages
        self._flush_buffer(buffer, configured_catalog, path, schema_name, motherduck_api_key)
        if legacy_state_messages:
            # Save to emit these now, since we've finished processing the stream.
            yield from legacy_state_messages

    def _flush_buffer(
        self,
        buffer: Dict[str, Dict[str, List[Any]]],
        configured_catalog: ConfiguredAirbyteCatalog,
        db_path: str,
        schema_name: str,
        motherduck_api_key: str,
        stream_name: str | None = None,
    ) -> None:
        """
        Flush the buffer to the destination.

        If no stream name is provided, then all streams will be flushed.
        """
        for configured_stream in configured_catalog.streams:
            if (stream_name is None or stream_name == configured_stream.stream.name) and buffer.get(configured_stream.stream.name):
                processor = self._get_sql_processor(
                    configured_catalog=configured_catalog, schema_name=schema_name, db_path=db_path, motherduck_token=motherduck_api_key
                )
                processor.write_stream_data_from_buffer(buffer, configured_stream.stream.name, configured_stream.destination_sync_mode)

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            path = config.get("destination_path", "")
            path = self._get_destination_path(path)

            if path.startswith("/local"):
                logger.info(f"Using DuckDB file at {path}")
                os.makedirs(os.path.dirname(path), exist_ok=True)

            if self._is_motherduck(path):
                # We want to specify 'saas_mode' for during check,
                # to reduce memory usage from unnecessary extensions
                if "?" in path:
                    # There are already some query params; append to them.
                    path += "&saas_mode=true"
                else:
                    # No query params yet; add one.
                    path += "?saas_mode=true"

            # Create a dummy catalog to check if the SQL processor works
            check_stream = ConfiguredAirbyteStream(
                stream=AirbyteStream(name="check", json_schema={"type": "object"}, supported_sync_modes=[SyncMode.incremental]),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=SyncMode.incremental,
            )
            check_catalog = ConfiguredAirbyteCatalog(streams=[check_stream])
            processor = self._get_sql_processor(
                configured_catalog=check_catalog,
                schema_name="test",
                db_path=path,
                motherduck_token=str(config.get(CONFIG_MOTHERDUCK_API_KEY, "")),
            )
            processor._execute_sql("SELECT 1;")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")

    @override
    def run(self, args: list[str]) -> None:
        """Overridden from CDK base class in order to use the patched SerDes class."""
        init_uncaught_exception_handler(logger)
        parsed_args = self.parse_args(args)
        output_messages = self.run_cmd(parsed_args)
        for message in output_messages:
            print(
                orjson.dumps(
                    PatchedAirbyteMessageSerializer.dump(
                        cast(PatchedAirbyteMessage, message),
                    )
                ).decode()
            )

    @override
    def _parse_input_stream(self, input_stream: io.TextIOWrapper) -> Iterable[AirbyteMessage]:
        """Reads from stdin, converting to Airbyte messages.

        Includes overrides that should be in the CDK but we need to test it in the wild first.

        Rationale:
            The platform injects `id` but our serializer classes don't support
            `additionalProperties`.
        """
        for line in input_stream:
            try:
                yield PatchedAirbyteMessageSerializer.load(orjson.loads(line))
            except orjson.JSONDecodeError:
                logger.info(f"ignoring input which can't be deserialized as Airbyte Message: {line}")
