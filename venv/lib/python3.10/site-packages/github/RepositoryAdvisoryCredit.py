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

import sys
import typing

import github.GithubObject
import github.NamedUser

if sys.version_info >= (3, 8):
    # TypedDict is only available in Python 3.8 and later
    class SimpleCredit(typing.TypedDict):
        """
        A simple credit for a security advisory.
        """

        login: typing.Union[str, "github.NamedUser.NamedUser"]
        type: str

else:
    SimpleCredit = typing.Dict[str, typing.Any]

Credit = typing.Union[SimpleCredit, "RepositoryAdvisoryCredit"]


class RepositoryAdvisoryCredit(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents a credit that is assigned to a SecurityAdvisory.
    The reference can be found here https://docs.github.com/en/rest/security-advisories/repository-advisories
    """

    @property
    def login(self) -> str:
        """
        :type: string
        """
        return self._login.value

    @property
    def type(self) -> str:
        """
        :type: string
        """
        return self._type.value

    # noinspection PyPep8Naming
    def _initAttributes(self):
        self._login = github.GithubObject.NotSet
        self._type = github.GithubObject.NotSet

    # noinspection PyPep8Naming
    def _useAttributes(self, attributes):
        if "login" in attributes:  # pragma no branch
            self._login = self._makeStringAttribute(attributes["login"])
        if "type" in attributes:  # pragma no branch
            self._type = self._makeStringAttribute(attributes["type"])

    @staticmethod
    def _validate_credit(credit: Credit) -> None:
        assert isinstance(credit, (dict, RepositoryAdvisoryCredit)), credit
        if isinstance(credit, dict):
            assert "login" in credit, credit
            assert "type" in credit, credit
            assert isinstance(
                credit["login"], (str, github.NamedUser.NamedUser)
            ), credit["login"]
            assert isinstance(credit["type"], str), credit["type"]
        else:
            assert isinstance(credit.login, str), credit.login
            assert isinstance(credit.type, str), credit.type

    @staticmethod
    def _to_github_dict(credit: Credit) -> SimpleCredit:
        assert isinstance(credit, (dict, RepositoryAdvisoryCredit)), credit
        if isinstance(credit, dict):
            assert "login" in credit, credit
            assert "type" in credit, credit
            assert isinstance(
                credit["login"], (str, github.NamedUser.NamedUser)
            ), credit["login"]
            login = credit["login"]
            if isinstance(login, github.NamedUser.NamedUser):
                login = login.login
            return {
                "login": login,
                "type": credit["type"],
            }
        else:
            return {
                "login": credit.login,
                "type": credit.type,
            }
