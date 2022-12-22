#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict

from airbyte_cdk.models import AirbyteStream
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode


class Helpers:
    
    @staticmethod
    def clean_name(name_str: str) -> str:
        return name_str.replace(" ", "_").lower().strip()
        
    @staticmethod
    def get_json_schema(table: Dict[str, Any]) -> Dict[str, str]:
        fields = table.get("fields", {})
        properties = {
            "_airtable_id": {"type": ["null", "string"]},
            "_airtable_created_time": {"type": ["null", "string"]},
        }
        
        for field in fields:
            field_name = Helpers.clean_name(field.get("name"))
            properties[field_name] = {"type": ["null", "string"]}
            
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
