#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Any, Dict, Iterable, Mapping, Optional
from uuid import uuid4

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from firebolt.client import DEFAULT_API_URL
from firebolt.db import Connection, connect

from .writer import FireboltS3Writer, FireboltSQLWriter


def parse_config(config: json, logger: Optional[AirbyteLogger] = None) -> Dict[str, Any]:
    """
    Convert dict of config values to firebolt.db.Connection arguments
    :param config: json-compatible dict of settings
    :param logger: AirbyteLogger instance to print logs.
    :return: dictionary of firebolt.db.Connection-compatible kwargs
    """
    connection_args = {
        "database": config["database"],
        "username": config["username"],
        "password": config["password"],
        "api_endpoint": config.get("host", DEFAULT_API_URL),
        "account_name": config.get("account"),
    }
    # engine can be a name or a full URL of a cluster
    engine = config.get("engine")
    if engine:
        if "." in engine:
            connection_args["engine_url"] = engine
        else:
            connection_args["engine_name"] = engine
    elif logger:
        logger.info("Engine parameter was not provided. Connecting to the default engine.")
    return connection_args


def establish_connection(config: json, logger: Optional[AirbyteLogger] = None) -> Connection:
    """
    Creates a connection to Firebolt database using the parameters provided.
    :param config: Json object containing db credentials.
    :param logger: AirbyteLogger instance to print logs.
    :return: PEP-249 compliant database Connection object.
    """
    logger.debug("Connecting to Firebolt.") if logger else None
    connection = connect(**parse_config(config, logger))
    logger.debug("Connection to Firebolt established.") if logger else None
    return connection


class DestinationFirebolt(Destination):
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

        with establish_connection(config) as connection:
            if config.get("s3_bucket"):
                writer = FireboltS3Writer(connection, config["s3_bucket"], config["aws_key_id"], config["aws_key_secret"])
            else:
                writer = FireboltSQLWriter(connection)

            for configured_stream in configured_catalog.streams:
                if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                    writer.delete_table(configured_stream.stream.name)
                writer.create_raw_table(configured_stream.stream.name)

            for message in input_messages:
                if message.type == Type.STATE:
                    yield message
                elif message.type == Type.RECORD:
                    data = message.record.data
                    stream = message.record.stream
                    # Skip unselected streams
                    if stream not in streams:
                        continue
                    writer.queue_write_data(stream, str(uuid4()), int(datetime.now().timestamp()) * 1000, json.dumps(data))

            # Flush any leftover messages
            writer.flush()

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
            s3_bucket = config.get("s3_bucket")
            aws_key_id = config.get("aws_key_id")
            aws_key_secret = config.get("aws_key_secret")
            if any([s3_bucket, aws_key_id, aws_key_secret]) and not all([s3_bucket, aws_key_id, aws_key_secret]):
                raise Exception("If using External Table strategy please provide S3 bucket name, AWS Key and AWS Secret")
            with establish_connection(config, logger) as connection:
                # We can only verify correctness of connection parameters on execution
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
