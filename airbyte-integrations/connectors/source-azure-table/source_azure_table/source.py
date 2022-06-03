#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import traceback
from datetime import datetime
from typing import Dict, Generator

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources import Source

from .reader import Reader


class SourceAzureTable(Source):
    """This source helps to sync data from one azure data table a time"""

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        try:
            reader = Reader(logger, config)
            client = reader.get_table_service()
            tables_iterator = client.list_tables(results_per_page=1)
            next(tables_iterator)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except StopIteration:
            logger.log("No tables found, but credentials are correct.")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        reader = Reader(logger, config)
        streams = reader.get_streams()
        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        try:
            for configured_stream in catalog.streams:
                if configured_stream.sync_mode == SyncMode.full_refresh:
                    stream_name = configured_stream.stream.name
                    reader = Reader(logger, config)
                    table_client = reader.get_table_client(stream_name)
                    logger.info(f"Reading data from stream '{stream_name}'")

                    for row in reader.read(table_client, None):
                        # Timestamp property is in metadata object
                        # row.metadata.timestamp
                        row["additionalProperties"] = True
                        yield AirbyteMessage(
                            type=Type.RECORD,
                            record=AirbyteRecordMessage(stream=stream_name, data=row, emitted_at=int(datetime.now().timestamp()) * 1000),
                        )
                if configured_stream.sync_mode == SyncMode.incremental:
                    logger.warn(f"Incremental sync is not supported by stream {stream_name}")

        except Exception as err:
            reason = f"Failed to read data of {stream_name}: {repr(err)}\n{traceback.format_exc()}"
            logger.error(reason)
            raise err
