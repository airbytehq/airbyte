############################ Copyrights and license ############################
#                                                                              #
# Copyright 2023 Enrico Minack <github@enrico.minack.dev>                      #
#                                                                              #
# This file is part of PyGithub.                                               #
# http://pygithub.readthedocs.io/                                              #
#                                                                              #
# PyGithub is free software: you can redistribute it and/or modify it under    #
# the terms of the GNU Lesser General Public License as published by the Free  #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# PyGithub is distributed in the hope that it will be useful, but WITHOUT ANY  #
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS    #
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more #
# details.                                                                     #
#                                                                              #
# You should have received a copy of the GNU Lesser General Public License     #
# along with PyGithub. If not, see <http://www.gnu.org/licenses/>.             #
#                                                                              #
################################################################################

import abc
import base64
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Union

import jwt

from github import Consts
from github.InstallationAuthorization import InstallationAuthorization
from github.Requester import Requester, WithRequester

# For App authentication, time remaining before token expiration to request a new one
ACCESS_TOKEN_REFRESH_THRESHOLD_SECONDS = 20
TOKEN_REFRESH_THRESHOLD_TIMEDELTA = timedelta(
    seconds=ACCESS_TOKEN_REFRESH_THRESHOLD_SECONDS
)


class Auth(abc.ABC):
    """
    This class is the base class of all authentication methods for Requester.
    """

    @property
    @abc.abstractmethod
    def token_type(self) -> str:
        """
        The type of the auth token as used in the HTTP Authorization header, e.g. Bearer or Basic.
        :return: token type
        """
        pass

    @property
    @abc.abstractmethod
    def token(self) -> str:
        """
        The auth token as used in the HTTP Authorization header.
        :return: token
        """
        pass


class Login(Auth):
    """
    This class is used to authenticate Requester with login and password.
    """

    def __init__(self, login: str, password: str):
        assert isinstance(login, str)
        assert len(login) > 0
        assert isinstance(password, str)
        assert len(password) > 0

        self._login = login
        self._password = password

    @property
    def login(self) -> str:
        return self._login

    @property
    def password(self) -> str:
        return self._password

    @property
    def token_type(self) -> str:
        return "Basic"

    @property
    def token(self) -> str:
        return (
            base64.b64encode(f"{self.login}:{self.password}".encode())
            .decode("utf-8")
            .replace("\n", "")
        )


class Token(Auth):
    """
    This class is used to authenticate Requester with a single constant token.
    """

    def __init__(self, token: str):
        assert isinstance(token, str)
        assert len(token) > 0
        self._token = token

    @property
    def token_type(self) -> str:
        return "token"

    @property
    def token(self) -> str:
        return self._token


class JWT(Auth):
    """
    This class is the base class to authenticate with a JSON Web Token (JWT).
    https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app
    """

    @property
    def token_type(self) -> str:
        return "Bearer"


