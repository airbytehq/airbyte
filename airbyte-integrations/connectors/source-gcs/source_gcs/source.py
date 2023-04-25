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

from .helpers import construct_file_schema, get_gcs_blobs, get_stream_name, read_csv_file


class SourceGCS(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Check to see if a client can be created and list the files in the bucket.
        """
        try:
            blobs = get_gcs_blobs(config)
            if not blobs:
                return AirbyteConnectionStatus(status=Status.FAILED, message="No compatible file found in bucket")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        streams = []

        blobs = get_gcs_blobs(config)
        for blob in blobs:
            # Read the first 0.1MB of the file to determine schema
            df = read_csv_file(blob, read_header_only=True)
            stream_name = get_stream_name(blob)
            json_schema = construct_file_schema(df)
            streams.append(AirbyteStream(name=stream_name, json_schema=json_schema, supported_sync_modes=["full_refresh"]))

        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        logger.info("Start reading")
        blobs = get_gcs_blobs(config)

        # Read only selected stream(s)
        selected_streams = [configged_stream.stream.name for configged_stream in catalog.streams]
        selected_blobs = [blob for blob in blobs if get_stream_name(blob) in selected_streams]

        for blob in selected_blobs:
            logger.info(blob.name)
            df = read_csv_file(blob)
            stream_name = get_stream_name(blob)
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                row_dict = {k: str(v) for k, v in row_dict.items()}
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=stream_name, data=row_dict, emitted_at=int(datetime.now().timestamp()) * 1000),
                )
