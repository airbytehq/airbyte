#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import re
from typing import Any, Iterable, List, Mapping, Optional

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

    @property
    def cursor_field(self) -> str:
        """
        The incremental is disabled. Config / spec should not provide the cursor_field.
        It will be ignored if provided.
        However, this return should be kept for case we wanna support it.
        Disabled cursor_field should be always empty array or string, to keep the internal logic
            (get length of cursor_field).
        Since it is not provided, the stream will be full refresh anyway.
        The inheritance from the Incremental stream is made for supporting both types,
            and need to be kept.
        If you need to enable this option, uncomment the first return and modify your config
        """
        # return self.custom_query_config.get("cursor_field") or []
        return []

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        if not self.cursor_field:
            return [None]
        return super().stream_slices(stream_state=stream_state, **kwargs)

    def get_query(self, stream_slice: Mapping[str, Any] = None) -> str:
        if not self.cursor_field:
            return self.user_defined_query
        start_date, end_date = self.get_date_params(stream_slice, self.cursor_field)
        final_query = (
            self.user_defined_query
            + f"\nWHERE {self.cursor_field} > '{start_date}' AND {self.cursor_field} < '{end_date}' ORDER BY {self.cursor_field} ASC"
        )
        return final_query

    def get_json_schema(self):
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
        ga_field_service = self.google_ads_client.client.get_service("GoogleAdsFieldService")
        request = self.google_ads_client.client.get_type("SearchGoogleAdsFieldsRequest")
        request.page_size = len(fields)
        fields_sql = ",".join([f"'{field}'" for field in fields])
        request.query = f"""
        SELECT
          name,
          data_type,
          enum_values
        WHERE name in ({fields_sql})
        """
        response = ga_field_service.search_google_ads_fields(request=request)
        google_schema = {r.name: r for r in response}

        for field in fields:
            node = google_schema.get(field)
            # Data type return in enum format: "GoogleAdsFieldDataType.<data_type>"
            google_data_type = str(node.data_type).replace("GoogleAdsFieldDataType.", "")
            if google_data_type == "ENUM":
                field_value = {"type": "string", "enum": list(node.enum_values)}
            elif google_data_type == "MESSAGE":  # this can be anything (or skip as additionalproperties) ?
                output_type = ["string", "number", "array", "object", "boolean", "null"]
                field_value = {"type": output_type}
            else:
                output_type = [google_datatype_mapping.get(google_data_type, "string"), "null"]
                field_value = {"type": output_type}
            local_json_schema["properties"][field] = field_value

        return local_json_schema

    @staticmethod
    def get_query_fields(query: str) -> List[str]:
        re_flags = re.DOTALL | re.MULTILINE | re.IGNORECASE
        select_re = re.compile("select(.*)from", flags=re_flags)
        fields = select_re.search(query)
        if not fields:
            return []
        fields = fields.group(1)
        return [f.strip() for f in fields.split(",")]
