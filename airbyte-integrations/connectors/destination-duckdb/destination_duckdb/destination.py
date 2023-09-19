#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import os
import uuid
from collections import defaultdict
from logging import getLogger
from typing import Any, Iterable, Mapping

import duckdb
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type

logger = getLogger("airbyte")


class DestinationDuckdb(Destination):
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

        # Get and register auth token if applicable
        motherduck_api_key = str(config.get("motherduck_api_key"))
        if motherduck_api_key:
            os.environ["motherduck_token"] = motherduck_api_key

        con = duckdb.connect(database=path, read_only=False)

        # create the tables if needed
        # con.execute("BEGIN TRANSACTION")
        for configured_stream in configured_catalog.streams:
            name = configured_stream.stream.name
            table_name = f"_airbyte_raw_{name}"
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                # delete the tables
                logger.info(f"Dropping tables for overwrite: {table_name}")
                query = """
                DROP TABLE IF EXISTS {}
                """.format(
                    table_name
                )
                con.execute(query)
            # create the table if needed
            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                _airbyte_ab_id TEXT PRIMARY KEY,
                _airbyte_emitted_at DATETIME,
                _airbyte_data JSON
            )
            """

            con.execute(query)

        buffer = defaultdict(list)

        for message in input_messages:
            if message.type == Type.STATE:
                # flush the buffer
                for stream_name in buffer.keys():
                    logger.info(f"flushing buffer for state: {message}")
                    query = """
                    INSERT INTO {table_name} (_airbyte_ab_id, _airbyte_emitted_at, _airbyte_data)
                    VALUES (?,?,?)
                    """.format(
                        table_name=f"_airbyte_raw_{stream_name}"
                    )
                    con.executemany(query, buffer[stream_name])

                con.commit()
                buffer = defaultdict(list)

                yield message
            elif message.type == Type.RECORD:
                data = message.record.data
                stream = message.record.stream
                if stream not in streams:
                    logger.debug(f"Stream {stream} was not present in configured streams, skipping")
                    continue

                # add to buffer
                buffer[stream].append(
                    (
                        str(uuid.uuid4()),
                        datetime.datetime.now().isoformat(),
                        json.dumps(data),
                    )
                )
            else:
                logger.info(f"Message type {message.type} not supported, skipping")

        # flush any remaining messages
        for stream_name in buffer.keys():
            query = """
            INSERT INTO {table_name}
            VALUES (?,?,?)
            """.format(
                table_name=f"_airbyte_raw_{stream_name}"
            )

            con.executemany(query, buffer[stream_name])
            con.commit()

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
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
            path = config.get("destination_path")
            path = self._get_destination_path(path)

            if path.startswith("/local"):
                logger.info(f"Using DuckDB file at {path}")
                os.makedirs(os.path.dirname(path), exist_ok=True)

            if "motherduck_api_key" in config:
                os.environ["motherduck_token"] = config["motherduck_api_key"]

            con = duckdb.connect(database=path, read_only=False)
            con.execute("SELECT 1;")

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
