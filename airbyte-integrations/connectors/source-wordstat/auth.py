from requests.auth import AuthBase


class CookiesAuthenticator(AuthBase):

    def __init__(self, cookies: dict[str, any]):
        # TODO: simplified authenticator for MVP
        self._cookies: dict[str, any] = cookies

    def get_cookies(self) -> dict[str, any]:
        return self._cookies
