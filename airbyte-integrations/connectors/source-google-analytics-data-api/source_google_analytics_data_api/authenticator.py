#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime

import jwt
import requests
from source_google_analytics_data_api import utils


class GoogleServiceKeyAuthenticator(requests.auth.AuthBase):
    _google_oauth2_token_endpoint = "https://oauth2.googleapis.com/token"
    _google_oauth2_scope_endpoint = "https://www.googleapis.com/auth/analytics.readonly"
    _google_oauth2_grant_type_urn = "urn:ietf:params:oauth:grant-type:jwt-bearer"

    _default_token_lifetime_secs = 3600
    _jwt_encode_algorithm = "RS256"

    def __init__(self, credentials: dict):
        self._client_email = credentials["client_email"]
        self._client_secret = credentials["private_key"]
        self._client_id = credentials["client_id"]

        self._token: dict = {}

    def _get_claims(self) -> dict:
        now = datetime.datetime.utcnow()
        expiry = now + datetime.timedelta(seconds=self._default_token_lifetime_secs)

        return {
            "iss": self._client_email,
            "scope": self._google_oauth2_scope_endpoint,
            "aud": self._google_oauth2_token_endpoint,
            "exp": utils.datetime_to_secs(expiry),
            "iat": utils.datetime_to_secs(now),
        }

    def _get_headers(self):
        headers = {}
        if self._client_id:
            headers["kid"] = self._client_id
        return headers

    def _get_signed_payload(self) -> dict:
        claims = self._get_claims()
        headers = self._get_headers()
        assertion = jwt.encode(claims, self._client_secret, headers=headers, algorithm=self._jwt_encode_algorithm)
        return {"grant_type": self._google_oauth2_grant_type_urn, "assertion": str(assertion)}

    def _token_expired(self):
        if not self._token:
            return True
        return self._token["expires_at"] < utils.datetime_to_secs(datetime.datetime.utcnow())

    def _rotate(self):
        if self._token_expired():
            try:
                response = requests.request(method="POST", url=self._google_oauth2_token_endpoint, params=self._get_signed_payload()).json()
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error refreshing access token: {e}") from e
            self._token = dict(
                **response,
                expires_at=utils.datetime_to_secs(datetime.datetime.utcnow() + datetime.timedelta(seconds=response["expires_in"])),
            )

    def __call__(self, r: requests.Request) -> requests.Request:
        self._rotate()

        r.headers["Authorization"] = f"Bearer {self._token['access_token']}"
        return r
