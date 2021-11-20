from abc import ABC, abstractmethod
from typing import Any, List, Mapping, MutableMapping, Tuple

from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from airbyte_cdk.sources.streams.http import HttpStream


EGNYTE_API_URL_BASE = "https://viewthespace.egnyte.com"


class EgnyteOAuth(Oauth2Authenticator):
    """
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        token_refresh_endpoint: str = "https://viewthespace.egnyte.com/puboauth/token"
    ):
        super().__init__(self, token_refresh_endpoint, client_id, client_secret)
        self.username = username
        self.password = password

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "username": self.username,
            "password": self.password
        }

        if self.scopes:
            payload["scopes"] = self.scopes

        return payload


class EgnyteApiStream(HttpStream, ABC):
    url_base = EGNYTE_API_URL_BASE


class EgnyteListStream(EgnyteApiStream, ABC):

    def __init__(self, folder_path: str = None, **kwqargs):
        super().__init__(**kwargs)
        self._folder_path = folder_path

    def path(self):
        return f"/pubapi/v1/fs/{self._folder_path}"

    def parse_response(self, response: requests.Response) -> Iterable[Mapping]:
        files_lst = response.json().get("files")
        return files_lst


class EgnyteDownloadStream(EgnyteApiStream, ABC):
    def __init__(self, folder_path: str = None, **kwqargs):
        super().__init__(**kwargs)
        self._file_path = file_path

    def path(self):
        return f"/pubapi/v1/fs-content/{self._file_path}"









