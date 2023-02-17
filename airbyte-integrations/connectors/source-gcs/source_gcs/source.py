#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Dict, Generator

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import Source

from .helpers import construct_file_schema, get_gcs_blobs, read_csv_file


class SourceGCS(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Check to see if a client can be created and list the files in the bucket.
        """
        try:
            blobs = get_gcs_blobs(config)
            # TODO: only support CSV intially. Change this check if implementing other file formats.
            files = [blob.name for blob in blobs if "csv" in blob.name.lower()]
            if not files:
                return AirbyteConnectionStatus(status=Status.FAILED, message=f"No compatible file found in bucket")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        streams = []

        blobs = get_gcs_blobs(config)
        for blob in blobs:
            # Read the first 0.1MB of the file to determine schema
            df = read_csv_file(blob, limit_bytes=102400)
            stream_name = blob.name.replace(".csv", "")
            json_schema = construct_file_schema(df)
            streams.append(AirbyteStream(name=stream_name, json_schema=json_schema, supported_sync_modes=["full_refresh"]))

        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        logger.info("Start reading")
        blobs = get_gcs_blobs(config)
        for blob in blobs:
            logger.info(blob.name)
            df = read_csv_file(blob)
            logger.info(df)
            stream_name = blob.name.replace(".csv", "")
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                print(row_dict)
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=stream_name, data=row_dict, emitted_at=int(datetime.now().timestamp()) * 1000),
                )
