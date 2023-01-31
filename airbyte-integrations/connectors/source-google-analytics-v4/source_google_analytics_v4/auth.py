from typing import Mapping, Tuple
from typing import Any
import pendulum
import requests
import jwt
import time
import json
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator, TokenAuthenticator


class GoogleAnalyticsServiceOauth2Authenticator(Oauth2Authenticator):
    """Request example for API token extraction:
    curl --location --request POST
    https://oauth2.googleapis.com/token?grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=signed_JWT
    """

    def __init__(self, config: Mapping):
        self.credentials_json = json.loads(config["credentials_json"])
        self.client_email = self.credentials_json["client_email"]
        self.scope = "https://www.googleapis.com/auth/analytics.readonly"

        super().__init__(
            token_refresh_endpoint="https://oauth2.googleapis.com/token",
            client_secret=self.credentials_json["private_key"],
            client_id=self.credentials_json["private_key_id"],
            refresh_token=None,
        )

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Calling the Google OAuth 2.0 token endpoint. Used for authorizing signed JWT.
        Returns tuple with access token and token's time-to-live
        """
        response_json = None
        try:
            response = requests.request(
                method="POST", url=self.token_refresh_endpoint, params=self.get_refresh_request_params())

            response_json = response.json()
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if response_json and "error" in response_json:
                raise Exception(
                    "Error refreshing access token {}. Error: {}; Error details: {}; Exception: {}".format(
                        response_json, response_json["error"], response_json["error_description"], e
                    )
                ) from e
            raise Exception(f"Error refreshing access token: {e}") from e
        else:
            return response_json["access_token"], response_json["expires_in"]

    def get_refresh_request_params(self) -> Mapping[str, Any]:
        """
        Sign the JWT with RSA-256 using the private key found in service account JSON file.
        """
        token_lifetime = 3600  # token lifetime is 1 hour

        issued_at = time.time()
        expiration_time = issued_at + token_lifetime

        payload = {
            "iss": self.client_email,
            "sub": self.client_email,
            "scope": self.scope,
            "aud": self.token_refresh_endpoint,
            "iat": issued_at,
            "exp": expiration_time,
        }
        headers = {"kid": self.client_id}
        signed_jwt = jwt.encode(
            payload, self.client_secret, headers=headers, algorithm="RS256")
        return {"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": str(signed_jwt)}


class CredentialsCraftAuthenticator(TokenAuthenticator):
    def __init__(self, credentials_craft_host: str, credentials_craft_token: str, credentials_craft_token_id: int):
        self._cc_host = credentials_craft_host
        self._cc_token = credentials_craft_token
        self._cc_token_id = credentials_craft_token_id
        self._token_data = None

    @property
    def _url(self) -> str:
        return f"{self._cc_host}/api/v1/token/google/{self._cc_token_id}/"

    def token_data_from_cc(self) -> Mapping[str, Any]:
        resp = requests.get(self._url, headers=self.cc_auth_headers)
        resp.raise_for_status()
        return resp.json()

    @property
    def cc_auth_headers(self) -> Mapping[str, str]:
        return {"Authorization": f"Bearer {self._cc_token}"}

    def update_token(self) -> Mapping[str, Any]:
        resp = requests.put(self._url + 'refresh',
                            headers=self.cc_auth_headers)
        resp.raise_for_status()
        return resp.json()

    def is_access_token_expired(self, token_data: Mapping[str, Any]) -> bool:
        return pendulum.parse(token_data['access_token_expires_datetime']).in_tz('UTC') < pendulum.now('UTC')

    def get_auth_header(self) -> Mapping[str, Any]:
        if not self._token_data:
            self._token_data = self.token_data_from_cc()
        if self.is_access_token_expired(self._token_data):
            self._token_data = self.update_token()
        super().__init__(
            self._token_data["access_token"], "Bearer", "Authorization")
        return super().get_auth_header()

    def check_connection(self):
        try:
            requests.get(self._cc_host, timeout=15)
        except:
            return False, f"Connection to {self._cc_host} timed out"

        token_resp = requests.get(
            self._url, headers={"Authorization": f"Bearer {self._cc_token}"}).json()
        if token_resp.get("error"):
            return False, f"CredentialsCraft error: {token_resp.get('error')}"

        return True, None
