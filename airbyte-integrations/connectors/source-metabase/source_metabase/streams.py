#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from ast import literal_eval
from typing import Any, Iterable, Mapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams import IncrementalMixin


class MetabaseStream(HttpStream, ABC):
    def __init__(self, instance_api_url: str, **kwargs):
        super().__init__(**kwargs)
        self.instance_api_url = instance_api_url

    primary_key = "id"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    @property
    def url_base(self) -> str:
        return self.instance_api_url

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        result = response.json()
        yield from result


class IncrementalMetabaseStream(MetabaseStream, IncrementalMixin, ABC):
    _cursor_value = None

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: str(self._cursor_value)}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]


class Activity(MetabaseStream):
    def path(self, **kwargs) -> str:
        return "activity"


class Cards(MetabaseStream):
    def path(self, **kwargs) -> str:
        return "card"


class Collections(MetabaseStream):
    def path(self, **kwargs) -> str:
        return "collection"


class Dashboards(MetabaseStream):
    def path(self, **kwargs) -> str:
        return "dashboard"


class DatasetQueryViews(IncrementalMetabaseStream):
    cursor_field = "viewed_on"
    http_method = "POST"
    page_size = 10000
    page_offset = 0

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data_result = response.json().get("data", [])
        rows_result = data_result.get("rows", [])
        header = [
            "viewed_on",
            "card_id",
            "card_name",
            "query_hash",
            "type",
            "collection_id",
            "collection",
            "viewed_by_id",
            "viewed_by",
            "saved_by_id",
            "saved_by",
            "database_id",
            "source_db",
            "table_id",
            "table"
        ]
        row_num = 0
        for row in literal_eval(str(rows_result)):
            result = {}
            for i in range(len(header)):
                result[header[i]] = row[i]
            result['page_offset'] = self.page_offset + row_num
            row_num += 1
            yield result

    def path(self, **kwargs) -> str:
        return "dataset"

    def request_body_json(self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs) -> Optional[Mapping]:
        payload = {
            "offset": self.page_offset,
            "limit": self.page_size,
            "type": "internal",
            "fn": "metabase-enterprise.audit-app.pages.users/query-views",
            "args": [],
            "parameters": []
        }
        return payload

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        try:
            max_viewed_on = None
            for row in self.parse_response(response):
                if not max_viewed_on or row[self.cursor_field] >= max_viewed_on:
                    max_viewed_on = row[self.cursor_field]
        except StopIteration:
            return None
        current_state = literal_eval(str(self.state))
        if not current_state or not literal_eval(str(current_state[self.cursor_field])):
            # No state set yet, get all pages
            if max_viewed_on:
                # return a value if we still have data being pulled
                result = "initial_sync"
            else:
                # No more data, stop retrieving pages
                result = None
        elif max_viewed_on >= literal_eval(str(current_state[self.cursor_field])):
            result = max_viewed_on
        else:
            result = None
        if result:
            self.page_offset += self.page_size
        return result


class Snippets(MetabaseStream):
    def path(self, **kwargs) -> str:
        return "native-query-snippet"


class Users(MetabaseStream):
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        result = response.json().get("data", [])
        print(f"Extracted {result}")
        yield from result

    def path(self, **kwargs) -> str:
        return "user"
