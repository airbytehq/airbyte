#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import traceback
import uuid
from typing import Any, Dict, Iterable, Mapping, Optional

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from destination_sftp.client import SftpClient


class DestinationSftp(Destination):
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
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """
        # Extract the SSH algorithms configuration if provided
        ssh_algorithms: Optional[Dict[str, Any]] = config.get("ssh_algorithms")

        # Extract the configuration, with defaults
        sftp_config = {
            "host": config["host"],
            "port": config.get("port", 22),
            "username": config["username"],
            "password": config["password"],
            "destination_path": config["destination_path"],
            "file_format": config.get("file_format", "json"),  # Default to json for backward compatibility
            "file_name_pattern": config.get("file_name_pattern", "airbyte_{format}_{stream}"),  # Default naming pattern
        }

        # Add SSH algorithms if provided
        if ssh_algorithms:
            sftp_config["ssh_algorithms"] = ssh_algorithms

        with SftpClient(**sftp_config) as writer:
            for configured_stream in configured_catalog.streams:
                if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                    writer.delete(configured_stream.stream.name)

            for message in input_messages:
                if message.type == Type.STATE:
                    # Emitting a state message indicates that all records which came
                    # before it have been written to the destination. We don't need to
                    # do anything specific to save the data so we just re-emit these
                    yield message
                elif message.type == Type.RECORD:
                    record = message.record
                    if record is not None:
                        writer.write(record.stream, record.data)
                else:
                    # ignore other message types for now
                    continue

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination.
        """
        try:
            # Generate a unique test stream name
            stream = str(uuid.uuid4())

            # Extract basic configuration
            sftp_config = {
                "host": config["host"],
                "port": int(config.get("port", 22)),
                "username": config["username"],
                "password": config["password"],
                "destination_path": config["destination_path"],
                "file_format": config.get("file_format", "json"),
                "file_name_pattern": config.get("file_name_pattern", "airbyte_{format}_{stream}"),
            }

            # Add SSH algorithms if provided
            if "ssh_algorithms" in config:
                sftp_config["ssh_algorithms"] = config["ssh_algorithms"]

            logger.info(f"Testing connection to {sftp_config['host']}:{sftp_config['port']} with user {sftp_config['username']}")
            logger.info(f"Destination path: {sftp_config['destination_path']}")

            with SftpClient(**sftp_config) as client:
                # Test write operation
                logger.info(f"Testing write operation with stream: {stream}")
                client.write(stream, {"value": "_airbyte_connection_check"})
                logger.info("Write test successful")

                # Test read operation
                logger.info("Testing read operation")
                data = client.read_data(stream)
                logger.info(f"Read test successful: {data}")

                # Test delete operation
                logger.info("Testing delete operation")
                client.delete(stream)
                logger.info("Delete test successful")

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            error_msg = f"An exception occurred: {e}. \nStacktrace: \n{traceback.format_exc()}"
            logger.error(error_msg)
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message=error_msg,
            )
