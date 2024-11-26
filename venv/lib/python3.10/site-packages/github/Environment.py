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

import datetime
from typing import List

import github.EnvironmentDeploymentBranchPolicy
import github.EnvironmentProtectionRule
import github.GithubObject


class Environment(github.GithubObject.CompletableGithubObject):
    """
    This class represents Environment. The reference can be found here https://docs.github.com/en/rest/reference/deployments#environments
    """

    def __repr__(self):
        return self.get__repr__({"name": self._name.value})

    @property
    def created_at(self) -> datetime.datetime:
        self._completeIfNotSet(self._created_at)
        return self._created_at.value

    @property
    def html_url(self) -> str:
        self._completeIfNotSet(self._html_url)
        return self._html_url.value

    @property
    def id(self) -> int:
        self._completeIfNotSet(self._id)
        return self._id.value

    @property
    def name(self) -> str:
        self._completeIfNotSet(self._name)
        return self._name.value

    @property
    def node_id(self) -> str:
        self._completeIfNotSet(self._node_id)
        return self._node_id.value

    @property
    def protection_rules(
        self,
    ) -> List[github.EnvironmentProtectionRule.EnvironmentProtectionRule]:
        self._completeIfNotSet(self._protection_rules)
        return self._protection_rules.value

    @property
    def updated_at(self) -> datetime.datetime:
        self._completeIfNotSet(self._updated_at)
        return self._updated_at.value

    @property
    def url(self) -> str:
        self._completeIfNotSet(self._url)
        return self._url.value

    @property
    def deployment_branch_policy(
        self,
    ) -> github.EnvironmentDeploymentBranchPolicy.EnvironmentDeploymentBranchPolicy:
        self._completeIfNotSet(self._deployment_branch_policy)
        return self._deployment_branch_policy.value

    def _initAttributes(self):
        self._created_at = github.GithubObject.NotSet
        self._html_url = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._node_id = github.GithubObject.NotSet
        self._protection_rules = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet
        self._deployment_branch_policy = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "html_url" in attributes:  # pragma no branch
            self._html_url = self._makeStringAttribute(attributes["html_url"])
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "node_id" in attributes:  # pragma no branch
            self._node_id = self._makeStringAttribute(attributes["node_id"])
        if "protection_rules" in attributes:  # pragma no branch
            self._protection_rules = self._makeListOfClassesAttribute(
                github.EnvironmentProtectionRule.EnvironmentProtectionRule,
                attributes["protection_rules"],
            )
        if "updated_at" in attributes:  # pragma no branch
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
        if "deployment_branch_policy" in attributes:  # pragma no branch
            self._deployment_branch_policy = self._makeClassAttribute(
                github.EnvironmentDeploymentBranchPolicy.EnvironmentDeploymentBranchPolicy,
                attributes["deployment_branch_policy"],
            )
