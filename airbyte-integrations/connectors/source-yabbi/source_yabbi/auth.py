from datetime import datetime
import logging
import pendulum
from requests.auth import AuthBase
import requests
from typing import Mapping, Any, Tuple


# import http.client as http_client
# http_client.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


class CookiesAuthenticator(AuthBase):

    def __init__(
        self,
        auth_cookies_refresh_endpoint: str,
        get_auth_cookies_request_data: Mapping[str, Any] = None,
        get_auth_cookies_request_params: Mapping[str, Any] = None,
        get_auth_cookies_request_headers: Mapping[str, Any] = None,
        first_layer_authentiator: 'CookiesAuthenticator' = None,
        additional_constant_cookies: Mapping[str, Any] = {},
        get_auth_cookies_request_method: str = 'POST',
    ):
        self._auth_cookies_refresh_endpoint = auth_cookies_refresh_endpoint
        self._get_auth_cookies_request_params = get_auth_cookies_request_params
        self._get_auth_cookies_request_data = get_auth_cookies_request_data
        self._get_auth_cookies_request_headers = get_auth_cookies_request_headers
        self._get_auth_cookies_request_method = get_auth_cookies_request_method
        self._additional_constant_cookies = additional_constant_cookies
        self._first_layer_authentiator = first_layer_authentiator

        self._auth_cookies_expiry_date = None
        self._auth_cookies = self.refresh_auth_cookies()

    def get_auth_cookies_refresh_endpoint(self) -> str:
        return self._auth_cookies_refresh_endpoint

    def get_auth_cookies_expiry_date(self) -> pendulum.DateTime:
        return self._auth_cookies_expiry_date

    def set_auth_cookies_expiry_date(self, value: pendulum.DateTime):
        self._auth_cookies_expiry_date = value

    def auth_cookies_has_expired(self) -> bool:
        """Returns True if auth cookies is expired"""
        if self.get_auth_cookies_expiry_date():
            return pendulum.now() > self.get_auth_cookies_expiry_date()
        return True

    def get_auth_cookies(self) -> Mapping[str, str]:
        """Returns the auth cookies"""
        if self.auth_cookies_has_expired():
            t0 = pendulum.now()
            _auth_cookies, expires_in = self.refresh_auth_cookies()
            _auth_cookies.update(self._additional_constant_cookies)
            self._auth_cookies = _auth_cookies

            if self._first_layer_authentiator:
                self._auth_cookies.update(
                    self._first_layer_authentiator.get_auth_cookies())
            self.set_auth_cookies_expiry_date(t0.add(seconds=expires_in - 10))

        return self._auth_cookies

    def refresh_auth_cookies(self) -> Tuple[dict, int]:
        try:
            request_kwargs = dict(
                method=self._get_auth_cookies_request_method,
                url=self.get_auth_cookies_refresh_endpoint(),
                params=self._get_auth_cookies_request_params,
                data=self._get_auth_cookies_request_data,
                headers=self._get_auth_cookies_request_headers,
            )
            if self._first_layer_authentiator:
                request_kwargs['cookies'] = self._first_layer_authentiator.get_auth_cookies(
                )
            response = requests.request(
                **request_kwargs
            )
            response.raise_for_status()
            if not response.cookies:
                raise Exception("Invalid credentials")
            return (
                dict(response.cookies),
                min(
                    [
                        cookie.expires - int(datetime.now().timestamp())
                        for cookie in response.cookies
                    ]
                )
            )
        except Exception as e:
            raise Exception(f"Error while refreshing auth cookies: {e}") from e


class ConstantCookiesAuthenticator(CookiesAuthenticator):
    def __init__(self, auth_cookies: dict[str, str]):
        self._auth_cookies_refresh_endpoint = None
        self._get_auth_cookies_request_params = None
        self._auth_cookies = auth_cookies

    def get_auth_cookies(self) -> str:
        return self._auth_cookies


class CookiesNoAuth(CookiesAuthenticator):
    def __init__(self):
        super().__init__(
            auth_cookies_refresh_endpoint=None,
            get_auth_cookies_request_data=None
        )

    def get_auth_cookies(self) -> str:
        return {}
