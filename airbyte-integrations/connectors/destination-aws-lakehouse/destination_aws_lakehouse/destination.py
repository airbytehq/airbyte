#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping
import pandas as pd

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type

from .config_reader import ConnectorConfig
from .lakehouse_writer import LakehouseWriter
from botocore.exceptions import ClientError, InvalidRegionError
import logging
from .handler import Handler
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("airbyte")
RECORD_FLUSH_INTERVAL = 75000

class DestinationAwsLakehouse(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:

        connector_config = ConnectorConfig(**config)

        try:
            handler = Handler(connector_config, self)
        except ClientError as e:
            logger.error(f"Could not create session due to exception {repr(e)}")
            raise Exception(f"Could not create session due to exception {repr(e)}")

        # creating stream writers
        streams = {
            s.stream.name: LakehouseWriter(handler=handler, config=connector_config, configured_stream=s)
            for s in configured_catalog.streams
        }

        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message means all records that came before it
                # have already been published.
                yield message

            elif message.type == Type.RECORD:
                data = message.record.data
                stream = message.record.stream

                streams[stream].append_message(data)

                # Flush records every RECORD_FLUSH_INTERVAL records to limit memory consumption
                # Records will either get flushed when a state message is received or when hitting the RECORD_FLUSH_INTERVAL
                if len(streams[stream]._messages) > RECORD_FLUSH_INTERVAL:
                    logger.debug(f"Reached size limit: flushing records for {stream}")
                    streams[stream].write_to_s3()

                # print a message sample
                # if len(streams[stream]._messages) == 1:
                #     print(streams[stream]._messages[0])

                streams[stream]._total_messages += 1
            else:
                logger.info(f"Unhandled message type {message.type}: {message}")

        # Flush all or remaining records
        self._flush_streams(streams)

        for stream in streams:
            if streams[stream]._total_messages > 0:
                streams[stream].merge_to_iceberg()

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        
        connector_config = ConnectorConfig(**config)

        try:
            handler = Handler(connector_config, self)
        except (ClientError, AttributeError) as e:
            logger.error(f"""Could not create session on {connector_config.aws_account_id} Exception: {repr(e)}""")
            message = f"""Could not authenticate using {connector_config.credentials_type} on Account {connector_config.aws_account_id} Exception: {repr(e)}"""
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)
        except InvalidRegionError:
            message = f"{connector_config.region} is not a valid AWS region"
            logger.error(message)
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)
        
        try:
            handler.head_bucket()
        except ClientError as e:
            message = f"""Could not find bucket {connector_config.bucket_name} in aws://{connector_config.aws_account_id}:{connector_config.region} Exception: {repr(e)}"""
            return AirbyteConnectionStatus(status=Status.FAILED, message=message)

        try:  
            df = pd.DataFrame({"id": [1, 2], "value": ["foo", "bar"]})
            handler.create_temp_athena_table(df=df)
            handler.temp_table_cleanup()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.info(e)
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
        
    def _flush_streams(self, streams: Dict[str, LakehouseWriter]) -> None:
        for stream in streams:
            streams[stream].write_to_s3()
