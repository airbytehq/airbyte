#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from functools import lru_cache
from typing import Any, Dict, List, Mapping, MutableMapping

from .streams import GoogleAdsStream, IncrementalGoogleAdsStream
from .utils import GAQL


logger = logging.getLogger("airbyte")


DATE_TYPES = ("segments.date", "segments.month", "segments.quarter", "segments.week")


class CustomQueryMixin:
    def __init__(self, config, **kwargs):
        self.config = config
        super().__init__(**kwargs)

    @property
    def primary_key(self) -> str:
        """
        The primary_key option is disabled. Config should not provide the primary key.
        It will be ignored if provided.
        If you need to enable it, uncomment the next line instead of `return None` and modify your config
        """
        # return self.config.get("primary_key") or None
        return None

    @property
    def name(self):
        return self.config["table_name"]

    # IncrementalGoogleAdsStream uses get_json_schema a lot while parsing
    # responses, caching playing crucial role for performance here.
    @lru_cache()
    def get_json_schema(self) -> Dict[str, Any]:
        """
        Compose json schema based on user defined query.
        :return Dict object representing jsonschema
        """

        local_json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }
        # full list {'ENUM', 'STRING', 'DATE', 'DOUBLE', 'RESOURCE_NAME', 'INT32', 'INT64', 'BOOLEAN', 'MESSAGE'}

        google_datatype_mapping = {
            "INT64": "integer",
            "INT32": "integer",
            "DOUBLE": "number",
            "STRING": "string",
            "BOOLEAN": "boolean",
            "DATE": "string",
            "MESSAGE": "string",
            "ENUM": "string",
        }
        fields = list(self.config["query"].fields)
        if self.cursor_field:
            fields.append(self.cursor_field)
        google_schema = self.google_ads_client.get_fields_metadata(fields)

        for field in fields:
            node = google_schema.get(field)
            # Data type return in enum format: "GoogleAdsFieldDataType.<data_type>"
            google_data_type = node.data_type.name
            field_value = {"type": [google_datatype_mapping.get(google_data_type, "string"), "null"]}

            # Google Ads doesn't differentiate between DATE and DATETIME, so we need to manually check for fields with known type
            if google_data_type == "DATE" and field in DATE_TYPES:
                field_value["format"] = "date"

            if google_data_type == "ENUM":
                field_value = {"type": "string", "enum": list(node.enum_values)}

            if node.is_repeated:
                field_value = {"type": ["null", "array"], "items": field_value}

            local_json_schema["properties"][field] = field_value

        return local_json_schema


class IncrementalCustomQuery(CustomQueryMixin, IncrementalGoogleAdsStream):
    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        """
        Check if state needs migration from CDK v7 concurrent format to legacy format.

        CDK v7 concurrent format has "states" key with array of partition states.
        Legacy format has customer_id keys directly: {customer_id: {cursor}}
        """
        return bool(stream_state and "states" in stream_state)

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Migrate CDK v7 concurrent state format to legacy format.

        CDK v7 concurrent format:
        {
          "states": [{"cursor": {...}, "partition": {"customer_id": "customers/123", ...}}],
          "state": {...}
        }

        Legacy format:
        {"123": {"segments.date": "2025-12-20"}}
        """
        if not self.should_migrate(stream_state):
            return stream_state

        # Convert from concurrent to legacy format
        legacy_state = {}
        for partition_state in stream_state.get("states", []):
            cursor = partition_state.get("cursor", {})
            partition = partition_state.get("partition", {})
            customer_id_full = partition.get("customer_id", "")

            if customer_id_full and cursor:
                # Extract customer_id without "customers/" prefix
                customer_id = customer_id_full.replace("customers/", "") if customer_id_full.startswith("customers/") else customer_id_full
                legacy_state[customer_id] = cursor

        return legacy_state

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """
        Override state setter to automatically migrate CDK v7 concurrent state format.
        """
        if self.should_migrate(value):
            value = self.migrate(value)
        self._state.update(value)

    def get_query(self, stream_slice: Mapping[str, Any] = None) -> str:
        start_date, end_date = stream_slice["start_date"], stream_slice["end_date"]
        query = self.insert_segments_date_expr(self.config["query"], start_date, end_date)
        return str(query)

    @staticmethod
    def insert_segments_date_expr(query: GAQL, start_date: str, end_date: str) -> GAQL:
        """
        Insert segments.date condition to break query into slices for incremental stream.
        :param query Origin user defined query
        :param start_date start date for metric (inclusive)
        :param end_date end date for metric (inclusive)
        :return Modified query with date window condition included
        """
        if "segments.date" not in query.fields:
            query = query.append_field("segments.date")
        condition = f"segments.date BETWEEN '{start_date}' AND '{end_date}'"
        if query.where:
            return query.set_where(query.where + " AND " + condition)
        return query.set_where(condition)


class CustomQuery(CustomQueryMixin, GoogleAdsStream):
    def get_query(self, stream_slice: Mapping[str, Any] = None) -> str:
        return str(self.config["query"])
