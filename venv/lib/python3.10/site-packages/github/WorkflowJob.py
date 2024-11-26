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
import github.WorkflowStep


class WorkflowJob(github.GithubObject.CompletableGithubObject):
    """
    This class represents Workflow Jobs. The reference can be found here https://docs.github.com/en/rest/reference/actions#workflow-jobs
    """

    def __repr__(self):
        return self.get__repr__({"id": self._id.value, "url": self._url.value})

    @property
    def check_run_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._check_run_url)
        return self._check_run_url.value

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
    def head_sha(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._head_sha)
        return self._head_sha.value

    @property
    def html_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._html_url)
        return self._html_url.value

    @property
    def id(self):
        """
        :type: int
        """
        self._completeIfNotSet(self._id)
        return self._id.value

    @property
    def name(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._name)
        return self._name.value

    @property
    def node_id(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._node_id)
        return self._node_id.value

    @property
    def run_id(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._run_id)
        return self._run_id.value

    @property
    def run_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._run_url)
        return self._run_url.value

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

    @property
    def steps(self):
        """
        :type: list of github.WorkflowStep.WorkflowStep
        """
        self._completeIfNotSet(self._steps)
        return self._steps.value

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    def logs_url(self):
        """
        :type: string
        """
        print(f"{self.url}/logs")
        headers, _ = self._requester.requestBlobAndCheck("GET", f"{self.url}/logs")
        return headers["location"]

    def _initAttributes(self):
        self._check_run_url = github.GithubObject.NotSet
        self._completed_at = github.GithubObject.NotSet
        self._conclusion = github.GithubObject.NotSet
        self._head_sha = github.GithubObject.NotSet
        self._html_url = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._node_id = github.GithubObject.NotSet
        self._run_id = github.GithubObject.NotSet
        self._run_url = github.GithubObject.NotSet
        self._started_at = github.GithubObject.NotSet
        self._status = github.GithubObject.NotSet
        self._steps = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "check_run_url" in attributes:  # pragma no branch
            self._check_run_url = self._makeStringAttribute(attributes["check_run_url"])
        if "completed_at" in attributes:  # pragma no branch
            self._completed_at = self._makeDatetimeAttribute(attributes["completed_at"])
        if "conclusion" in attributes:  # pragma no branch
            self._conclusion = self._makeStringAttribute(attributes["conclusion"])
        if "head_sha" in attributes:  # pragma no branch
            self._head_sha = self._makeStringAttribute(attributes["head_sha"])
        if "html_url" in attributes:  # pragma no branch
            self._html_url = self._makeStringAttribute(attributes["html_url"])
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "node_id" in attributes:  # pragma no branch
            self._node_id = self._makeStringAttribute(attributes["node_id"])
        if "run_id" in attributes:  # pragma no branch
            self._run_id = self._makeIntAttribute(attributes["run_id"])
        if "run_url" in attributes:  # pragma no branch
            self._run_url = self._makeStringAttribute(attributes["run_url"])
        if "started_at" in attributes:  # pragma no branch
            self._started_at = self._makeDatetimeAttribute(attributes["started_at"])
        if "status" in attributes:  # pragma no branch
            self._status = self._makeStringAttribute(attributes["status"])
        if "steps" in attributes:  # pragma no branch
            self._steps = self._makeListOfClassesAttribute(
                github.WorkflowStep.WorkflowStep, attributes["steps"]
            )
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
