# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
import os
import tempfile
import pandas as pd
from datetime import datetime, timedelta
from typing import Any, Dict, Generator
import logging, inspect

from airbyte_protocol_dataclasses.models import (
    AirbyteStateType,
    AirbyteStreamState,
    StreamDescriptor,
    AirbyteStateBlob,
    AirbyteCatalog,
    AirbyteStateBlob,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    AirbyteStateStats,
    Status,
    Type,
    SyncMode,
    AirbyteStateMessage
)
from airbyte_cdk.sources import Source
from .config import configuration
from .report_query import report_job
from .utils import (
    parse_date_to_dict,
    get_start_date,
    get_end_date,
    create_ad_manager_client,
    get_state,
    update_report_job_config
)

import pytz
from io import StringIO
from pydantic import BaseModel

# Constants

scopes = configuration["stream"]["scopes"]
application_name = configuration["stream"]["application_name"]
stream_name = configuration["stream"]["stream_name"]
temp_file_mode = configuration["report"]["temp_file_mode"]
temp_file_delete = configuration["report"]["temp_file_delete"]
date_format = configuration["report"]["date_format"]
report_download_format = configuration["report"]["report_download_format"]
use_gzip_compression = configuration["report"]["use_gzip_compression"]
report_config_keys = configuration["report"]["config_keys"]
json_schema = configuration["report"]["json_schema"]
supported_sync_modes = configuration["stream"]["supported_sync_modes"] 
source_defined_cursor = configuration["stream"]["source_defined_cursor"]
default_cursor_field = configuration["stream"]["default_cursor_field"] 



class GoogleAdManagerStreamState(BaseModel):
    state_date: str
    start_chunk_index: int


class SourceGoogleAdManager(Source):

    def check(self, logger: logging.Logger, config: json) -> AirbyteConnectionStatus:
        try:
            start_date = datetime.strptime(config["startDate"], "%Y-%m-%d")
            end_date = datetime.strptime(config["endDate"], "%Y-%m-%d")
            if start_date > end_date:
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"start_date ({config['startDate']}) cannot be greater than end_date ({config['endDate']})."
                )
            ad_manager_client = create_ad_manager_client(config=config, scopes=scopes, application_name=application_name)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: logging.Logger, config: json) -> AirbyteCatalog:
        streams = []

        streams.append(AirbyteStream(name=stream_name, json_schema=json_schema, supported_sync_modes=supported_sync_modes,
                                     source_defined_cursor=source_defined_cursor, default_cursor_field=default_cursor_field))
        return AirbyteCatalog(streams=streams)

    def read(self, logger: logging.Logger, config: json,  catalog: ConfiguredAirbyteCatalog, state: Dict[str, Any]) -> Generator[AirbyteMessage, None, None]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        ad_manager_client = create_ad_manager_client(config=config, scopes=scopes, application_name=application_name)
        report_downloader = ad_manager_client.GetDataDownloader(version='v202502')

        update_report_job_config(report_job, config, report_config_keys)

        selected_stream = next((cs for cs in catalog.streams if cs.stream.name == stream_name), None)
        state_date, start_chunk_index = get_state(state)
        today = datetime.now()
        start_date = get_start_date(state_date, config, today, selected_stream.sync_mode,date_format=date_format)
        end_date = get_end_date(today, config, selected_stream.sync_mode, date_format=date_format)
        if start_date > end_date:
            raise ValueError(f"start_date ({start_date}) cannot be greater than end_date ({end_date}).")

        for date in pd.date_range(start_date, end_date, freq='d'):
            report_job['reportQuery']['startDate'] = parse_date_to_dict(date)
            report_job['reportQuery']['endDate'] = parse_date_to_dict(date)

            report_job_id = report_downloader.WaitForReport(report_job=report_job)

            with tempfile.NamedTemporaryFile(mode=temp_file_mode, delete=temp_file_delete) as temp_file:
                report_downloader.DownloadReportToFile(report_job_id, report_download_format, temp_file, use_gzip_compression=use_gzip_compression)
                temp_file.close()

                temp_file_size = os.path.getsize(temp_file.name)
                if temp_file_size > 0:
                    chunks = pd.read_csv(temp_file.name, chunksize=int(config.get('chunk_size')))
                    for chunk_index, df in enumerate(chunks):
                        if chunk_index < start_chunk_index:
                            continue
                        pd.set_option('display.max_columns', None)
                        for _, row in df.iterrows():
                            record = row.to_dict()
                            record_message = AirbyteRecordMessage(
                                stream=stream_name,
                                data={'DATE': date.strftime(date_format), 'record': record},
                                emitted_at=int(datetime.now().timestamp()) * 1000
                            )
                            yield AirbyteMessage(
                                type=Type.RECORD,
                                record=record_message
                            )
                        if selected_stream.sync_mode == SyncMode.incremental:

                            state_data = GoogleAdManagerStreamState(
                                state_date=date.strftime(date_format),
                                start_chunk_index=chunk_index)

                            stream_state = AirbyteStateMessage(
                                type=AirbyteStateType.STREAM,
                                stream=AirbyteStreamState(
                                    stream_descriptor=StreamDescriptor(name=stream_name, namespace="public"),
                                    stream_state=state_data
                                ))
                            yield AirbyteMessage(type=Type.STATE, state=stream_state)
                            logger.info(f"State updated to: {stream_state}")
                    start_chunk_index = 0
                else:
                    logger.error("Temporary report file is empty.")
                os.remove(temp_file.name)
            logger.info(f"Fetched data up to: {date.strftime(date_format)}")
