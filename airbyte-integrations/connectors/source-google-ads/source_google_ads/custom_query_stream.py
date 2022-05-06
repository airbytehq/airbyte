#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import re
from functools import lru_cache
from typing import Any, Dict, List, Mapping

from .streams import IncrementalGoogleAdsStream


class CustomQuery(IncrementalGoogleAdsStream):
    def __init__(self, custom_query_config, **kwargs):
        self.custom_query_config = custom_query_config
        self.user_defined_query = custom_query_config["query"]
        super().__init__(**kwargs)

    @property
    def primary_key(self) -> str:
        """
        The primary_key option is disabled. Config should not provide the primary key.
        It will be ignored if provided.
        If you need to enable it, uncomment the next line instead of `return None` and modify your config
        """
        # return self.custom_query_config.get("primary_key") or None
        return None

    @property
    def name(self):
        return self.custom_query_config["table_name"]

    def get_query(self, stream_slice: Mapping[str, Any] = None) -> str:
        start_date, end_date = stream_slice.get("start_date"), stream_slice.get("end_date")
        return self.insert_segments_date_expr(self.user_defined_query, start_date, end_date)

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
        }
        fields = CustomQuery.get_query_fields(self.user_defined_query)
        fields.append(self.cursor_field)
        google_schema = self.google_ads_client.get_fields_metadata(fields)

        for field in fields:
            node = google_schema.get(field)
            # Data type return in enum format: "GoogleAdsFieldDataType.<data_type>"
            google_data_type = str(node.data_type).replace("GoogleAdsFieldDataType.", "")
            if google_data_type == "ENUM":
                field_value = {"type": "string", "enum": list(node.enum_values)}
            elif google_data_type == "MESSAGE":
                # Represents protobuf message and could be anything, set custom
                # attribute "protobuf_message" to convert it to a string (or
                # array of strings) later.
                # https://developers.google.com/google-ads/api/reference/rpc/v8/GoogleAdsFieldDataTypeEnum.GoogleAdsFieldDataType?hl=en#message
                if node.is_repeated:
                    output_type = ["array", "null"]
                else:
                    output_type = ["string", "null"]
                field_value = {"type": output_type, "protobuf_message": True}
            else:
                output_type = [google_datatype_mapping.get(google_data_type, "string"), "null"]
                field_value = {"type": output_type}
                if google_data_type == "DATE":
                    field_value["format"] = "date"

            local_json_schema["properties"][field] = field_value

        return local_json_schema

    # Regexp flags for parsing GAQL query
    RE_FLAGS = re.DOTALL | re.MULTILINE | re.IGNORECASE
    # Regexp for getting query columns
    SELECT_EXPR = re.compile("select(.*)from", flags=RE_FLAGS)
    WHERE_EXPR = re.compile("where.*", flags=RE_FLAGS)
    # list of keywords that can come after WHERE clause,
    # according to https://developers.google.com/google-ads/api/docs/query/grammar
    KEYWORDS_EXPR = re.compile("(order by|limit|parameters)", flags=RE_FLAGS)

    @staticmethod
    def get_query_fields(query: str) -> List[str]:
        fields = CustomQuery.SELECT_EXPR.search(query)
        if not fields:
            return []
        fields = fields.group(1)
        return [f.strip() for f in fields.split(",")]

    @staticmethod
    def insert_segments_date_expr(query: str, start_date: str, end_date: str) -> str:
        """
        Insert segments.date condition to break query into slices for incremental stream.
        :param query Origin user defined query
        :param start_date start date for metric (inclusive)
        :param end_date end date for metric (inclusive)
        :return Modified query with date window condition included
        """
        # insert segments.date field
        columns = CustomQuery.SELECT_EXPR.search(query)
        if not columns:
            raise Exception("Not valid GAQL expression")
        columns = columns.group(1)
        new_columns = columns + ", segments.date\n"
        result_query = query.replace(columns, new_columns)

        # Modify/insert where condition
        where_cond = CustomQuery.WHERE_EXPR.search(result_query)
        if not where_cond:
            # There is no where condition, insert new one
            where_location = len(result_query)
            keywords = CustomQuery.KEYWORDS_EXPR.search(result_query)
            if keywords:
                # where condition is not at the end of expression, insert new condition before keyword begins.
                where_location = keywords.start()
            result_query = (
                result_query[0:where_location]
                + f"\nWHERE segments.date BETWEEN '{start_date}' AND '{end_date}'\n"
                + result_query[where_location:]
            )
            return result_query
        # There is already where condition, add segments.date expression
        where_cond = where_cond.group(0)
        keywords = CustomQuery.KEYWORDS_EXPR.search(where_cond)
        if keywords:
            # There is some keywords after WHERE condition
            where_cond = where_cond[0 : keywords.start()]
        new_where_cond = where_cond + f" AND segments.date BETWEEN '{start_date}' AND '{end_date}'\n"
        result_query = result_query.replace(where_cond, new_where_cond)
        return result_query
