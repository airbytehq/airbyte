# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import json

from typing import Mapping, Any, Iterable

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, ConfiguredAirbyteCatalog, AirbyteMessage, Status, Type

from botocore.exceptions import ClientError
from .config_reader import ConnectorConfig
from .airbyte_helper import StreamWriter

from .aws_helpers import AwsHelper, LakeformationTransaction


class DestinationAwsDatalake(Destination):
    def write(
            self,
            config: Mapping[str, Any],
            configured_catalog: ConfiguredAirbyteCatalog,
            input_messages: Iterable[AirbyteMessage]
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
        self.logger.debug(f"write method invoked")
        connector_config = ConnectorConfig(**config)
        self.logger.debug(f"Creating AWS session")
        try:
            aws_helper = AwsHelper(connector_config, self)
        except ClientError as e:
            self.logger.error(f"Could not create session due to exception {repr(e)}")
            raise
        self.logger.debug(f"AWS session creation OK")

        with LakeformationTransaction(aws_helper) as tx:
            # creating stream writers
            streams = {
                s.stream.name: StreamWriter(
                    name=s.stream.name,
                    aws_helper=aws_helper,
                    tx=tx,
                    connector_config=connector_config,
                    schema=s.stream.json_schema["properties"],
                    sync_mode=s.destination_sync_mode,
                )
                for s in configured_catalog.streams
            }
            for message in input_messages:
                if message.type == Type.STATE:
                    streams[stream].add_to_datalake()
                    self.logger.debug(f"Write is yielding")
                    yield message
                    self.logger.debug(f"Write is back from yield")
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
        self.logger.debug(f"check method invoked")
        connector_config = ConnectorConfig(**config)
        logger.debug("Checking account")
        try:
            aws_helper = AwsHelper(connector_config, self)
        except ClientError as e:
            logger.error(f"""Could not create session on {connector_config.AwsAccountId}
Exception: {repr(e)}""")
            message = f"""Could not authenticate using {connector_config.AuthMode} on Account {connector_config.AwsAccountId}
Exception: {repr(e)}"""
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)
        logger.debug("Account OK")
        logger.debug("Checking bucket")
        try:
            aws_helper.head_bucket()
        except ClientError as e:
            message = f"""Could not find bucket {connector_config.BucketName} in aws://{connector_config.AwsAccountId}:{connector_config.Region}
Exception: {repr(e)}"""
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)
        logger.debug("Bucket OK")
        logger.debug("Checking Lakeformation")
        with LakeformationTransaction(aws_helper) as tx:
            table_location = "s3://" + connector_config.BucketName + "/" + connector_config.Prefix + "/" + "airbyte_test/"
            table = aws_helper.get_table(
                tx.txid, connector_config.DatabaseName, "airbyte_test", table_location
            )
        if table is None:
            message = f"Could not create a table in database {connector_config.DatabaseName}"
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)
        logger.debug("Lakeformation OK")
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)
