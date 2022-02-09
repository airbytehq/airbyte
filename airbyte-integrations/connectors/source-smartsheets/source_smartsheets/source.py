#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
# ws version


import json
from datetime import datetime
from typing import Any, Dict, Generator

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

# helpers
from airbyte_cdk.sources import Source


def get_prop(col_type: str) -> Dict[str, any]:
    props = {
        "TEXT_NUMBER": {"type": "string"},
        "DATE": {"type": "string", "format": "date"},
        "DATETIME": {"type": "string", "format": "date-time"},
    }
    if col_type in props.keys():
        return props[col_type]
    else:  # assume string
        return props["TEXT_NUMBER"]


def get_json_schema(sheet: Dict, config: json) -> Dict:
    # Get static metadata config options
    ss_add_row_id = config["smartsheets_add_row_id"]
    ss_add_row_extended_meta = config["smartsheets_add_row_extended_metadata"]
    ss_add_sheet_id = config["smartsheets_add_sheet_id"]
    ss_add_sheet_extended_meta = config["smartsheets_add_sheet_extended_metadata"]
    ss_add_workspace_id = config["smartsheets_add_workspace_id"]

    # Get Dynamic schema items from sheet columns.
    column_info = {i["title"]: get_prop(i["type"]) for i in sheet["columns"]}
    # Add static schema items.
    if bool(ss_add_row_id):
        column_info['_ss_row_id'] = {"type":"integer"} # Add Row ID to returned dynamic schema
    if bool(ss_add_row_extended_meta):
        column_info['_ss_row_created_at'] = {"type":"string"} # Row created at timestamp
        column_info['_ss_row_modified_at'] = {"type":"string"} # Row Modified at timestamp
        column_info['_ss_row_number'] = {"type":"string"} # Row number (changes with sort)
        column_info['_ss_row_parent_id'] = {"type" : "integer"} # ID of parent Row (if any)
        column_info['_ss_row_sibling_id'] = {"type": "integer"} # ID of previous sibiling row at same level (if any)
    if bool(ss_add_sheet_id):
        column_info['_ss_sheet_id'] = {"type":"integer"} # Add Sheet ID to returned dynamic schema
        column_info['_ss_sheet_name'] = {"type":"string"} # Add Sheet Name to returned dynamic schema
    if bool(ss_add_sheet_extended_meta):
        column_info['_ss_sheet_version'] = {"type":"integer"} # Sheet saved version number
        column_info['_ss_sheet_permalink'] = {"type":"string"} # Sheet permalink URL
        column_info['_ss_sheet_created_at'] = {"type":"string"} # Sheet Created Timestamp
        column_info['_ss_sheet_modified_at'] = {"type":"string"} # Sheet Created Timestamp
    if bool(ss_add_workspace_id):
        column_info['_ss_workspace_id'] = {"type":"integer"} # Add Workspace ID
        column_info['_ss_workspace_name'] = {"type":"string"} # Add Workspace Name

    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": [],
        "properties": column_info,
    }
    return json_schema

def catch(d: dict) -> Any:
    if 'value' in d:
        return d['value']
    return ''

