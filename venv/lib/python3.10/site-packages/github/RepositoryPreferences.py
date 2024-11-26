############################ Copyrights and license ############################
#                                                                              #
# Copyright 2020 Dhruv Manilawala <dhruvmanila@gmail.com>                      #
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
import github.Repository


class RepositoryPreferences(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents repository preferences.
    The reference can be found here https://docs.github.com/en/free-pro-team@latest/rest/reference/checks#update-repository-preferences-for-check-suites
    """

    @property
    def preferences(self):
        """
        :type: dict
        """
        return self._preferences.value

    @property
    def repository(self):
        """
        :type: :class:`github.Repository.Repository`
        """
        return self._repository.value

    def _initAttributes(self):
        self._preferences = github.GithubObject.NotSet
        self._repository = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "preferences" in attributes:  # pragma no branch
            self._preferences = self._makeDictAttribute(attributes["preferences"])
        if "repository" in attributes:  # pragma no branch
            self._repository = self._makeClassAttribute(
                github.Repository.Repository, attributes["repository"]
            )
