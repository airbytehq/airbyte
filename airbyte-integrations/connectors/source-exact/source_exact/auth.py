from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator


class ExactOauth2Authenticator(Oauth2Authenticator):
    pass


def get_auth_header(self):
    token = self.get_access_token()
    return token
