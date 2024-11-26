############################ Copyrights and license ############################
#                                                                              #
# Copyright 2018 Wan Liuyang <tsfdye@gmail.com>                                #
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


class License(github.GithubObject.CompletableGithubObject):
    """
    This class represents Licenses. The reference can be found here https://docs.github.com/en/rest/reference/licenses
    """

    def __repr__(self):
        return self.get__repr__({"name": self._name.value})

    @property
    def key(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._key)
        return self._key.value

    @property
    def name(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._name)
        return self._name.value

    @property
    def spdx_id(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._spdx_id)
        return self._spdx_id.value

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    @property
    def html_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._html_url)
        return self._html_url.value

    @property
    def description(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._description)
        return self._description.value

    @property
    def implementation(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._implementation)
        return self._implementation.value

    @property
    def body(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._body)
        return self._body.value

    @property
    def permissions(self):
        """
        :type: list of string
        """
        self._completeIfNotSet(self._permissions)
        return self._permissions.value

    @property
    def conditions(self):
        """
        :type: list of string
        """
        self._completeIfNotSet(self._conditions)
        return self._conditions.value

    @property
    def limitations(self):
        """
        :type: list of string
        """
        self._completeIfNotSet(self._limitations)
        return self._limitations.value

    def _initAttributes(self):
        self._key = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._spdx_id = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet
        self._html_url = github.GithubObject.NotSet
        self._description = github.GithubObject.NotSet
        self._implementation = github.GithubObject.NotSet
        self._body = github.GithubObject.NotSet
        self._permissions = github.GithubObject.NotSet
        self._conditions = github.GithubObject.NotSet
        self._limitations = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "key" in attributes:  # pragma no branch
            self._key = self._makeStringAttribute(attributes["key"])
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "spdx_id" in attributes:  # pragma no branch
            self._spdx_id = self._makeStringAttribute(attributes["spdx_id"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
        if "html_url" in attributes:  # pragma no branch
            self._html_url = self._makeStringAttribute(attributes["html_url"])
        if "description" in attributes:  # pragma no branch
            self._description = self._makeStringAttribute(attributes["description"])
        if "implementation" in attributes:  # pragma no branch
            self._implementation = self._makeStringAttribute(
                attributes["implementation"]
            )
        if "body" in attributes:  # pragma no branch
            self._body = self._makeStringAttribute(attributes["body"])
        if "permissions" in attributes:  # pragma no branch
            self._permissions = self._makeListOfStringsAttribute(
                attributes["permissions"]
            )
        if "conditions" in attributes:  # pragma no branch
            self._conditions = self._makeListOfStringsAttribute(
                attributes["conditions"]
            )
        if "limitations" in attributes:  # pragma no branch
            self._limitations = self._makeListOfStringsAttribute(
                attributes["limitations"]
            )
