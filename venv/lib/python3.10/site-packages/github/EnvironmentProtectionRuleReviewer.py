############################ Copyrights and license ############################
#                                                                              #
# Copyright 2022 Alson van der Meulen <alson.vandermeulen@dearhealth.com>      #
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

from __future__ import annotations

import github.GithubObject
import github.NamedUser
import github.Team


class EnvironmentProtectionRuleReviewer(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents a reviewer for an EnvironmentProtectionRule. The reference can be found here https://docs.github.com/en/rest/reference/deployments#environments
    """

    def __repr__(self):
        return self.get__repr__({"type": self._type.value})

    @property
    def type(self) -> str:
        return self._type.value

    @property
    def reviewer(self) -> github.NamedUser.NamedUser | github.Team.Team:
        return self._reviewer.value

    def _initAttributes(self):
        self._type = github.GithubObject.NotSet
        self._reviewer = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "type" in attributes:  # pragma no branch
            self._type = self._makeStringAttribute(attributes["type"])
        if "reviewer" in attributes:  # pragma no branch
            assert self._type.value in ("User", "Team")
            if self._type.value == "User":
                self._reviewer = self._makeClassAttribute(
                    github.NamedUser.NamedUser, attributes["reviewer"]
                )
            elif self._type.value == "Team":
                self._reviewer = self._makeClassAttribute(
                    github.Team.Team, attributes["reviewer"]
                )


class ReviewerParams:
    """
    This class presents reviewers as can be configured for an Environment.
    """

    def __init__(self, type_: str, id_: int):
        assert isinstance(type_, str) and type_ in ("User", "Team")
        assert isinstance(id_, int)
        self.type = type_
        self.id = id_

    def _asdict(self) -> dict:
        return {
            "type": self.type,
            "id": self.id,
        }
