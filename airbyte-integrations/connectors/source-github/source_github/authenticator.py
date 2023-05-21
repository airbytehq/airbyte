import os
import time

import evervault
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

# Installation tokens expire after 1hr. Have a 10 min beuffer.
INSTALLATION_TOKEN_EXPIRES_SECS = 50 * 60 

GITHUB_APP_PRIVATE_KEY = os.environ.get('GITHUB_APP_PRIVATE_KEY', '')

GITHUB_APP_ID = os.environ.get('GITHUB_APP_ID', '')

EVERVAULT_API_KEY = os.environ.get('EVERVAULT_API_KEY', '')

evervault.init(EVERVAULT_API_KEY)

class GithubInstallationAuthenticator(HttpAuthenticator):
    def __init__(self, installation_id: str, auth_method: str = "Bearer", auth_header: str = "Authorization"):
        if not GITHUB_APP_PRIVATE_KEY:
            raise Exception("Missing `GITHUB_APP_PRIVATE_KEY` required environment variable.")
        
        if not GITHUB_APP_ID:
            raise Exception("Missing `GITHUB_APP_ID` required environment variable.")
        
        if not EVERVAULT_API_KEY:
            raise Exception("Missing `EVERVAULT_API_KEY` required environment variable.")
        
        self.auth_method = auth_method
        self.auth_header = auth_header
        self._private_key = GITHUB_APP_PRIVATE_KEY
        self._app_id = GITHUB_APP_ID
        self._installation_id = installation_id
        self._token = None
        self._token_expires_at = None

    def _ensure_token(self):
        if not self._token or time.time() > self._token_expires_at:
            ev_res = evervault.run('github-installation-token-function', {
                'appId': self._app_id,
                'installationId': self._installation_id,
                'privateKEy': self._private_key,
            })
            self._token = ev_res['result']['installationToken']
            self._token_expires_at = time.time() + INSTALLATION_TOKEN_EXPIRES_SECS

    def get_auth_header(self) -> Mapping[str, Any]:
        self._ensure_token()
        assert self._token
        return {self.auth_header: f"{self.auth_method} {self._token}"}