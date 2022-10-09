#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from functools import cache
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

from .base import IncrementalMixpanelStream, MixpanelStream


class EngageSchema(MixpanelStream):
    """
    Engage helper stream for dynamic schema extraction.
    :: reqs_per_hour_limit: int - property is set to the value of 1 million,
       to get the sleep time close to the zero, while generating dynamic schema.
       When `reqs_per_hour_limit = 0` - it means we skip this limits.
    """

    primary_key: str = None
    data_field: str = "results"
    reqs_per_hour_limit: int = 0  # see the docstring

    def path(self, **kwargs) -> str:
        return "engage/properties"

    def process_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        response.json() example:
        {
            "results": {
                "$browser": {
                    "count": 124,
                    "type": "string"
                },
                "$browser_version": {
                    "count": 124,
                    "type": "string"
                },
                ...
                "_some_custom_property": {
                    "count": 124,
                    "type": "string"
                }
            }
        }
        """
        records = response.json().get(self.data_field, {})
        for property_name in records:
            yield {
                "name": property_name,
                "type": records[property_name]["type"],
            }


class Engage(IncrementalMixpanelStream):
    """Return list of all users
    API Docs: https://developer.mixpanel.com/reference/engage
    Endpoint: https://mixpanel.com/api/2.0/engage
    """

    http_method: str = "POST"
    data_field: str = "results"
    primary_key: str = "distinct_id"
    page_size: int = 1000  # min 100
    _total: Any = None
    cursor_field = "last_seen"

    @property
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def supports_incremental(self) -> bool:
        return True

    # enable automatic object mutation to align with desired schema before outputting to the destination
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def path(self, **kwargs) -> str:
        return "engage"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return {"include_all_users": True}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params = {**params, "page_size": self.page_size}
        if next_page_token:
            params.update(next_page_token)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        page_number = decoded_response.get("page")
        total = decoded_response.get("total")  # exist only on first page
        if total:
            self._total = total

        if self._total and page_number is not None and self._total > self.page_size * (page_number + 1):
            return {
                "session_id": decoded_response.get("session_id"),
                "page": page_number + 1,
            }
        else:
            self._total = None
            return None

    def process_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        {
            "page": 0
            "page_size": 1000
            "session_id": "1234567890-EXAMPL"
            "status": "ok"
            "total": 1
            "results": [{
                "$distinct_id": "9d35cd7f-3f06-4549-91bf-198ee58bb58a"
                "$properties":{
                    "$browser":"Chrome"
                    "$browser_version":"83.0.4103.116"
                    "$city":"Leeds"
                    "$country_code":"GB"
                    "$region":"Leeds"
                    "$timezone":"Europe/London"
                    "unblocked":"true"
                    "$email":"nadine@asw.com"
                    "$first_name":"Nadine"
                    "$last_name":"Burzler"
                    "$name":"Nadine Burzler"
                    "id":"632540fa-d1af-4535-bc52-e331955d363e"
                    "$last_seen":"2020-06-28T12:12:31"
                    ...
                    }
                },{
                ...
                }
            ]

        }
        """
        records = response.json().get(self.data_field, [])
        for record in records:
            item = {"distinct_id": record["$distinct_id"]}
            properties = record["$properties"]
            for property_name in properties:
                this_property_name = property_name
                if property_name.startswith("$"):
                    # Just remove leading '$' for 'reserved' mixpanel properties name, example:
                    # from API: '$browser'
                    # to stream: 'browser'
                    this_property_name = this_property_name[1:]
                item[this_property_name] = properties[property_name]
            item_cursor = item.get(self.cursor_field)
            state_cursor = stream_state.get(self.cursor_field)
            if not item_cursor or not state_cursor or item_cursor >= state_cursor:
                yield item

    @cache
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.

        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.
        """
        schema = super().get_json_schema()

        # Set whether to allow additional properties for engage and export endpoints
        # Event and Engage properties are dynamic and depend on the properties provided on upload,
        #   when the Event or Engage (user/person) was created.
        schema["additionalProperties"] = self.additional_properties

        types = {
            "boolean": {"type": ["null", "boolean"]},
            "number": {"type": ["null", "number"], "multipleOf": 1e-20},
            "datetime": {"type": ["null", "string"], "format": "date-time"},
            "object": {"type": ["null", "object"], "additionalProperties": True},
            "list": {"type": ["null", "array"], "required": False, "items": {}},
            "string": {"type": ["null", "string"]},
        }

        # read existing Engage schema from API
        schema_properties = EngageSchema(**self.get_stream_params()).read_records(sync_mode=SyncMode.full_refresh)
        for property_entry in schema_properties:
            property_name: str = property_entry["name"]
            property_type: str = property_entry["type"]
            if property_name.startswith("$"):
                # Just remove leading '$' for 'reserved' mixpanel properties name, example:
                # from API: '$browser'
                # to stream: 'browser'
                property_name = property_name[1:]
            # Do not overwrite 'standard' hard-coded properties, add 'custom' properties
            if property_name not in schema["properties"]:
                schema["properties"][property_name] = types.get(property_type, {"type": ["null", "string"]})

        return schema

    def set_cursor(self, cursor_field: List[str]):
        if not cursor_field:
            raise Exception("cursor_field is not defined")
        if len(cursor_field) > 1:
            raise Exception("multidimensional cursor_field is not supported")
        self.cursor_field = cursor_field[0]

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if sync_mode == SyncMode.incremental:
            self.set_cursor(cursor_field)
        return super().stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
