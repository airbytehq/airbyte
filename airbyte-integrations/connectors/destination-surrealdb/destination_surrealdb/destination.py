#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import logging
import os
import uuid
from collections import defaultdict
from logging import getLogger
from typing import Any, Dict, Iterable, List, Mapping

from surrealdb import RecordID, Surreal

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from airbyte_cdk.sql.constants import AB_EXTRACTED_AT_COLUMN, AB_INTERNAL_COLUMNS, AB_META_COLUMN, AB_RAW_ID_COLUMN


logger = getLogger("airbyte")

CONFIG_SURREALDB_URL = "surrealdb_url"
CONFIG_SURREALDB_NAMESPACE = "surrealdb_namespace"
CONFIG_SURREALDB_DATABASE = "surrealdb_database"
CONFIG_SURREALDB_TOKEN = "surrealdb_token"
CONFIG_SURREALDB_USERNAME = "surrealdb_username"
CONFIG_SURREALDB_PASSWORD = "surrealdb_password"

# `id` is reserved for the record ID in SurrealDB, so a source field named `id` is stored under this name instead.
SOURCE_ID_FIELD = "_airbyte_source_id"

JSON_SCHEMA_TYPE_TO_SURREALDB_TYPE = {
    "string": "string",
    "integer": "int",
    "number": "number",
    "boolean": "bool",
    "object": "object",
    "array": "array",
}


def quote_identifier(name: str) -> str:
    """Quote a table or field name so that it is safe to use in a SurrealQL statement."""
    return "`" + name.replace("`", "\\`") + "`"


def surrealdb_field_type(props: Mapping[str, Any]) -> str:
    """
    Map a JSON schema property definition to a SurrealDB field type.

    Source fields are always optional, because sources do not guarantee that every field is present in every record.
    """
    types = props.get("type", [])
    if isinstance(types, str):
        types = [types]
    kinds: List[str] = []
    for tpe in types:
        if tpe == "null":
            continue
        if tpe == "string" and props.get("format") == "date-time":
            kind = "datetime"
        else:
            kind = JSON_SCHEMA_TYPE_TO_SURREALDB_TYPE.get(tpe, "any")
        if kind not in kinds:
            kinds.append(kind)
    if not kinds or "any" in kinds:
        return "any"
    return f"option<{' | '.join(kinds)}>"


def is_datetime_type(field_type: str) -> bool:
    return field_type in ("datetime", "option<datetime>")


def destination_field_name(field_name: str) -> str:
    return SOURCE_ID_FIELD if field_name == "id" else field_name


def normalize_url(url: str) -> str:
    """
    Get a normalized version of the destination url.
    Translate rocksdb:NAME, surrealkv:NAME, and file:NAME to rocksdb://NAME, surrealkv://NAME, and file://NAME respectively.
    Strip trailing slashes, which would otherwise produce an invalid `//rpc` endpoint for http(s) URLs.
    """
    url = url.rstrip("/")
    if "://" not in url:
        components = url.split(":")
        if len(components) == 2:
            return f"{components[0]}://{components[1]}"
        else:
            raise ValueError(f"Invalid URL: {url}")

    return url


def surrealdb_connect(config: Mapping[str, Any]) -> Surreal:
    """
    Connect to SurrealDB.

    Args:
        config (Mapping[str, Any]): SurrealDB connection config
        config[CONFIG_SURREALDB_URL]: SurrealDB URL
        config[CONFIG_SURREALDB_NAMESPACE]: SurrealDB namespace
        config[CONFIG_SURREALDB_DATABASE]: SurrealDB database
        config[CONFIG_SURREALDB_TOKEN]: SurrealDB token
        config[CONFIG_SURREALDB_USERNAME]: SurrealDB username
        config[CONFIG_SURREALDB_PASSWORD]: SurrealDB password

    Returns:
        Surreal: SurrealDB client
    """
    url = str(config.get(CONFIG_SURREALDB_URL))
    url = normalize_url(url)
    if url.startswith("surrealkv:") or url.startswith("rocksdb:") or url.startswith("file:"):
        components = url.split("://")
        logger.info("Using %s at %s", components[0], components[1])
        os.makedirs(os.path.dirname(components[1]), exist_ok=True)

    signin_args = {}
    if CONFIG_SURREALDB_TOKEN in config:
        signin_args["token"] = str(config[CONFIG_SURREALDB_TOKEN])
    if CONFIG_SURREALDB_USERNAME in config:
        signin_args["username"] = str(config[CONFIG_SURREALDB_USERNAME])
    if CONFIG_SURREALDB_PASSWORD in config:
        signin_args["password"] = str(config[CONFIG_SURREALDB_PASSWORD])

    con = Surreal(url=url)
    if signin_args.keys().__len__() > 0:
        con.signin(signin_args)
    return con


