#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Any, Dict, Optional

from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS, HttpRequest

from .config import FOLDER_ID


GONG_API_URL = "https://api.gong.io/v2"


class RequestBuilder:
    @classmethod
    def workspaces_endpoint(cls) -> "RequestBuilder":
        return cls(resource="workspaces")

    @classmethod
    def call_transcripts_endpoint(cls) -> "RequestBuilder":
        return cls(resource="calls/transcript", http_method="POST")

    @classmethod
    def trackers_endpoint(cls) -> "RequestBuilder":
        return cls(resource="settings/trackers")

    @classmethod
    def library_folders_endpoint(cls) -> "RequestBuilder":
        return cls(resource="library/folders")

    @classmethod
    def library_folder_content_endpoint(cls, folder_id: str = FOLDER_ID) -> "RequestBuilder":
        builder = cls(resource="library/folder-content")
        builder.with_query_param("folderId", folder_id)
        return builder

    @classmethod
    def stats_activity_aggregate_endpoint(cls) -> "RequestBuilder":
        return cls(resource="stats/activity/aggregate", http_method="POST")

    @classmethod
    def stats_activity_day_by_day_endpoint(cls) -> "RequestBuilder":
        return cls(resource="stats/activity/day-by-day", http_method="POST")

    @classmethod
    def stats_interaction_endpoint(cls) -> "RequestBuilder":
        return cls(resource="stats/interaction", http_method="POST")

    @classmethod
    def users_endpoint(cls) -> "RequestBuilder":
        return cls(resource="users")

    @classmethod
    def calls_endpoint(cls) -> "RequestBuilder":
        return cls(resource="calls")

    @classmethod
    def extensive_calls_endpoint(cls) -> "RequestBuilder":
        return cls(resource="calls/extensive", http_method="POST")

    @classmethod
    def scorecards_endpoint(cls) -> "RequestBuilder":
        return cls(resource="settings/scorecards")

    @classmethod
    def answered_scorecards_endpoint(cls) -> "RequestBuilder":
        return cls(resource="stats/activity/scorecards", http_method="POST")

    def __init__(self, resource: str = "", http_method: str = "GET") -> None:
        self._resource = resource
        self._http_method = http_method
        self._query_params: Dict[str, Any] = {}
        self._body: Optional[str] = None
        self._any_query_params = False

    def with_query_param(self, key: str, value: Any) -> "RequestBuilder":
        self._query_params[key] = value
        return self

    def with_from_date_time(self, from_date_time: str) -> "RequestBuilder":
        self._query_params["fromDateTime"] = from_date_time
        return self

    def with_cursor(self, cursor: str) -> "RequestBuilder":
        self._query_params["cursor"] = cursor
        return self

    def with_limit(self, limit: int) -> "RequestBuilder":
        self._query_params["limit"] = limit
        return self

    def with_any_query_params(self) -> "RequestBuilder":
        self._any_query_params = True
        return self

    def with_body(self, body: str) -> "RequestBuilder":
        self._body = body
        return self

    def build(self) -> HttpRequest:
        query_params = ANY_QUERY_PARAMS if self._any_query_params else (self._query_params if self._query_params else None)
        return HttpRequest(
            url=f"{GONG_API_URL}/{self._resource}",
            query_params=query_params,
            body=self._body,
        )
