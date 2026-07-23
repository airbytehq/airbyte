# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import logging
import os
import ssl
import uuid
from logging import getLogger
from typing import Any, Iterable, Mapping

from pydantic import ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    DestinationSyncMode,
    Status,
)
from destination_starrocks.config import StarRocksConfig
from destination_starrocks.writer import StarRocksWriter


logger = getLogger("airbyte")


class DestinationStarRocks(Destination):
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
        try:
            parsed_config = StarRocksConfig(**config)
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise

        writer = StarRocksWriter(parsed_config)
        loading_mode = parsed_config.loading_mode.get("mode", "typed")

        if loading_mode == "raw":
            yield from writer.write_raw(configured_catalog, input_messages)
        else:
            yield from writer.write_typed(configured_catalog, input_messages)

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
            try:
                parsed_config = StarRocksConfig(**config)
            except ValidationError as e:
                errors = e.errors()
                field_errors = []
                for error in errors:
                    field = ".".join(str(x) for x in error["loc"])
                    msg = error["msg"]
                    field_errors.append(f"{field}: {msg}")
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"Configuration validation failed. Please check the following fields: {'; '.join(field_errors)}"
                )

            logger.info(f"Attempting to connect to StarRocks at {parsed_config.host}:{parsed_config.port}")

            try:
                connection_url = URL.create(
                    drivername="starrocks",
                    username=parsed_config.username,
                    password=parsed_config.password,
                    host=parsed_config.host,
                    port=parsed_config.port,
                    database=parsed_config.database,
                )

                engine = create_engine(connection_url)
            except Exception as e:
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"Failed to create database engine. This is an internal error. Error: {str(e)}"
                )

            try:
                with engine.connect() as connection:
                    result = connection.execute(text("SELECT 1"))
                    row = result.fetchone()
                    if row is None or row[0] != 1:
                        raise Exception("Query returned unexpected result")

                    # Test write/drop permissions
                    test_table = f"_airbyte_connection_test_{uuid.uuid4().hex[:8]}"
                    try:
                        connection.execute(text(f"""
                            CREATE TABLE `{parsed_config.database}`.`{test_table}` (
                                id INT
                            )
                        """))
                        connection.execute(text(f"DROP TABLE `{parsed_config.database}`.`{test_table}`"))
                        connection.commit()
                    except Exception as e:
                        return AirbyteConnectionStatus(
                            status=Status.FAILED,
                            message=f"User '{parsed_config.username}' does not have write permissions on database '{parsed_config.database}'. Please grant CREATE TABLE and DROP TABLE permissions. Error: {str(e)}"
                        )

                    # Verify Stream Load API accessibility
                    writer = StarRocksWriter(parsed_config)
                    try:
                        if not writer.verify_stream_load_connectivity():
                            return AirbyteConnectionStatus(
                                status=Status.FAILED,
                                message=f"Stream Load API is not accessible at "
                                f"{writer._stream_load_base_url}. "
                                f"Please verify the http_port setting and that the endpoint "
                                f"is reachable from this host."
                            )
                        logger.info("Stream Load API is accessible - ready to sync")
                    except Exception as e:
                        return AirbyteConnectionStatus(
                            status=Status.FAILED,
                            message=f"Stream Load API check failed: {str(e)}"
                        )

                logger.info("Connection check successful")
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)

            except SQLAlchemyError as e:
                error_msg = str(e).lower()
                if "access denied" in error_msg or "authentication" in error_msg:
                    return AirbyteConnectionStatus(
                        status=Status.FAILED,
                        message=f"Authentication failed: Please verify your username and password are correct. Error: {str(e)}"
                    )
                elif "unknown database" in error_msg:
                    return AirbyteConnectionStatus(
                        status=Status.FAILED,
                        message=f"Database '{parsed_config.database}' does not exist. Please create the database first or verify the database name is correct."
                    )
                elif "can't connect" in error_msg or "connection refused" in error_msg or "timed out" in error_msg:
                    return AirbyteConnectionStatus(
                        status=Status.FAILED,
                        message=f"Unable to connect to StarRocks at {parsed_config.host}:{parsed_config.port}. Please verify: 1) The host and port are correct, 2) StarRocks is running, 3) There are no firewall rules blocking the connection. Error: {str(e)}"
                    )
                else:
                    return AirbyteConnectionStatus(
                        status=Status.FAILED,
                        message=f"Failed to connect to StarRocks: {str(e)}"
                    )

        except Exception as e:
            logger.error(f"Unexpected error during connection check: {str(e)}")
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message=f"An unexpected error occurred: {str(e)}. Please contact support with this error message."
            )

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        """
        Returns the connector specification from spec.json.
        """
        spec_path = os.path.join(os.path.dirname(__file__), "spec.json")
        with open(spec_path, 'r') as f:
            spec_json = json.load(f)

        return ConnectorSpecification(
            documentationUrl=spec_json.get("documentationUrl", "https://docs.airbyte.com/integrations/destinations/starrocks"),
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append],
            connectionSpecification=spec_json["connectionSpecification"],
        )
