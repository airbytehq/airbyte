#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Mapping, Union

import requests
from requests import HTTPError

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class AuthenticatorFacebookPageAccessToken(NoAuth):
    config: Config
    page_id: Union[InterpolatedString, str]
    access_token: Union[InterpolatedString, str]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._page_id = InterpolatedString.create(self.page_id, parameters=parameters).eval(self.config)
        self._access_token = InterpolatedString.create(self.access_token, parameters=parameters).eval(self.config)

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach the page access token to params to authenticate on the HTTP request"""
        page_access_token = self.generate_page_access_token()
        request.prepare_url(url=request.url, params={"access_token": page_access_token})
        return request

    def generate_page_access_token(self) -> str:
        # We are expecting to receive User access token from config. To access
        # Pages API we need to generate Page access token. Page access tokens
        # can be generated from another Page access token (with the same page ID)
        # so if user manually set Page access token instead of User access
        # token it would be no problem unless it has wrong page ID.
        # https://developers.facebook.com/docs/pages/access-tokens#get-a-page-access-token
        try:
            r = requests.get(
                f"https://graph.facebook.com/{self._page_id}", params={"fields": "access_token", "access_token": self._access_token}
            )
            if r.status_code != HTTPStatus.OK:
                raise HTTPError(r.text)
            return r.json().get("access_token")
        except Exception as e:
            raise Exception(f"Error while generating page access token: {e}") from e