############################ Copyrights and license ############################
#                                                                              #
# Copyright 2021 Jeppe Fihl-Pearson <jeppe@tenzer.dk>                          #
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


class WorkflowStep(github.GithubObject.CompletableGithubObject):
    """
    This class represents steps in a Workflow Job. The reference can be found here https://docs.github.com/en/rest/reference/actions#workflow-jobs
    """

    def __repr__(self):
        return self.get__repr__(
            {"number": self._number.value, "name": self._name.value}
        )

    @property
    def completed_at(self):
        """
        :type: datetime.datetime
        """
        self._completeIfNotSet(self._completed_at)
        return self._completed_at.value

    @property
    def conclusion(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._conclusion)
        return self._conclusion.value

    @property
    def name(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._name)
        return self._name.value

    @property
    def number(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._number)
        return self._number.value

    @property
    def started_at(self):
        """
        :type: datetime.datetime
        """
        self._completeIfNotSet(self._started_at)
        return self._started_at.value

    @property
    def status(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._status)
        return self._status.value

    def _initAttributes(self):
        self._completed_at = github.GithubObject.NotSet
        self._conclusion = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._number = github.GithubObject.NotSet
        self._started_at = github.GithubObject.NotSet
        self._status = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "completed_at" in attributes:  # pragma no branch
            self._completed_at = self._makeDatetimeAttribute(attributes["completed_at"])
        if "conclusion" in attributes:  # pragma no branch
            self._conclusion = self._makeStringAttribute(attributes["conclusion"])
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "number" in attributes:  # pragma no branch
            self._number = self._makeIntAttribute(attributes["number"])
        if "started_at" in attributes:  # pragma no branch
            self._started_at = self._makeDatetimeAttribute(attributes["started_at"])
        if "status" in attributes:  # pragma no branch
            self._status = self._makeStringAttribute(attributes["status"])