class AppAuth(JWT):
    """
    This class is used to authenticate Requester as a GitHub App.
    https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app
    """

    def __init__(
        self,
        app_id: Union[int, str],
        private_key: str,
        jwt_expiry: int = Consts.DEFAULT_JWT_EXPIRY,
        jwt_issued_at: int = Consts.DEFAULT_JWT_ISSUED_AT,
        jwt_algorithm: str = Consts.DEFAULT_JWT_ALGORITHM,
    ):
        assert isinstance(app_id, (int, str)), app_id
        if isinstance(app_id, str):
            assert len(app_id) > 0, "app_id must not be empty"
        assert isinstance(private_key, str)
        assert len(private_key) > 0, "private_key must not be empty"
        assert isinstance(jwt_expiry, int), jwt_expiry
        assert Consts.MIN_JWT_EXPIRY <= jwt_expiry <= Consts.MAX_JWT_EXPIRY, jwt_expiry

        self._app_id = app_id
        self._private_key = private_key
        self._jwt_expiry = jwt_expiry
        self._jwt_issued_at = jwt_issued_at
        self._jwt_algorithm = jwt_algorithm

    @property
    def app_id(self) -> Union[int, str]:
        return self._app_id

    @property
    def private_key(self) -> str:
        return self._private_key

    @property
    def token(self) -> str:
        return self.create_jwt()

    def get_installation_auth(
        self,
        installation_id: int,
        token_permissions: Optional[Dict[str, str]] = None,
        requester: Optional[Requester] = None,
    ) -> "AppInstallationAuth":
        """
        Creates a github.Auth.AppInstallationAuth instance for an installation.
        :param installation_id: installation id
        :param token_permissions: optional permissions
        :param requester: optional requester with app authentication
        :return:
        """
        return AppInstallationAuth(self, installation_id, token_permissions, requester)

    def create_jwt(self, expiration=None) -> str:
        """
        Create a signed JWT
        https://docs.github.com/en/developers/apps/building-github-apps/authenticating-with-github-apps#authenticating-as-a-github-app

        :return string: jwt
        """
        if expiration is not None:
            assert isinstance(expiration, int), expiration
            assert (
                Consts.MIN_JWT_EXPIRY <= expiration <= Consts.MAX_JWT_EXPIRY
            ), expiration

        now = int(time.time())
        payload = {
            "iat": now + self._jwt_issued_at,
            "exp": now + (expiration if expiration is not None else self._jwt_expiry),
            "iss": self._app_id,
        }
        encrypted = jwt.encode(
            payload, key=self.private_key, algorithm=self._jwt_algorithm
        )

        if isinstance(encrypted, bytes):
            return encrypted.decode("utf-8")
        return encrypted


class AppAuthToken(JWT):
    """
    This class is used to authenticate Requester as a GitHub App with a single constant JWT.
    https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app
    """

    def __init__(self, token: str):
        assert isinstance(token, str)
        assert len(token) > 0
        self._token = token

    @property
    def token(self) -> str:
        return self._token


class AppInstallationAuth(Auth, WithRequester["AppInstallationAuth"]):
    """
    This class is used to authenticate Requester as a GitHub App Installation.
    https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation
    """

    # imported here to avoid circular import, needed for typing only
    from github.GithubIntegration import GithubIntegration

    # used to fetch live access token when calling self.token
    __integration: Optional[GithubIntegration] = None
    __installation_authorization: Optional[InstallationAuthorization] = None

    def __init__(
        self,
        app_auth: AppAuth,
        installation_id: int,
        token_permissions: Optional[Dict[str, str]] = None,
        requester: Optional[Requester] = None,
    ):
        super().__init__()

        assert isinstance(app_auth, AppAuth), app_auth
        assert isinstance(installation_id, int), installation_id
        assert token_permissions is None or isinstance(
            token_permissions, dict
        ), token_permissions

        self._app_auth = app_auth
        self._installation_id = installation_id
        self._token_permissions = token_permissions

        if requester is not None:
            self.withRequester(requester)

    def withRequester(self, requester: Requester) -> "AppInstallationAuth":
        super().withRequester(requester.withAuth(self._app_auth))

        from github.GithubIntegration import GithubIntegration

        self.__integration = GithubIntegration(
            auth=self._app_auth,
            base_url=requester.base_url,
        )

        return self

    @property
    def app_id(self) -> Union[int, str]:
        return self._app_auth.app_id

    @property
    def private_key(self) -> str:
        return self._app_auth.private_key

    @property
    def installation_id(self) -> int:
        return self._installation_id

    @property
    def token_permissions(self) -> Optional[Dict[str, str]]:
        return self._token_permissions

    @property
    def token_type(self) -> str:
        return "token"

    @property
    def token(self) -> str:
        if self.__installation_authorization is None or self._is_expired:
            self.__installation_authorization = self._get_installation_authorization()
        return self.__installation_authorization.token

    @property
    def _is_expired(self) -> bool:
        assert self.__installation_authorization is not None
        token_expires_at = (
            self.__installation_authorization.expires_at
            - TOKEN_REFRESH_THRESHOLD_TIMEDELTA
        )
        # to be fixed by https://github.com/PyGithub/PyGithub/pull/1831
        return token_expires_at < datetime.now(timezone.utc).replace(tzinfo=None)

    def _get_installation_authorization(self) -> InstallationAuthorization:
        assert (
            self.__integration is not None
        ), "Method withRequester(Requester) must be called first"
        return self.__integration.get_access_token(
            self._installation_id,
            permissions=self._token_permissions,
        )


