#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import List, Optional, Union

from source_instagram.source import SourceInstagram

from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest
from airbyte_cdk.test.mock_http.request import HttpRequest

from .config import ACCOUNTS_FIELDS


GRAPH_URL = resolve_manifest(source=SourceInstagram()).record.data["manifest"]["definitions"]["base_requester"]["url_base"]


def get_account_request() -> RequestBuilder:
    return RequestBuilder.get_account_endpoint().with_limit(100)


class RequestBuilder:
    @classmethod
    def get_account_endpoint(cls) -> RequestBuilder:
        return cls(resource="me/accounts").with_fields(ACCOUNTS_FIELDS)

    @classmethod
    def get_media_endpoint(cls, item_id: str) -> RequestBuilder:
        return cls(resource="media").with_item_id(item_id)

    @classmethod
    def get_media_children_endpoint(cls, item_id: str) -> RequestBuilder:
        return cls().with_item_id(item_id).with_item_id_is_sub_path(False)

    @classmethod
    def get_media_insights_endpoint(cls, item_id: str) -> RequestBuilder:
        return cls(resource="insights").with_item_id(item_id)

    @classmethod
    def get_stories_endpoint(cls, item_id: str) -> RequestBuilder:
        return cls(resource="stories").with_item_id(item_id)

    @classmethod
    def get_users_endpoint(cls, item_id: str) -> RequestBuilder:
        return cls().with_item_id(item_id).with_item_id_is_sub_path(False)

    @classmethod
    def get_user_lifetime_insights_endpoint(cls, item_id: str) -> RequestBuilder:
        return cls(resource="insights").with_item_id(item_id)

    def __init__(self, resource: Optional[str] = "") -> None:
        self._item_id = None
        self._resource = resource
        self._query_params = {}
        self._body = None
        self._item_id_is_sub_path = True

    def with_item_id(self, item_id: str) -> RequestBuilder:
        self._item_id = item_id
        return self

    def with_limit(self, limit: int) -> RequestBuilder:
        self._query_params["limit"] = limit
        return self

    def with_fields(self, fields: List[str]) -> RequestBuilder:
        self._query_params["fields"] = self._get_formatted_fields(fields)
        return self

    def with_next_page_token(self, next_page_token: str) -> RequestBuilder:
        self._query_params["after"] = next_page_token
        return self

    def with_item_id_is_sub_path(self, is_sub_path: bool):
        self._item_id_is_sub_path = is_sub_path
        return self

    def with_custom_param(self, param: str, value: Union[str, List[str]], with_format=False):
        if with_format and isinstance(value, List):
            value = self._get_formatted_fields(value)
        self._query_params[param] = value
        return self

    @staticmethod
    def _get_formatted_fields(fields: List[str]) -> str:
        return ",".join(fields)

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{GRAPH_URL}/{self._item_path()}{self._resource}",
            query_params=self._query_params,
            body=self._body,
        )

    def _item_path(self) -> str:
        path_for_resource = "/" if self._item_id_is_sub_path else ""
        return f"{self._item_id}{path_for_resource}" if self._item_id else ""
