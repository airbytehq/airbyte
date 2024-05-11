# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest

from . import AbstractRequestBuilder


class OAuthRequestBuilder(AbstractRequestBuilder):
    URL = "https://api.hubapi.com/oauth/v1/token"

    def __init__(self):
        self._params = {}

    def with_client_id(self, client_id: str):
        self._params["client_id"] = client_id
        return self

    def with_client_secret(self, client_secret: str):
        self._params["client_secret"] = client_secret
        return self

    def with_refresh_token(self, refresh_token: str):
        self._params["refresh_token"] = refresh_token
        return self

    def build(self) -> HttpRequest:
        client_id, client_secret, refresh_token = self._params["client_id"], self._params["client_secret"], self._params["refresh_token"]
        return HttpRequest(
            url=self.URL,
            body=f"grant_type=refresh_token&client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}"
        )


class ScopesRequestBuilder(AbstractRequestBuilder):
    URL = "https://api.hubapi.com/oauth/v1/access-tokens/{token}"

    def __init__(self):
        self._token = None

    def with_access_token(self, token: str):
        self._token = token
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(url=self.URL.format(token=self._token))


class CustomObjectsRequestBuilder(AbstractRequestBuilder):
    URL = "https://api.hubapi.com/crm/v3/schemas"

    def build(self) -> HttpRequest:
        return HttpRequest(url=self.URL)


class PropertiesRequestBuilder(AbstractRequestBuilder):
    URL = "https://api.hubapi.com/properties/v2/{resource}/properties"

    def __init__(self):
        self._resource = None

    def for_entity(self, entity):
        self._resource = entity
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(url=self.URL.format(resource=self._resource))
