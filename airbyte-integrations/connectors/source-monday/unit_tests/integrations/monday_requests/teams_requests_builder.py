# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from .base_requests_builder import MondayBaseRequestBuilder
from .request_authenticators.authenticator import Authenticator


class TeamsRequestBuilder(MondayBaseRequestBuilder):
    @classmethod
    def teams_endpoint(cls, authenticator: Authenticator) -> "TeamsRequestBuilder":
        return cls().with_authenticator(authenticator)

    @property
    def query_params(self):
        params = super().query_params or {}
        params["query"] = "query{teams{id,name,picture_url,users{id}}}"
        return params
