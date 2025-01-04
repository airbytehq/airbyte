#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict

import requests

from airbyte_cdk.models import AirbyteStream
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class Helpers(object):
    base_url = "https://api.gridly.com/v1/"

    @staticmethod
    def view_detail_url(view_id: str) -> str:
        return Helpers.base_url + f"views/{view_id}"

    @staticmethod
    def view_list_url(grid_id: str) -> str:
        return Helpers.base_url + f"views?gridId={grid_id}"

    @staticmethod
    def grid_detail_url(grid_id: str) -> str:
        return Helpers.base_url + f"grids/{grid_id}"

    @staticmethod
    def get_views(auth: TokenAuthenticator, grid_id: str) -> Dict[str, Any]:
        url = Helpers.view_list_url(grid_id)
        try:
            response = requests.get(url, headers=auth.get_auth_header())
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid API Key")
            elif e.response.status_code == 404:
                raise Exception(f"Grid id '{grid_id}' not found")
            else:
                raise Exception(f"Error getting listing views of grid '{grid_id}'")

        return response.json()

    @staticmethod
    def get_grid(auth: TokenAuthenticator, grid_id: str) -> Dict[str, Any]:
        url = Helpers.grid_detail_url(grid_id)
        try:
            response = requests.get(url, headers=auth.get_auth_header())
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid API Key")
            elif e.response.status_code == 404:
                raise Exception(f"Grid '{grid_id}' not found")
            else:
                raise Exception(f"Error getting grid {grid_id}: {e}")
        return response.json()

    @staticmethod
    def get_view(auth: TokenAuthenticator, view_id: str) -> Dict[str, Any]:
        url = Helpers.view_detail_url(view_id)
        try:
            response = requests.get(url, headers=auth.get_auth_header())
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid API Key")
            elif e.response.status_code == 404:
                raise Exception(f"View '{view_id}' not found")
            else:
                raise Exception(f"Error getting view {view_id}: {e}")
        return response.json()

    @staticmethod
    def to_airbyte_data_type(column_type: str) -> str:
        if column_type == "number":
            return "number"
        elif column_type == "boolean":
            return "boolean"
        else:
            return "string"

    @staticmethod
    def get_json_schema(view: Dict[str, Any]) -> Dict[str, str]:
        columns = view.get("columns", {})
        properties = {}

        for column in columns:
            column_id = column.get("id")
            column_type = column.get("type", "singleLine")
            properties[column_id] = {"type": ["null", Helpers.to_airbyte_data_type(column_type)]}

        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
        }
        return json_schema

    @staticmethod
    def get_airbyte_stream(view: Dict[str, Any]) -> AirbyteStream:
        view_name = view.get("name")
        columns = view.get("columns", {})
        properties = {}

        for column in columns:
            column_id = column.get("id")
            column_type = column.get("type", "singleLine")
            properties[column_id] = {"type": ["null", Helpers.to_airbyte_data_type(column_type)]}

        json_schema = Helpers.get_json_schema(view)

        return AirbyteStream(
            name=view_name,
            json_schema=json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append_dedup],
        )

    @staticmethod
    def transform_record(record: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        schema_properties = schema.get("properties")
        columns = [k for k, v in schema_properties.items()]

        cells = record.get("cells")

        transformed_record = {}
        if "_recordId" in columns:
            transformed_record["_recordId"] = record.get("id")
        if "_path" in columns:
            transformed_record["_path"] = record.get("path", "")

        for cell in cells:
            transformed_record[cell.get("columnId")] = cell.get("value")

        return transformed_record
