from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from typing import Mapping, Any, MutableMapping, Tuple
import pendulum
import requests


class UsernamePasswordOauth2Authenticator(Oauth2Authenticator):
    def __init__(
        self,
        username: str,
        password: str,
        client_id: str,
        token_endpoint: str = 'https://backend.media/oauth/v2/token',
        access_token_name: str = "access_token",
        expires_in_name: str = "expires_in",
        refresh_request_body: Mapping[str, Any] = None
    ):
        token_data_response = requests.post(
            token_endpoint,
            json={
                'grant_type': 'password',
                'username': username,
                'password': password,
                'client_id': client_id
            }
        )
        print(token_data_response.text)
        try:
            token_data_response.raise_for_status()
        except:
            raise Exception(token_data_response.text)
        token_data = token_data_response.json()
        super().__init__(
            token_refresh_endpoint=token_endpoint,
            client_id=client_id,
            client_secret=None,
            refresh_token=token_data['refresh_token'],
            scopes=token_data['scope'],
            token_expiry_date=pendulum.now().add(
                seconds=token_data['expires_in']),
            access_token_name=access_token_name,
            expires_in_name=expires_in_name,
            refresh_request_body=refresh_request_body
        )
        self._access_token = token_data['access_token']
