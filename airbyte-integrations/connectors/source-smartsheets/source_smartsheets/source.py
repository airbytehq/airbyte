#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Dict, Generator, List

import smartsheet
from airbyte_cdk import AirbyteLogger
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


def get_prop(col_type: str) -> Dict[str, any]:
    props = {
        "TEXT_NUMBER": {"type": "string"},
        "DATE": {"type": "string", "format": "date"},
        "DATETIME": {"type": "string", "format": "date-time"},
    }
    return props.get(col_type, {"type": "string"})


def construct_record(sheet_columns: List[Dict], row_cells: List[Dict]) -> Dict:
    # convert all data to string as it is only expected format in schema
    values_column_map = {cell["columnId"]: str(cell.get("value", "")) for cell in row_cells}
    return {column["title"]: values_column_map[column["id"]] for column in sheet_columns}


def get_json_schema(sheet_columns: List[Dict]) -> Dict:
    column_info = {column["title"]: get_prop(column["type"]) for column in sheet_columns}
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": column_info,
    }
    return json_schema


class SourceSmartsheets(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        try:
            access_token = config["access_token"]
            spreadsheet_id = config["spreadsheet_id"]

            smartsheet_client = smartsheet.Smartsheet(access_token)
            smartsheet_client.errors_as_exceptions(True)
            smartsheet_client.Sheets.get_sheet(spreadsheet_id)

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            if isinstance(e, smartsheet.exceptions.ApiError):
                err = e.error.result
                code = 404 if err.code == 1006 else err.code
                reason = f"{err.name}: {code} - {err.message} | Check your spreadsheet ID."
            else:
                reason = str(e)
            logger.error(reason)
        return AirbyteConnectionStatus(status=Status.FAILED)

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        access_token = config["access_token"]
        spreadsheet_id = config["spreadsheet_id"]
        streams = []

        smartsheet_client = smartsheet.Smartsheet(access_token)
        try:
            sheet = smartsheet_client.Sheets.get_sheet(spreadsheet_id)
            sheet = json.loads(str(sheet))  # make it subscriptable
            sheet_json_schema = get_json_schema(sheet["columns"])
            logger.info(f"Running discovery on sheet: {sheet['name']} with {spreadsheet_id}")

            stream = AirbyteStream(name=sheet["name"], json_schema=sheet_json_schema)
            stream.supported_sync_modes = ["full_refresh"]
            streams.append(stream)

        except Exception as e:
            raise Exception(f"Could not run discovery: {str(e)}")

        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:

        access_token = config["access_token"]
        spreadsheet_id = config["spreadsheet_id"]
        smartsheet_client = smartsheet.Smartsheet(access_token)

        for configured_stream in catalog.streams:
            stream = configured_stream.stream
            try:
                sheet = smartsheet_client.Sheets.get_sheet(spreadsheet_id)
                sheet = json.loads(str(sheet))  # make it subscriptable
                logger.info(f"Starting syncing spreadsheet {sheet['name']}")
                logger.info(f"Row count: {sheet['totalRowCount']}")

                for row in sheet["rows"]:
                    try:
                        record = construct_record(sheet["columns"], row["cells"])
                        yield AirbyteMessage(
                            type=Type.RECORD,
                            record=AirbyteRecordMessage(stream=stream.name, data=record, emitted_at=int(datetime.now().timestamp()) * 1000),
                        )
                    except Exception as e:
                        logger.error(f"Unable to encode row into an AirbyteMessage with the following error: {e}")

            except Exception as e:
                logger.error(f"Could not read smartsheet: {stream.name}")
                raise e
        logger.info(f"Finished syncing spreadsheet with ID: {spreadsheet_id}")
