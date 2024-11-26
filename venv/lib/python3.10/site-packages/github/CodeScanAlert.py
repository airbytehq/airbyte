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

import github.CodeScanAlertInstance
import github.CodeScanRule
import github.CodeScanTool
import github.GithubObject
import github.NamedUser
import github.PaginatedList


class CodeScanAlert(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents alerts from code scanning.
    The reference can be found here https://docs.github.com/en/rest/reference/code-scanning.
    """

    def __repr__(self):
        return self.get__repr__({"number": self.number})

    @property
    def number(self):
        """
        :type: int
        """
        return self._number.value

    @property
    def rule(self):
        """
        :type: :class: `github.CodeScanRule.CodeScanRule`
        """
        return self._rule.value

    @property
    def tool(self):
        """
        :type:  :class: `github.CodeScanTool.CodeScanTool`
        """
        return self._tool.value

    @property
    def created_at(self):
        """
        :type: datetime
        """
        return self._created_at.value

    @property
    def dismissed_at(self):
        """
        :type: datetime
        """
        return self._dismissed_at.value

    @property
    def dismissed_by(self):
        """
        :type: :class: `github.NamedUser.NamedUser`
        """
        return self._dismissed_by.value

    @property
    def dismissed_reason(self):
        """
        :type: str
        """
        return self._dismissed_reason.value

    @property
    def url(self):
        """
        :type: string
        """
        return self._url.value

    @property
    def html_url(self):
        """
        :type: string
        """
        return self._html_url.value

    @property
    def instances_url(self):
        """
        :type: string
        """
        return self._instances_url.value

    @property
    def most_recent_instance(self):
        """
        :type: :class: github.CodeScanAlertInstance.CodeScanAlertInstance
        """
        return self._most_recent_instance.value

    @property
    def state(self):
        """
        :type: str
        """
        return self._state.value

    def get_instances(self):
        """
        :calls: `GET` on the URL for instances as provided by Github
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.CodeScanAlertInstance.CodeScanAlertInstance`
        """
        return github.PaginatedList.PaginatedList(
            github.CodeScanAlertInstance.CodeScanAlertInstance,
            self._requester,
            self.instances_url,
            None,
        )

    def _initAttributes(self):
        self._number = github.GithubObject.NotSet
        self._rule = github.GithubObject.NotSet
        self._tool = github.GithubObject.NotSet

        self._created_at = github.GithubObject.NotSet
        self._dismissed_at = github.GithubObject.NotSet
        self._dismissed_by = github.GithubObject.NotSet
        self._dismissed_reason = github.GithubObject.NotSet

        self._url = github.GithubObject.NotSet
        self._html_url = github.GithubObject.NotSet
        self._instances_url = github.GithubObject.NotSet

        self._most_recent_instance = github.GithubObject.NotSet
        self._state = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "number" in attributes:  # pragma no branch
            self._number = self._makeIntAttribute(attributes["number"])
        if "rule" in attributes:  # pragma no branch
            self._rule = self._makeClassAttribute(
                github.CodeScanRule.CodeScanRule, attributes["rule"]
            )
        if "tool" in attributes:  # pragma no branch
            self._tool = self._makeClassAttribute(
                github.CodeScanTool.CodeScanTool, attributes["tool"]
            )

        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "dismissed_at" in attributes:  # pragma no branch
            self._dismissed_at = self._makeDatetimeAttribute(attributes["dismissed_at"])
        if "dismissed_by" in attributes:  # pragma no branch
            self._dismissed_by = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["dismissed_by"]
            )
        if "dismissed_reason" in attributes:  # pragma no branch
            self._dismissed_reason = self._makeStringAttribute(
                attributes["dismissed_reason"]
            )

        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
        if "html_url" in attributes:  # pragma no branch
            self._html_url = self._makeStringAttribute(attributes["html_url"])
        if "instances_url" in attributes:  # pragma no branch
            self._instances_url = self._makeStringAttribute(attributes["instances_url"])

        if "most_recent_instance" in attributes:  # pragma no branch
            self._most_recent_instance = self._makeClassAttribute(
                github.CodeScanAlertInstance.CodeScanAlertInstance,
                attributes["most_recent_instance"],
            )
        if "state" in attributes:  # pragma no branch
            self._state = self._makeStringAttribute(attributes["state"])
