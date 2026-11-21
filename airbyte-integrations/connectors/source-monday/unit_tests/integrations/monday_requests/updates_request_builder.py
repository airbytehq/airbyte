# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Optional

from .base_requests_builder import MondayBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


UPDATES_FIELDS = (
    "assets{created_at,file_extension,file_size,id,name,original_geometry,public_url,uploaded_by{id},url,url_thumbnail},"
    "body,created_at,creator_id,id,item_id,replies{id,creator_id,created_at,text_body,updated_at,body},text_body,updated_at"
)


class UpdatesRequestBuilder(MondayBaseRequestBuilder):
    @classmethod
    def updates_endpoint(cls, authenticator: Authenticator) -> "UpdatesRequestBuilder":
        return cls().with_authenticator(authenticator)

    def __init__(self) -> None:
        super().__init__()
        self._page: Optional[int] = None
        self._from_date: Optional[str] = None
        self._to_date: Optional[str] = None

    @property
    def request_body(self):
        arguments = ["limit:100"]
        if self._page:
            arguments.append(f"page:{self._page}")
        if self._from_date:
            arguments.append(f'from_date:"{self._from_date}"')
            arguments.append(f'to_date:"{self._to_date}"')
        return {"query": f"{{updates({','.join(arguments)}){{{UPDATES_FIELDS}}}}}"}

    def with_page(self, page: int) -> "UpdatesRequestBuilder":
        self._page = page
        return self

    def with_date_range(self, from_date: str, to_date: str) -> "UpdatesRequestBuilder":
        self._from_date = from_date
        self._to_date = to_date
        return self
