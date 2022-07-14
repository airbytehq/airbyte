#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

import traceback
from datetime import datetime
from typing import Any, Dict, Generator, Mapping

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    Status,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import Source
from source_dynamodb import reader


class SourceDynamodb(Source):
    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            rdr = reader.Reader(logger=logger, config=config)
            number_of_tables = rdr.check()
            if number_of_tables == 0:
                logger.info("No tables found, but credentials are correct.")

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message=f"An exception occurred: {str(e)}",
            )

    def discover(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteCatalog:

        rdr = reader.Reader(logger=logger, config=config)
        streams = rdr.get_streams()
        return AirbyteCatalog(streams=streams)

    def read(
        self,
        logger: AirbyteLogger,
        config,
        catalog: ConfiguredAirbyteCatalog,
        state: Dict[str, Any],
    ) -> Generator[AirbyteMessage, None, None]:
        for config_stream in catalog.streams:
            stream_name = config_stream.stream.name
            try:
                if config_stream.sync_mode == SyncMode.full_refresh:
                    rdr = reader.Reader(logger=logger, config=config)
                    logger.info(f"Reading data fror stream '{stream_name}'")

                    for row in rdr.read(table_name=stream_name):
                        row["additionalProperties"] = True
                        yield AirbyteMessage(
                            log=None,
                            catalog=None,
                            state=None,
                            trace=None,
                            type=Type.RECORD,
                            record=AirbyteRecordMessage(
                                stream=stream_name,
                                data=row,
                                emitted_at=int(datetime.now().timestamp()) * 1000,
                                namespace=config_stream.stream.namespace,
                            ),
                        )
            except Exception as e:
                msg = f"Failed to read data for stream '{stream_name}': " f"{repr(e)}\n{traceback.format_exc()}"
                logger.error(message=msg)
                raise e
