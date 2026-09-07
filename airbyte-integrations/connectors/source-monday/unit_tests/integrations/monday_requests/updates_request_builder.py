# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Optional

from .base_requests_builder import MondayBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class UpdatesRequestBuilder(MondayBaseRequestBuilder):
    @classmethod
    def updates_endpoint(cls, authenticator: Authenticator, page: Optional[int] = None) -> "UpdatesRequestBuilder":
        builder = cls().with_authenticator(authenticator)
        builder._page = page
        return builder

    @property
    def request_body(self):
        params = super().query_params or {}
        page_argument = f",page:{self._page}" if self._page else ""
        params["query"] = (
            "{updates(limit:100%s){assets{created_at,file_extension,file_size,id,name,original_geometry,public_url,uploaded_by{id},url,url_thumbnail},body,created_at,creator_id,id,item_id,replies{id,creator_id,created_at,text_body,updated_at,body},text_body,updated_at}}"
            % page_argument
        )
        return params
