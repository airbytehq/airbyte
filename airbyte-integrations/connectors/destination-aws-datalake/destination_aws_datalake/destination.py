#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import pandas as pd

from typing import Any, Iterable, Mapping, Dict
from botocore.exceptions import ClientError, InvalidRegionError

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type

from .aws import AwsHandler
from .config_reader import ConnectorConfig
from .stream_writer import StreamWriter

logger = logging.getLogger("airbyte")


class DestinationAwsDatalake(Destination):
    def _flush_streams(self, streams: Dict[str, StreamWriter]) -> None:
        for stream in streams:
            streams[stream].flush()

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
        connector_config = ConnectorConfig(**config)

        try:
            aws_handler = AwsHandler(connector_config, self)
        except ClientError as e:
            logger.error(f"Could not create session due to exception {repr(e)}")
            raise Exception(f"Could not create session due to exception {repr(e)}")

        # creating stream writers
        streams = {
            s.stream.name: StreamWriter(aws_handler=aws_handler, config=connector_config, configured_stream=s)
            for s in configured_catalog.streams
        }

        for message in input_messages:
            if message.type == Type.STATE:
                if not message.state.data:
                    # if state is empty, reset all streams
                    logger.info(f"Received empty state, resetting streams: {message}")
                    for stream in streams:
                        streams[stream].reset()

                yield message

            elif message.type == Type.RECORD:
                data = message.record.data
                stream = message.record.stream
                streams[stream].append_message(data)

            else:
                logger.info(f"Unhandled message type {message.type}: {message}")

        self._flush_streams(streams)

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

        connector_config = ConnectorConfig(**config)

        try:
            aws_handler = AwsHandler(connector_config, self)
        except (ClientError, AttributeError) as e:
            logger.error(f"""Could not create session on {connector_config.aws_account_id} Exception: {repr(e)}""")
            message = f"""Could not authenticate using {connector_config.credentials_type} on Account {connector_config.aws_account_id} Exception: {repr(e)}"""
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)
        except InvalidRegionError as e:
            message = f"{connector_config.region} is not a valid AWS region"
            logger.error(message)
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)

        try:
            aws_handler.head_bucket()
        except ClientError as e:
            message = f"""Could not find bucket {connector_config.bucket_name} in aws://{connector_config.aws_account_id}:{connector_config.region} Exception: {repr(e)}"""
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)

        try:
            df = pd.DataFrame({"id": [1, 2], "value": ["foo", "bar"]})

            bucket = f"s3://{connector_config.bucket_name}"
            if connector_config.bucket_prefix:
                bucket += f"/{connector_config.bucket_prefix}"

            path = f"{bucket}/{connector_config.lakeformation_database_name}/airbyte_test/"
            logger.debug(f"Writing test file to {path}")
            aws_handler.write(df, path, connector_config.lakeformation_database_name, "airbyte_test", None)
            aws_handler.delete_table(connector_config.lakeformation_database_name, "airbyte_test")

        except Exception as e:
            message = f"Could not create a table in database {connector_config.lakeformation_database_name}: {repr(e)}"
            logger.error(message)
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)
