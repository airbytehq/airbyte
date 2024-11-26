############################ Copyrights and license ############################
#                                                                              #
# Copyright 2018 Steve Kowalik <steven@wedontsleep.org>                        #
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


class RequiredStatusChecks(github.GithubObject.CompletableGithubObject):
    """
    This class represents Required Status Checks. The reference can be found here https://docs.github.com/en/rest/reference/repos#get-status-checks-protection
    """

    def __repr__(self):
        return self.get__repr__({"strict": self._strict.value, "url": self._url.value})

    @property
    def strict(self):
        """
        :type: bool
        """
        self._completeIfNotSet(self._strict)
        return self._strict.value

    @property
    def contexts(self):
        """
        :type: list of string
        """
        self._completeIfNotSet(self._contexts)
        return self._contexts.value

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    def _initAttributes(self):
        self._strict = github.GithubObject.NotSet
        self._contexts = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "strict" in attributes:  # pragma no branch
            self._strict = self._makeBoolAttribute(attributes["strict"])
        if "contexts" in attributes:  # pragma no branch
            self._contexts = self._makeListOfStringsAttribute(attributes["contexts"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
