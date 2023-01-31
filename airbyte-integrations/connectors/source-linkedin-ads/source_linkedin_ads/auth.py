from typing import Any, Dict, List, Mapping, Optional, Tuple
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator, TokenAuthenticator
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
import requests

class Oauth2AuthenticatorWithProxy(Oauth2Authenticator):
    def __init__(
        self,
        token_refresh_endpoint: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        scopes: List[str] = None,
        refresh_access_token_headers: Optional[Mapping[str, Any]] = None,
        refresh_access_token_authenticator: Optional[HttpAuthenticator] = None,
        proxies: Dict[str, Any] = {}
    ):
        super().__init__(
            token_refresh_endpoint,
            client_id,
            client_secret,
            refresh_token,
            scopes,
            refresh_access_token_headers,
            refresh_access_token_authenticator
        )
        self._session = requests.Session()
        if proxies:
            self._session.proxies.update(proxies)
    
    def refresh_access_token(self) -> Tuple[str, int]:
        """
        returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        try:
            response = self._session.request(
                method="POST",
                url=self.token_refresh_endpoint,
                data=self.get_refresh_request_body(),
                headers=self.get_refresh_access_token_headers(),
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e