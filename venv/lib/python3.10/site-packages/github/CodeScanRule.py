############################ Copyrights and license ############################
#                                                                              #
# Copyright 2022 Eric Nieuwland <eric.nieuwland@gmail.com>                     #
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


class CodeScanRule(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents Alerts from code scanning.
    The reference can be found here https://docs.github.com/en/rest/reference/code-scanning.
    """

    def __repr__(self):
        return self.get__repr__({"id": self.id, "name": self.name})

    @property
    def id(self):
        """
        :type: str
        """
        return self._id.value

    @property
    def name(self):
        """
        :type: str
        """
        return self._name.value

    @property
    def severity(self):
        """
        :type: str
        """
        return self._severity.value

    @property
    def security_severity_level(self):
        """
        :type: str
        """
        return self._security_severity_level.value

    @property
    def description(self):
        """
        :type: str
        """
        return self._description.value

    def _initAttributes(self):
        self._id = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._severity = github.GithubObject.NotSet
        self._security_severity_level = github.GithubObject.NotSet
        self._description = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "id" in attributes:  # pragma no branch
            self._id = self._makeStringAttribute(attributes["id"])
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "severity" in attributes:  # pragma no branch
            self._severity = self._makeStringAttribute(attributes["severity"])
        if "security_severity_level" in attributes:  # pragma no branch
            self._security_severity_level = self._makeStringAttribute(
                attributes["security_severity_level"]
            )
        if "description" in attributes:  # pragma no branch
            self._description = self._makeStringAttribute(attributes["description"])
