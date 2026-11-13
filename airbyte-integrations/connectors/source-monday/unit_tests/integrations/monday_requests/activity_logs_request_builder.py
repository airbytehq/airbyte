# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from .base_requests_builder import MondayBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class ActivityLogsRequestBuilder(MondayBaseRequestBuilder):
    @classmethod
    def activity_logs_endpoint(cls, authenticator: Authenticator) -> "ActivityLogsRequestBuilder":
        return cls().with_authenticator(authenticator)

    def __init__(self) -> None:
        super().__init__()
        self._page = None
        self._sub_page = None

    def with_page(self, page: int, sub_page: int) -> "ActivityLogsRequestBuilder":
        self._page = page
        self._sub_page = sub_page
        return self

    @property
    def request_body(self):
        page = f",page:{self._page}" if self._page else ""
        sub_page = f",page:{self._sub_page}" if self._sub_page else ""
        return {"query": "{boards(limit:1%s){activity_logs(limit:50%s){id,event,data,entity,created_at,user_id}}}" % (page, sub_page)}
