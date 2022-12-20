#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from asyncio import streams
from distutils.command.config import config
import urllib.parse
from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional
import json
from attr import field
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Tuple
from genson import SchemaBuilder
from dateutil import parser


class RocksetStream(HttpStream, ABC):
    url_base = None

    def __init__(self, workspace: str, name: str, api_token: str, start_date: str, region_url: str, **kwargs):
        super().__init__(**kwargs)
        print("  name ", name)
        self.table = name
        self.workspace = workspace
        self.api_token = api_token
        self.start_date = start_date
        self._state = {}
        self.url_base = "https://{}.rockset.com/v1/orgs/self/queries/".format(
            region_url)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(
        self,
        response: requests.post,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        return [response.json()]


# class IncrementalRocksetStream(RocksetStream):
#     cursor_field = "WHENMODIFIED"
#     filter_date = None

#     @property
#     def state(self) -> Mapping[str, Any]:
#         if not self._state:
#             self._state = {self.cursor_field: parser.parse(
#                 self.start_date).strftime('%Y-%m-%d')}
#         return self._state

#     @state.setter
#     def state(self, value: Mapping[str, Any]):
#         self._state = value

#     def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
#         for record in super().read_records(*args, **kwargs):
#             current_cursor_value = parser.parse(
#                 self.state[self.cursor_field])
#             latest_cursor_value = parser.parse(
#                 record[self.cursor_field])
#             new_cursor_value = max(latest_cursor_value, current_cursor_value)
#             self.state = {
#                 self.cursor_field: new_cursor_value.strftime('%Y-%m-%d')}
#             yield record


class Workspace_new(RocksetStream):
    http_method = "post"
    # This stream is primarily used for connnection checking.
    primary_key = "id"

    query_id = None

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        """
        Override when creating POST requests to populate the body of the request with a non-JSON payload.
        """
        # last_modified = stream_state.get(self.cursor_field, self.start_date)
        # last_modified = parser.parse(last_modified).strftime('%m-%d-%Y')
        # if (self.filter_date == None):
        #     self.filter_date = last_modified
        print("workspace and table names")
        print(self.workspace, self.table)
        return {
            "sql": {
                "query": "SELECT * FROM {}.{} WHERE {}._event_time > PARSE_DATE_ISO8601('{}') ".format(self.workspace, self.table, self.table, self.start_date),
                "generate_warnings": "true",
                "paginate": "true",
                "initial_paginate_response_doc_count": 10000


            },

        }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_body = response.json()
        response = response_body.get('pagination', {})
        print(response)
        # self.query_id = self.query_id or response_body.get('query_id', None)
        next_cursor = response.get("next_page_link", None)
        print({
            "next_cursor": next_cursor,

        })

        if (next_cursor):
            return {
                "next_cursor": next_cursor,

            }
        return None

    @property
    def name(self) -> str:
        return self.table

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        params = {

            "next_cursor": None,

        }
        print('#############url basee')
        print(self.url_base)

        if next_page_token:
            params.update(next_page_token)
        if (params["next_cursor"]):
            self.url_base = params["next_cursor"]

        return ''

    def parse_response(self, response: requests.post, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Iterable[Mapping]:
        data = response.json()
        print(len(data["results"]))
        # return []
        for item in data.get("results", []):
            yield item

    def get_json_schema(self):

        url_schema = self.url_base
        print("this is url schema")
        print(url_schema)

        payload = json.dumps({
            "sql": {
                "query": " DESCRIBE {}.{} ".format(self.workspace, self.table),
                "generate_warnings": "true",
                "paginate": "true",
                "initial_paginate_response_doc_count": "10000"
            }
        })
        headers = {
            'Authorization': 'ApiKey {}'.format(self.api_token),
            'Content-Type': 'application/json'
        }
        response = requests.request(
            "POST", url_schema, headers=headers, data=payload)
        print(response.json())
        print("this is the table name")
        print(self.table)
        jsonresponse = response.json()
        # builder = SchemaBuilder()
        properties = {}
        # builder.add_schema({"type": "object", "properties": {}})

        for items in jsonresponse.get("results", [{}]):
            print("this is items ######")
            print(items)
            if len(items["field"]) != 1:
                continue

            key = items["field"][0]
            data_type = items["type"]
            obj = {
                "type": ["string", "null"],
            }

            properties[key] = {}

            if data_type == "object":

                properties[key] = obj
                properties[key]["type"] = "object"

                properties[key]["properties"] = {}

            elif data_type == "array":
                properties[key] = obj
                properties[key]["type"] = "array"

                properties[key]["items"] = {}

            else:
                properties[key] = obj
        print({"type": "object", "properties": properties})
        return {"$schema": "http://json-schema.org/draft-04/schema#", "type": "object", "properties": properties}