class AppUserAuth(Auth, WithRequester["AppUserAuth"]):
    """
    This class is used to authenticate Requester as a GitHub App on behalf of a user.
    https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-with-a-github-app-on-behalf-of-a-user
    """

    _client_id: str
    _client_secret: str
    _token: str
    _type: str
    _scope: Optional[str]
    _expires_at: Optional[datetime]
    _refresh_token: Optional[str]
    _refresh_expires_at: Optional[datetime]

    # imported here to avoid circular import
    from github.ApplicationOAuth import ApplicationOAuth

    __app: ApplicationOAuth

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token: str,
        token_type: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        refresh_token=None,
        refresh_expires_at=None,
        requester: Optional[Requester] = None,
    ):
        assert isinstance(client_id, str)
        assert len(client_id) > 0
        assert isinstance(client_secret, str)
        assert len(client_secret) > 0
        assert isinstance(token, str)
        assert len(token) > 0
        if token_type is not None:
            assert isinstance(token_type, str)
            assert len(token_type) > 0
        assert isinstance(token, str)
        if token_type is not None:
            assert isinstance(token_type, str)
            assert len(token_type) > 0
        if expires_at is not None:
            assert isinstance(expires_at, datetime)
        if refresh_token is not None:
            assert isinstance(refresh_token, str)
            assert len(refresh_token) > 0
        if refresh_expires_at is not None:
            assert isinstance(refresh_expires_at, datetime)

        self._client_id = client_id
        self._client_secret = client_secret
        self._token = token
        self._type = token_type or "bearer"
        self._expires_at = expires_at
        self._refresh_token = refresh_token
        self._refresh_expires_at = refresh_expires_at

        if requester is not None:
            self.withRequester(requester)

    @property
    def token_type(self) -> str:
        return self._type

    @property
    def token(self) -> str:
        if self._is_expired:
            self._refresh()
        return self._token

    def withRequester(self, requester: Requester) -> "AppUserAuth":
        super().withRequester(requester.withAuth(None))

        # imported here to avoid circular import
        from github.ApplicationOAuth import ApplicationOAuth

        self.__app = ApplicationOAuth(
            # take requester given to super().withRequester, not given to this method
            super().requester,
            headers={},
            attributes={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            completed=False,
        )

        return self

    @property
    def _is_expired(self) -> bool:
        return self._expires_at is not None and self._expires_at < datetime.now(
            timezone.utc
        )

    def _refresh(self):
        if self._refresh_token is None:
            raise RuntimeError(
                "Cannot refresh expired token because no refresh token has been provided"
            )
        if (
            self._refresh_expires_at is not None
            and self._refresh_expires_at < datetime.now(timezone.utc)
        ):
            raise RuntimeError(
                "Cannot refresh expired token because refresh token also expired"
            )

        # refresh token
        token = self.__app.refresh_access_token(self._refresh_token)

        # update this auth
        self._token = token.token
        self._type = token.type
        self._scope = token.scope
        self._expires_at = token.expires_at
        self._refresh_token = token.refresh_token
        self._refresh_expires_at = token.refresh_expires_at

    @property
    def expires_at(self) -> Optional[datetime]:
        return self._expires_at

    @property
    def refresh_token(self) -> Optional[str]:
        return self._refresh_token

    @property
    def refresh_expires_at(self) -> Optional[datetime]:
        return self._refresh_expires_at
