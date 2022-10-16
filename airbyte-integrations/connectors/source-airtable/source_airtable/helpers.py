#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict

import requests
from airbyte_cdk.models import AirbyteStream
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class Helpers(object):
    @staticmethod
    def get_first_row(auth: TokenAuthenticator, base_id: str, table: str) -> Dict[str, Any]:
        url = f"https://api.airtable.com/v0/{base_id}/{table}?pageSize=1"
        try:
            response = requests.get(url, headers=auth.get_auth_header())
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid API key")
            elif e.response.status_code == 404:
                raise Exception(f"Table '{table}' not found")
            else:
                raise Exception(f"Error getting first row from table {table}: {e}")
        json_response = response.json()
        record = json_response.get("records", [])[0]
        return record

    @staticmethod
    def get_json_schema(record: Dict[str, Any]) -> Dict[str, str]:
        fields = record.get("fields", {})
        properties = {
            "_airtable_id": {"type": ["null", "string"]},
            "_airtable_created_time": {"type": ["null", "string"]},
        }

        for field in fields:
            properties[field] = {"type": ["null", "string"]}

        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
        }
        return json_schema

    @staticmethod
    def get_airbyte_stream(table: str, json_schema: Dict[str, Any]) -> AirbyteStream:
        return AirbyteStream(
            name=table,
            json_schema=json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append_dedup],
        )
