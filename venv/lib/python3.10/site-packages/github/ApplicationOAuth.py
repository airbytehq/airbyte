############################ Copyrights and license ###########################
#                                                                             #
# Copyright 2019 Rigas Papathanasopoulos <rigaspapas@gmail.com>               #
# Copyright 2023 Enrico Minack <github@enrico.minack.dev>                     #
#                                                                             #
# This file is part of PyGithub.                                              #
# http://pygithub.readthedocs.io/                                             #
#                                                                             #
# PyGithub is free software: you can redistribute it and/or modify it under   #
# the terms of the GNU Lesser General Public License as published by the Free #
# Software Foundation, either version 3 of the License, or (at your option)   #
# any later version.                                                          #
#                                                                             #
# PyGithub is distributed in the hope that it will be useful, but WITHOUT ANY #
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS   #
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more#
# details.                                                                    #
#                                                                             #
# You should have received a copy of the GNU Lesser General Public License    #
# along with PyGithub. If not, see <http://www.gnu.org/licenses/>.            #
#                                                                             #
###############################################################################

import urllib

import github.GithubObject
from github.AccessToken import AccessToken


class ApplicationOAuth(github.GithubObject.NonCompletableGithubObject):
    """
    This class is used for identifying and authorizing users for Github Apps.
    The reference can be found at https://docs.github.com/en/developers/apps/building-github-apps/identifying-and-authorizing-users-for-github-apps
    """

    def __init__(self, requester, headers, attributes, completed):
        # this object requires a request without authentication
        requester = requester.withAuth(auth=None)
        super().__init__(requester, headers, attributes, completed)

    def __repr__(self):
        return self.get__repr__({"client_id": self._client_id.value})

    @property
    def client_id(self):
        return self._client_id.value

    @property
    def client_secret(self):
        return self._client_secret.value

    def _initAttributes(self):
        self._client_id = github.GithubObject.NotSet
        self._client_secret = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "client_id" in attributes:  # pragma no branch
            self._client_id = self._makeStringAttribute(attributes["client_id"])
        if "client_secret" in attributes:  # pragma no branch
            self._client_secret = self._makeStringAttribute(attributes["client_secret"])

    def get_login_url(self, redirect_uri=None, state=None, login=None):
        """
        Return the URL you need to redirect a user to in order to authorize
        your App.
        :type: string
        """
        parameters = {"client_id": self.client_id}
        if redirect_uri is not None:
            assert isinstance(redirect_uri, str), redirect_uri
            parameters["redirect_uri"] = redirect_uri
        if state is not None:
            assert isinstance(state, str), state
            parameters["state"] = state
        if login is not None:
            assert isinstance(login, str), login
            parameters["login"] = login

        parameters = urllib.parse.urlencode(parameters)

        base_url = "https://github.com/login/oauth/authorize"
        return f"{base_url}?{parameters}"

    def get_access_token(self, code, state=None):
        """
        :calls: `POST /login/oauth/access_token <https://docs.github.com/en/developers/apps/identifying-and-authorizing-users-for-github-apps>`_
        :param code: string
        :param state: string
        """
        assert isinstance(code, str), code
        post_parameters = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        if state is not None:
            post_parameters["state"] = state

        headers, data = self._checkError(
            *self._requester.requestJsonAndCheck(
                "POST",
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                input=post_parameters,
            )
        )

        return AccessToken(
            requester=self._requester,
            headers=headers,
            attributes=data,
            completed=False,
        )

    def get_app_user_auth(self, token):
        """
        :param token: AccessToken
        """
        # imported here to avoid circular import
        from github.Auth import AppUserAuth

        return AppUserAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token=token.token,
            token_type=token.type,
            expires_at=token.expires_at,
            refresh_token=token.refresh_token,
            refresh_expires_at=token.refresh_expires_at,
            requester=self._requester,
        )

    def refresh_access_token(self, refresh_token):
        """
        :calls: `POST /login/oauth/access_token <https://docs.github.com/en/developers/apps/identifying-and-authorizing-users-for-github-apps>`_
        :param refresh_token: string
        """
        assert isinstance(refresh_token, str)
        post_parameters = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        headers, data = self._checkError(
            *self._requester.requestJsonAndCheck(
                "POST",
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                input=post_parameters,
            )
        )

        return AccessToken(
            requester=self._requester,
            headers=headers,
            attributes=data,
            completed=False,
        )

    @staticmethod
    def _checkError(headers, data):
        if isinstance(data, dict) and "error" in data:
            if data["error"] == "bad_verification_code":
                raise github.BadCredentialsException(200, data, headers)
            raise github.GithubException(200, data, headers)

        return headers, data
