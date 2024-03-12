#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.test.mock_http.request import HttpRequest

from .config import ACCESS_TOKEN, ACCOUNT_ID


def get_account_request(account_id: Optional[str] = ACCOUNT_ID) -> RequestBuilder:
    return RequestBuilder.get_account_endpoint(access_token=ACCESS_TOKEN, account_id=account_id)


class RequestBuilder:

    @classmethod
    def get_account_endpoint(cls, access_token: str, account_id: str) -> RequestBuilder:
        return cls(access_token=access_token).with_account_id(account_id)

    @classmethod
    def get_videos_endpoint(cls, access_token: str, account_id: str) -> RequestBuilder:
        return cls(access_token=access_token, resource="advideos").with_account_id(account_id)

    @classmethod
    def get_insights_endpoint(cls, access_token: str, account_id: str) -> RequestBuilder:
        return cls(access_token=access_token, resource="insights").with_account_id(account_id)

    @classmethod
    def get_execute_batch_endpoint(cls, access_token: str) -> RequestBuilder:
        return cls(access_token=access_token)

    @classmethod
    def get_insights_download_endpoint(cls, access_token: str, job_id: str) -> RequestBuilder:
        return cls(access_token=access_token, resource=f"{job_id}/insights")

    def __init__(self, access_token: str, resource: Optional[str] = "") -> None:
        self._account_id = None
        self._resource = resource
        self._query_params = {"access_token": access_token}
        self._body = None

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

    def with_next_page_token(self, next_page_token: str) -> RequestBuilder:
        self._query_params["after"] = next_page_token
        return self

    def with_body(self, body: Union[str, bytes, Mapping[str, Any]]) -> RequestBuilder:
        self._body = body
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"https://graph.facebook.com/v19.0/{self._account_sub_path()}{self._resource}",
            query_params=self._query_params,
            body=self._body,
        )

    def _account_sub_path(self) -> str:
        return f"act_{self._account_id}/" if self._account_id else ""

    @staticmethod
    def _get_formatted_fields(fields: List[str]) -> str:
        return ",".join(fields)
