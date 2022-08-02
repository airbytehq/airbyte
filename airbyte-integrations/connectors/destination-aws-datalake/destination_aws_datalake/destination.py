#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type
from botocore.exceptions import ClientError

from .aws import AwsHandler, LakeformationTransaction
from .config_reader import ConnectorConfig
from .stream_writer import StreamWriter


class DestinationAwsDatalake(Destination):
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
            self.logger.error(f"Could not create session due to exception {repr(e)}")
            raise
        self.logger.debug("AWS session creation OK")

        # creating stream writers
        streams = {
            s.stream.name: StreamWriter(
                name=s.stream.name,
                aws_handler=aws_handler,
                connector_config=connector_config,
                schema=s.stream.json_schema["properties"],
                sync_mode=s.destination_sync_mode,
            )
            for s in configured_catalog.streams
        }

        for message in input_messages:
            if message.type == Type.STATE:
                yield message
            else:
                data = message.record.data
                stream = message.record.stream
                streams[stream].append_message(json.dumps(data, default=str))

        for stream_name, stream in streams.items():
            stream.add_to_datalake()

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

        try:
            aws_handler.head_bucket()
        except ClientError as e:
            message = f"""Could not find bucket {connector_config.bucket_name} in aws://{connector_config.aws_account_id}:{connector_config.region} Exception: {repr(e)}"""
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)

        with LakeformationTransaction(aws_handler) as tx:
            table_location = "s3://" + connector_config.bucket_name + "/" + connector_config.bucket_prefix + "/" + "airbyte_test/"
            table = aws_handler.get_table(
                txid=tx.txid,
                database_name=connector_config.lakeformation_database_name,
                table_name="airbyte_test",
                location=table_location,
            )
        if table is None:
            message = f"Could not create a table in database {connector_config.lakeformation_database_name}"
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)
