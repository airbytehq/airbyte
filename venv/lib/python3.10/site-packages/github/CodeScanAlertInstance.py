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

import github.CodeScanAlertInstanceLocation
import github.GithubObject


class CodeScanAlertInstance(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents code scanning alert instances.
    The reference can be found here https://docs.github.com/en/rest/reference/code-scanning.
    """

    def __repr__(self):
        return self.get__repr__({"ref": self.ref, "analysis_key": self.analysis_key})

    @property
    def ref(self):
        """
        :type: str
        """
        return self._ref.value

    @property
    def analysis_key(self):
        """
        :type: str
        """
        return self._analysis_key.value

    @property
    def environment(self):
        """
        :type: str
        """
        return self._environment.value

    @property
    def state(self):
        """
        :type: str
        """
        return self._state.value

    @property
    def commit_sha(self):
        """
        :type: str
        """
        return self._commit_sha.value

    @property
    def message(self):
        """
        :type: str
        """
        return self._message.value

    @property
    def location(self):
        """
        :type: :class: `github.CodeScanAlertInstanceLocation.CodeScanAlertInstanceLocation`
        """
        return self._location.value

    @property
    def classifications(self):
        """
        :type: list of str
        """
        return self._classifications.value

    def _initAttributes(self):
        self._ref = github.GithubObject.NotSet
        self._analysis_key = github.GithubObject.NotSet
        self._environment = github.GithubObject.NotSet
        self._state = github.GithubObject.NotSet
        self._commit_sha = github.GithubObject.NotSet
        self._message = github.GithubObject.NotSet
        self._location = github.GithubObject.NotSet
        self._classifications = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "ref" in attributes:  # pragma no branch
            self._ref = self._makeStringAttribute(attributes["ref"])
        if "analysis_key" in attributes:  # pragma no branch
            self._analysis_key = self._makeStringAttribute(attributes["analysis_key"])
        if "environment" in attributes:  # pragma no branch
            self._environment = self._makeStringAttribute(attributes["environment"])
        if "state" in attributes:  # pragma no branch
            self._state = self._makeStringAttribute(attributes["state"])
        if "environment" in attributes:  # pragma no branch
            self._environment = self._makeStringAttribute(attributes["environment"])
        if "commit_sha" in attributes:  # pragma no branch
            self._commit_sha = self._makeStringAttribute(attributes["commit_sha"])
        if "message" in attributes:  # pragma no branch
            self._message = self._makeDictAttribute(attributes["message"])
        if "location" in attributes:  # pragma no branch
            self._location = self._makeClassAttribute(
                github.CodeScanAlertInstanceLocation.CodeScanAlertInstanceLocation,
                attributes["location"],
            )
        if "classifications" in attributes:  # pragma no branch
            self._classifications = self._makeListOfStringsAttribute(
                attributes["classifications"]
            )