# main class definition
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
        smartsheets_debug_logging_enabled = config["smartsheets_debug_logging"]
        
        streams = []

        smartsheet_client = smartsheet.Smartsheet(access_token)
        try:
            sheet = smartsheet_client.Sheets.get_sheet(spreadsheet_id)
            sheet = json.loads(str(sheet))  # make it subscriptable
            sheet_json_schema = get_json_schema(sheet, config)

            logger.info(f"Running discovery on sheet: {sheet['name']} with {spreadsheet_id}")
            logger.info(f"DEBUG: Decoded JSON schema {sheet_json_schema}")
            stream = AirbyteStream(name=sheet["name"], json_schema=sheet_json_schema)
            streams.append(stream)
        except Exception as e:
            raise Exception(f"Could not run discovery: {str(e)}")
        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:

        # Get primary config options
        access_token = config["access_token"]
        spreadsheet_id = config["spreadsheet_id"]
        smartsheets_debug_logging = config["smartsheets_debug_logging"]
        smartsheets_debug_logging_row_limit = config["smartsheets_debug_logging_row_limit"]
        
        # Get static metadata config options
        ss_add_row_id = config["smartsheets_add_row_id"]
        ss_add_row_extended_meta = config["smartsheets_add_row_extended_metadata"]
        ss_add_sheet_id = config["smartsheets_add_sheet_id"]
        ss_add_sheet_extended_meta = config["smartsheets_add_sheet_extended_metadata"]
        ss_add_workspace_id = config["smartsheets_add_workspace_id"]
        # Set access token in smartsheets client
        smartsheet_client = smartsheet.Smartsheet(access_token)

        for configured_stream in catalog.streams:
            stream = configured_stream.stream
            properties = stream.json_schema["properties"]
            if isinstance(properties, list):
                columns = tuple(key for dct in properties for key in dct.keys())
            elif isinstance(properties, dict):
                columns = tuple(i for i in properties.keys())
            else:
                logger.error("Could not read properties from the JSONschema in this stream")
            name = stream.name

            try:
                sheet = smartsheet_client.Sheets.get_sheet(spreadsheet_id)
                sheet = json.loads(str(sheet))  # make it subscriptable
                logger.info(f"Starting syncing spreadsheet {sheet['name']}")
                if bool(smartsheets_debug_logging):
                    logger.info(f"DEBUG: Configured JSON schema {properties}")
                logger.info(f"Row count: {sheet['totalRowCount']}")
                k = 1 # Reset Debug limit row counter

                for row in sheet["rows"]:
                    try:
                        id_name_map = {d['id']: d['title'] for d in sheet['columns']}
                        data = {id_name_map[i['columnId']]: catch(i) for i in row['cells']}
                    
                        if bool(ss_add_row_id):
                            data['_ss_row_id'] = row['id']
                        if bool(ss_add_row_extended_meta):
                            data['_ss_row_created_at'] = row['createdAt']
                            data['_ss_row_modified_at'] = row['modifiedAt']
                            data['_ss_row_number'] = row['rowNumber']
                            try:
                                data['_ss_row_parent_id'] = row['parentId']
                            except:
                                data['_ss_row_parent_id'] = None
                            try:
                                data['_ss_row_sibling_id'] = row['siblingId']
                            except:
                                data['_ss_row_sibling_id'] = None
                        if bool(ss_add_sheet_id):
                            data['_ss_sheet_id'] = sheet['id']
                            data['_ss_sheet_name'] = sheet['name']
                        if bool(ss_add_sheet_extended_meta):    
                            data['_ss_sheet_permalink'] = sheet['permalink']
                            data['_ss_sheet_created_at'] = sheet['createdAt']
                            data['_ss_sheet_modified_at'] = sheet['modifiedAt']
                            data['_ss_sheet_version'] = sheet['version']
                        if bool(ss_add_workspace_id):
                            try:                        
                                data['_ss_workspace_id'] = sheet['workspace']['id']
                            except:
                                data['_ss_workspace_id'] = None
                        
                            try:
                                data['_ss_workspace_name'] = sheet['workspace']['name']
                            except:
                                data['_ss_workspace_name'] = ""

                        if bool(smartsheets_debug_logging):
                            if (k <= smartsheets_debug_logging_row_limit):
                                logger.info(f"SOURCE SETTINGS DEBUG: Airbyte Row # {k}, SS Row ID: {row['id']} - Row Data: {data}")
                                k = k+1
                                                       
                        yield AirbyteMessage(
                            type=Type.RECORD,
                            record=AirbyteRecordMessage(stream=name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                        )
                    except Exception as e:
                        logger.error(f"Unable to encode row into an AirbyteMessage with the following error: {e}")
                        logger.error(f"Source Schema may be out of date.  Please update latest source schema in connection settings.")
                        raise

            except Exception as e:
                logger.error(f"Could not read smartsheet: {name}")
                raise e
        logger.info(f"Finished syncing spreadsheet with ID: {spreadsheet_id}")