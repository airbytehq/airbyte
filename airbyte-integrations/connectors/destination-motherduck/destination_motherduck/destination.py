# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import datetime
import json
import logging
import os
import re
import uuid
from collections import defaultdict
from logging import getLogger
from typing import Any, Dict, Iterable, List, Mapping
from urllib.parse import urlparse

from airbyte_cdk import AirbyteStream, ConfiguredAirbyteStream, SyncMode
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
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

        path = str(config.get("destination_path"))
        path = self._get_destination_path(path)
        schema_name = validated_sql_name(config.get("schema", CONFIG_DEFAULT_SCHEMA))
        motherduck_api_key = str(config.get(CONFIG_MOTHERDUCK_API_KEY, ""))

        for configured_stream in configured_catalog.streams:
            stream_name = configured_stream.stream.name
            # TODO: we're calling private methods on processor, should move this to write_stream_data or similar
            processor = self._get_sql_processor(
                configured_catalog=configured_catalog,
                schema_name=schema_name,
                db_path=path,
                motherduck_token=motherduck_api_key,
            )
            processor._ensure_schema_exists()

            table_name = processor.normalizer.normalize(stream_name)
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                # delete the tables
                logger.info(f"Dropping tables for overwrite: {table_name}")

                processor._drop_temp_table(table_name, if_exists=True)

            # Get the SQL column definitions
            sql_columns = processor._get_sql_column_definitions(stream_name)
            column_definition_str = ",\n                ".join(
                f"{self._quote_identifier(column_name)} {sql_type}" for column_name, sql_type in sql_columns.items()
            )

            # create the table if needed
            catalog_provider = CatalogProvider(configured_catalog)
            primary_keys = catalog_provider.get_primary_keys(stream_name)
            processor._create_table_if_not_exists(
                table_name=table_name,
                column_definition_str=column_definition_str,
                primary_keys=primary_keys,
            )

            processor._ensure_compatible_table_schema(stream_name=stream_name, table_name=table_name)

        buffer: dict[str, dict[str, list[Any]]] = defaultdict(lambda: defaultdict(list))
        for message in input_messages:
            if message.type == Type.STATE:
                # flush the buffer
                self._flush_buffer(buffer, configured_catalog, path, schema_name, motherduck_api_key)
                buffer = defaultdict(lambda: defaultdict(list))

                yield message
            elif message.type == Type.RECORD and message.record is not None:
                data = message.record.data
                stream_name = message.record.stream
                if stream_name not in streams:
                    logger.debug(f"Stream {stream_name} was not present in configured streams, skipping")
                    continue
                # add to buffer
                record_meta: dict[str, str] = {}
                for column_name in sql_columns:
                    if column_name in data:
                        buffer[stream_name][column_name].append(data[column_name])
                    elif column_name not in AB_INTERNAL_COLUMNS:
                        buffer[stream_name][column_name].append(None)
                buffer[stream_name][AB_RAW_ID_COLUMN].append(str(uuid.uuid4()))
                buffer[stream_name][AB_EXTRACTED_AT_COLUMN].append(datetime.datetime.now().isoformat())
                buffer[stream_name][AB_META_COLUMN].append(json.dumps(record_meta))

            else:
                logger.info(f"Message type {message.type} not supported, skipping")

        # flush any remaining messages
        self._flush_buffer(buffer, configured_catalog, path, schema_name, motherduck_api_key)

    def _flush_buffer(
        self,
        buffer: Dict[str, Dict[str, List[Any]]],
        configured_catalog: ConfiguredAirbyteCatalog,
        db_path: str,
        schema_name: str,
        motherduck_api_key: str,
    ) -> None:
        """
        Flush the buffer to the destination
        """
        for configured_stream in configured_catalog.streams:
            stream_name = configured_stream.stream.name
            if stream_name in buffer:
                processor = self._get_sql_processor(
                    configured_catalog=configured_catalog, schema_name=schema_name, db_path=db_path, motherduck_token=motherduck_api_key
                )
                processor.write_stream_data_from_buffer(buffer, stream_name, configured_stream.destination_sync_mode)

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
