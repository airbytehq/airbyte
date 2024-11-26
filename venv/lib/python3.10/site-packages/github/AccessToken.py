############################ Copyrights and license ############################
#                                                                              #
# Copyright 2019 Rigas Papathanasopoulos <rigaspapas@gmail.com>                #
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

from datetime import datetime, timedelta, timezone
from typing import Optional

import github.GithubObject

from .GithubObject import Attribute


class AccessToken(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents access tokens.
    """

    _created: datetime
    _token: Attribute[str]
    _type: Attribute[str]
    _scope: Attribute[str]
    _expires_in: Attribute[Optional[int]]
    _refresh_token: Attribute[str]
    _refresh_expires_in: Attribute[Optional[int]]

    def __repr__(self) -> str:
        return self.get__repr__(
            {
                "token": f"{self.token[:5]}...",
                "scope": self.scope,
                "type": self.type,
                "expires_in": self.expires_in,
                "refresh_token": (
                    f"{self.refresh_token[:5]}..." if self.refresh_token else None
                ),
                "refresh_token_expires_in": self.refresh_expires_in,
            }
        )

    @property
    def token(self) -> str:
        """
        :type: string
        """
        return self._token.value

    @property
    def type(self) -> str:
        """
        :type: string
        """
        return self._type.value

    @property
    def scope(self) -> str:
        """
        :type: string
        """
        return self._scope.value

    @property
    def created(self) -> datetime:
        """
        :type: datetime
        """
        return self._created

    @property
    def expires_in(self) -> Optional[int]:
        """
        :type: Optional[int]
        """
        return self._expires_in.value

    @property
    def expires_at(self) -> Optional[datetime]:
        """
        :type: Optional[datetime]
        """
        seconds = self.expires_in
        if seconds is not None:
            return self._created + timedelta(seconds=seconds)
        return None

    @property
    def refresh_token(self) -> Optional[str]:
        """
        :type: Optional[string]
        """
        return self._refresh_token.value

    @property
    def refresh_expires_in(self) -> Optional[int]:
        """
        :type: Optional[int]
        """
        return self._refresh_expires_in.value

    @property
    def refresh_expires_at(self) -> Optional[datetime]:
        """
        :type: Optional[datetime]
        """
        seconds = self.refresh_expires_in
        if seconds is not None:
            return self._created + timedelta(seconds=seconds)
        return None

    def _initAttributes(self):
        self._token = github.GithubObject.NotSet
        self._type = github.GithubObject.NotSet
        self._scope = github.GithubObject.NotSet
        self._expires_in = github.GithubObject.NotSet
        self._refresh_token = github.GithubObject.NotSet
        self._refresh_expires_in = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        self._created = datetime.now(timezone.utc)
        if "access_token" in attributes:  # pragma no branch
            self._token = self._makeStringAttribute(attributes["access_token"])
        if "token_type" in attributes:  # pragma no branch
            self._type = self._makeStringAttribute(attributes["token_type"])
        if "scope" in attributes:  # pragma no branch
            self._scope = self._makeStringAttribute(attributes["scope"])
        if "expires_in" in attributes:  # pragma no branch
            self._expires_in = self._makeIntAttribute(attributes["expires_in"])
        if "refresh_token" in attributes:  # pragma no branch
            self._refresh_token = self._makeStringAttribute(attributes["refresh_token"])
        if "refresh_token_expires_in" in attributes:  # pragma no branch
            self._refresh_expires_in = self._makeIntAttribute(
                attributes["refresh_token_expires_in"]
            )
