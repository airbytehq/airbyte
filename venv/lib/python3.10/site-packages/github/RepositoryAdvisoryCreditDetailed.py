############################ Copyrights and license ############################
#                                                                              #
# Copyright 2023 Jonathan Leitschuh <Jonathan.Leitschuh@gmail.com>             #
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

import github.GithubObject
import github.NamedUser


class RepositoryAdvisoryCreditDetailed(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents a credit that is assigned to a SecurityAdvisory.
    The reference can be found here https://docs.github.com/en/rest/security-advisories/repository-advisories
    """

    @property
    def state(self) -> str:
        """
        :type: string
        """
        return self._state.value

    @property
    def type(self) -> str:
        """
        :type: string
        """
        return self._type.value

    # noinspection PyPep8Naming
    @property
    def user(self) -> "github.NamedUser.NamedUser":
        """
        :type: :class:`github.NamedUser.NamedUser`
        """
        return self._user.value

    # noinspection PyPep8Naming
    def _initAttributes(self):
        self._state = github.GithubObject.NotSet
        self._type = github.GithubObject.NotSet
        self._user = github.GithubObject.NotSet

    # noinspection PyPep8Naming
    def _useAttributes(self, attributes):
        if "state" in attributes:  # pragma no branch
            self._state = self._makeStringAttribute(attributes["state"])
        if "type" in attributes:  # pragma no branch
            self._type = self._makeStringAttribute(attributes["type"])
        if "user" in attributes:  # pragma no branch
            self._user = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["user"]
            )
