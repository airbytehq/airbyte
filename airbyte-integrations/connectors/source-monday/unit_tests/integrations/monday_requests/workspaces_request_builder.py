# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Optional

from .base_requests_builder import MondayBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class WorkspacesRequestBuilder(MondayBaseRequestBuilder):
    @classmethod
    def workspaces_endpoint(cls, authenticator: Authenticator, page: Optional[int] = None) -> "WorkspacesRequestBuilder":
        builder = cls().with_authenticator(authenticator)
        builder._page = page
        return builder

    @property
    def request_body(self):
        params = super().query_params or {}
        page_argument = f",page:{self._page}" if self._page else ""
        params["query"] = (
            "{workspaces(limit:100%s){created_at,description,id,kind,name,state,account_product{id,kind},owners_subscribers{id},settings{icon{color,image}},team_owners_subscribers{id,name},teams_subscribers{id,name},users_subscribers{id}}}"
            % page_argument
        )
        return params
