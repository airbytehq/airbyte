from airbyte_cdk import SingleUseRefreshTokenOauth2Authenticator


class ExactOauth2Authenticator(SingleUseRefreshTokenOauth2Authenticator):
    pass


def get_auth_header(self):
    token = self.get_access_token()
    return token
