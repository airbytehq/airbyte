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

from surrealdb import Surreal

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


def normalize_url(url: str) -> str:
    """
    Get a normalized version of the destination url.
    Translate rocksdb:NAME, surrealkv:NAME, and file:NAME to rocksdb://NAME, surrealkv://NAME, and file://NAME respectively.
    """
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
                con.query(f"REMOVE TABLE IF EXISTS {table_name};")

            # create the table if needed
            con.query(f"DEFINE TABLE IF NOT EXISTS {table_name};")

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

            stream_fields = configured_stream.stream.json_schema["properties"].keys()
            for field_name in stream_fields:
                props = configured_stream.stream.json_schema["properties"][field_name]
                tpe = props["type"]
                fmt = props["format"] if "format" in props else None
                if tpe == "string" and fmt == "date-time":
                    fields_to_types[field_name] = "datetime"
                elif tpe == "integer":
                    fields_to_types[field_name] = "int"
                else:
                    fields_to_types[field_name] = tpe

            for field_name, field_type in fields_to_types.items():
                con.query(f"DEFINE FIELD OVERWRITE {field_name} ON {table_name} TYPE {field_type};")

            dest_table_definitions[table_name] = fields_to_types

        buffer = defaultdict(lambda: defaultdict(list))

        for message in input_messages:
            if message.type == Type.STATE:
                # flush the buffer
                for stream_name in buffer.keys():
                    logger.info("flushing buffer for state: %s", message)
                    DestinationSurrealDB._flush_buffer(con=con, buffer=buffer, stream_name=stream_name)

                buffer = defaultdict(lambda: defaultdict(list))

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
                if is_legacyv1:
                    # OLD Raw Table Columns
                    # See https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2#breakdown-of-breaking-changes
                    buffer[stream_name]["_airbyte_ab_id"].append(raw_id)
                    buffer[stream_name]["_airbyte_emitted_at"].append(emitted_at)
                    buffer[stream_name]["_airbyte_loaded_at"].append(loaded_at)
                else:
                    record_meta: dict[str, str] = {}
                    buffer[stream_name][AB_RAW_ID_COLUMN].append(raw_id)
                    buffer[stream_name][AB_EXTRACTED_AT_COLUMN].append(loaded_at)
                    buffer[stream_name][AB_META_COLUMN].append(record_meta)
                if do_write_raw or stream_name.startswith("airbyte_raw_"):
                    if is_legacyv1:
                        # OLD Raw Table Columns
                        # See https://docs.airbyte.com/release_notes/upgrading_to_destinations_v2#breakdown-of-breaking-changes
                        buffer[stream_name]["_airbyte_data"].append(json.dumps(data))
                    else:
                        buffer[stream_name]["_airbyte_data"].append(data)
                else:
                    for field_name in data.keys():
                        raw_data = data[field_name]
                        if field_name not in dest_table_definitions[stream_name]:
                            logger.error("field %s not in dest_table_definitions[%s]", field_name, stream_name)
                            continue
                        field_type = dest_table_definitions[stream_name][field_name]
                        if field_type == "datetime":
                            # This supports the following cases:
                            # - "2022-06-20T18:56:18" in case airbyte_type is "timestamp_without_timezone"
                            raw_data = datetime.datetime.fromisoformat(raw_data)
                        buffer[stream_name][field_name].append(raw_data)
            else:
                logger.info("Message type %s not supported, skipping", message.type)

        # flush any remaining messages
        for stream_name in buffer.keys():
            DestinationSurrealDB._flush_buffer(con=con, buffer=buffer, stream_name=stream_name)

    @staticmethod
    def _flush_buffer(*, con: Surreal, buffer: Dict[str, Dict[str, List[Any]]], stream_name: str):
        table_name = stream_name
        buf = buffer[stream_name]
        field_names = buf.keys()
        id_field = "_airbyte_ab_id" if "_airbyte_ab_id" in field_names else AB_RAW_ID_COLUMN
        id_column = buf[id_field]
        for i, _id in enumerate(id_column):
            record = {}
            for field_name in field_names:
                record[field_name] = buf[field_name][i]
            try:
                con.upsert(f"{table_name}:{_id}", record)
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
            logger.debug("Connected to SurrealDB. Running test query.")
            con.query("SELECT * FROM [1];")
            logger.debug("Test query succeeded.")

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
