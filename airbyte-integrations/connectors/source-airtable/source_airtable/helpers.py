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
    def get_most_complete_row(auth: TokenAuthenticator, base_id: str, table: str, sample_size: int = 100) -> Dict[str, Any]:
        url = f"https://api.airtable.com/v0/{base_id}/{table}?pageSize={sample_size}"
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
        records = json_response.get("records", [])
        most_complete_row = records[0]
        for record in records:
            if len(record.keys()) > len(most_complete_row.keys()):
                most_complete_row = record
        return most_complete_row

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
