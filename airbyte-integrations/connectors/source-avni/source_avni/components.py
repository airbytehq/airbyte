from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator
from dataclasses import dataclass
import boto3
import requests


@dataclass
class CustomAuthenticator(BasicHttpAuthenticator):

    @property
    def token(self) -> str:

        username = self._username.eval(self.config)
        password = self._password.eval(self.config)

        app_client_id = self.get_client_id()

        client = boto3.client("cognito-idp", region_name="ap-south-1")
        response = client.initiate_auth(
            ClientId=app_client_id, AuthFlow="USER_PASSWORD_AUTH", AuthParameters={"USERNAME": username, "PASSWORD": password}
        )
        token = response["AuthenticationResult"]["IdToken"]
        return token

    @property
    def auth_header(self) -> str:
        return "auth-token"

    def get_client_id(self):

        url_client = self.config["url_base"] + "/idp-details"
        response = requests.get(url_client, timeout=30)
        response.raise_for_status()
        client = response.json()
        return client["cognito"]["clientId"]
