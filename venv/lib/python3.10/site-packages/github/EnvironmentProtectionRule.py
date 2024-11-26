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

from typing import List

import github.EnvironmentProtectionRuleReviewer
import github.GithubObject


class EnvironmentProtectionRule(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents a protection rule for an environment. The reference can be found here https://docs.github.com/en/rest/reference/deployments#environments
    """

    def __repr__(self):
        return self.get__repr__({"id": self._id.value})

    @property
    def id(self) -> int:
        return self._id.value

    @property
    def node_id(self) -> str:
        return self._node_id.value

    @property
    def type(self) -> str:
        return self._type.value

    @property
    def reviewers(
        self,
    ) -> List[
        github.EnvironmentProtectionRuleReviewer.EnvironmentProtectionRuleReviewer
    ]:
        return self._reviewers.value

    @property
    def wait_timer(self) -> int:
        return self._wait_timer.value

    def _initAttributes(self):
        self._id = github.GithubObject.NotSet
        self._node_id = github.GithubObject.NotSet
        self._type = github.GithubObject.NotSet
        self._reviewers = github.GithubObject.NotSet
        self._wait_timer = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "node_id" in attributes:  # pragma no branch
            self._node_id = self._makeStringAttribute(attributes["node_id"])
        if "type" in attributes:  # pragma no branch
            self._type = self._makeStringAttribute(attributes["type"])
        if "reviewers" in attributes:  # pragma no branch
            self._reviewers = self._makeListOfClassesAttribute(
                github.EnvironmentProtectionRuleReviewer.EnvironmentProtectionRuleReviewer,
                attributes["reviewers"],
            )
        if "wait_timer" in attributes:  # pragma no branch
            self._wait_timer = self._makeIntAttribute(attributes["wait_timer"])