class DestinationSurrealDB(Destination):
    """
    Destination connector for SurrealDB.
    """

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        """
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """
        streams = {s.stream.name for s in configured_catalog.streams}
        logger.info("Starting write to SurrealDB with %d streams", len(streams))

        con = surrealdb_connect(config)

        namespace = str(config.get(CONFIG_SURREALDB_NAMESPACE))
        database = str(config.get(CONFIG_SURREALDB_DATABASE))

        con.query(f"DEFINE NAMESPACE IF NOT EXISTS {namespace};")
        con.query(f"DEFINE DATABASE IF NOT EXISTS {database};")
        con.use(namespace, database)

        # See https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2#breakdown-of-breaking-changes
        is_legacyv1 = False
        if "airbyte_destinations_version" in config:
            is_legacyv1 = config["airbyte_destinations_version"] == "v1"

        do_write_raw = False
        if "airbyte_write_raw" in config:
            do_write_raw = config["airbyte_write_raw"]

        dest_table_definitions = {}

        for configured_stream in configured_catalog.streams:
            table_name = configured_stream.stream.name
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                # delete the tables
                logger.info("Removing table for overwrite: %s", table_name)
                con.query(f"REMOVE TABLE IF EXISTS {quote_identifier(table_name)};")

            # create the table if needed
            con.query(f"DEFINE TABLE IF NOT EXISTS {quote_identifier(table_name)};")

            looks_raw = table_name.startswith("airbyte_raw_")
            fields_to_types = {}
            if is_legacyv1:
                fields_to_types = {"_airbyte_ab_id": "string", "_airbyte_emitted_at": "datetime"}
                if looks_raw:
                    fields_to_types["_airbyte_data"] = "string"
            else:
                fields_to_types = {
                    "_airbyte_raw_id": "string",
                    "_airbyte_extracted_at": "datetime",
                }
                if looks_raw:
                    fields_to_types["_airbyte_data"] = "object"
                    fields_to_types["_airbyte_loaded_at"] = "datetime"
                else:
                    fields_to_types["_airbyte_meta"] = "object"

            stream_properties = configured_stream.stream.json_schema.get("properties", {})
            for field_name, props in stream_properties.items():
                fields_to_types[destination_field_name(field_name)] = surrealdb_field_type(props)

            for field_name, field_type in fields_to_types.items():
                con.query(f"DEFINE FIELD OVERWRITE {quote_identifier(field_name)} ON {quote_identifier(table_name)} TYPE {field_type};")

            dest_table_definitions[table_name] = fields_to_types

        buffer: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for message in input_messages:
            if message.type == Type.STATE:
                # flush the buffer
                for stream_name in buffer.keys():
                    logger.info("flushing buffer for state: %s", message)
                    DestinationSurrealDB._flush_buffer(con=con, buffer=buffer, stream_name=stream_name)

                buffer = defaultdict(list)

                yield message
            elif message.type == Type.RECORD:
                data = message.record.data
                stream_name = message.record.stream
                if stream_name not in streams:
                    logger.debug("Stream %s was not present in configured streams, skipping", stream_name)
                    continue
                emitted_at = message.record.emitted_at
                emitted_at = datetime.datetime.fromtimestamp(emitted_at / 1000, datetime.timezone.utc)
                loaded_at = datetime.datetime.now(datetime.timezone.utc)
                # add to buffer
                raw_id = str(uuid.uuid4())
                record: Dict[str, Any] = {}
                if is_legacyv1:
                    # OLD Raw Table Columns
                    # See https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2#breakdown-of-breaking-changes
                    record["_airbyte_ab_id"] = raw_id
                    record["_airbyte_emitted_at"] = emitted_at
                    record["_airbyte_loaded_at"] = loaded_at
                else:
                    record_meta: dict[str, str] = {}
                    record[AB_RAW_ID_COLUMN] = raw_id
                    record[AB_EXTRACTED_AT_COLUMN] = loaded_at
                    record[AB_META_COLUMN] = record_meta
                if do_write_raw or stream_name.startswith("airbyte_raw_"):
                    if is_legacyv1:
                        # OLD Raw Table Columns
                        # See https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2#breakdown-of-breaking-changes
                        record["_airbyte_data"] = json.dumps(data)
                    else:
                        record["_airbyte_data"] = data
                else:
                    for source_field_name, raw_data in data.items():
                        field_name = destination_field_name(source_field_name)
                        if field_name not in dest_table_definitions[stream_name]:
                            logger.error("field %s not in dest_table_definitions[%s]", field_name, stream_name)
                            continue
                        field_type = dest_table_definitions[stream_name][field_name]
                        if is_datetime_type(field_type) and isinstance(raw_data, str):
                            # This supports the following cases:
                            # - "2022-06-20T18:56:18" in case airbyte_type is "timestamp_without_timezone"
                            raw_data = datetime.datetime.fromisoformat(raw_data)
                        record[field_name] = raw_data
                buffer[stream_name].append(record)
            else:
                logger.info("Message type %s not supported, skipping", message.type)

        # flush any remaining messages
        for stream_name in buffer.keys():
            DestinationSurrealDB._flush_buffer(con=con, buffer=buffer, stream_name=stream_name)

    @staticmethod
    def _flush_buffer(*, con: Surreal, buffer: Dict[str, List[Dict[str, Any]]], stream_name: str):
        table_name = stream_name
        for record in buffer[stream_name]:
            _id = record["_airbyte_ab_id"] if "_airbyte_ab_id" in record else record[AB_RAW_ID_COLUMN]
            try:
                con.upsert(RecordID(table_name, _id), record)
            except Exception as e:
                logger.error("error upserting record %s: %s", record, e)

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
            con = surrealdb_connect(config)
            # HTTP connections require a namespace and database to be selected before running any query.
            con.use(str(config.get(CONFIG_SURREALDB_NAMESPACE)), str(config.get(CONFIG_SURREALDB_DATABASE)))
            logger.debug("Connected to SurrealDB. Running test query.")
            con.query("SELECT * FROM [1];")
            logger.debug("Test query succeeded.")

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
