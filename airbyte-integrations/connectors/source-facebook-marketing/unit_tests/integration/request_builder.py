#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from typing import List, Optional

from airbyte_cdk.test.mock_http.request import HttpRequest

from .pagination import CURSOR_AFTER


class RequestBuilder:

    @classmethod
    def get_account_endpoint(cls, account_id: str, access_token: str) -> RequestBuilder:
        return cls(account_id=account_id, access_token=access_token)

    @classmethod
    def get_videos_endpoint(cls, account_id: str, access_token: str) -> RequestBuilder:
        return cls(account_id=account_id, access_token=access_token, resource="advideos")

    @classmethod
    def get_insights_endpoint(cls, account_id: str, access_token: str) -> RequestBuilder:
        return cls(account_id=account_id, access_token=access_token, resource="insights")

    def __init__(self, account_id: str, access_token: str, resource: Optional[str] = "") -> None:
        self._account_id = account_id
        self._resource = resource
        self._query_params = {"access_token": access_token}

    def with_account_id(self, account_id: str) -> RequestBuilder:
        self._account_id = account_id
        return self

    def with_limit(self, limit: int) -> RequestBuilder:
        self._query_params["limit"] = limit
        return self

    def with_summary(self) -> RequestBuilder:
        self._query_params["summary"] = "true"
        return self

    def with_fields(self, fields: List[str]) -> RequestBuilder:
        self._query_params["fields"] = self._get_formatted_fields(fields)
        return self

    def with_pagination_parameter(self) -> RequestBuilder:
        self._query_params["after"] = CURSOR_AFTER
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(url=f"https://graph.facebook.com/v17.0/act_{self._account_id}/{self._resource}", query_params=self._query_params)

    @staticmethod
    def _get_formatted_fields(fields: List[str]) -> str:
        return ",".join(fields)
