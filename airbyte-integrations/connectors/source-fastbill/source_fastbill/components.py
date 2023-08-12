from dataclasses import dataclass
import base64 
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator
from airbyte_cdk.sources.declarative.types import Config
from isodate import Duration, parse_duration


@dataclass
class CustomAuthenticator(BasicHttpAuthenticator):

    config: Config
    @property
    def token(self) -> str:

        username = self.config['username'].encode("latin1")
        password = self.config['api_key'].encode("latin1")
        encoded_credentials = base64.b64encode(b":".join((username, password))).strip()
        token = "Basic " + encoded_credentials.decode("utf-8")
        return token
