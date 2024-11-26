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

import datetime

import github.CheckRunAnnotation
import github.CheckRunOutput
import github.GithubApp
import github.GithubObject
import github.PaginatedList
import github.PullRequest


class CheckRun(github.GithubObject.CompletableGithubObject):
    """
    This class represents check runs.
    The reference can be found here https://docs.github.com/en/rest/reference/checks#check-runs
    """

    def __repr__(self):
        return self.get__repr__(
            {"id": self._id.value, "conclusion": self._conclusion.value}
        )

    @property
    def app(self):
        """
        :type: :class:`github.GithubApp.GithubApp`
        """
        self._completeIfNotSet(self._app)
        return self._app.value

    @property
    def check_suite_id(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._check_suite_id)
        return self._check_suite_id.value

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
    def details_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._details_url)
        return self._details_url.value

    @property
    def external_id(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._external_id)
        return self._external_id.value

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
        :type: integer
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
    def output(self):
        """
        :type: :class:`github.CheckRunOutput.CheckRunOutput`
        """
        self._completeIfNotSet(self._output)
        return self._output.value

    @property
    def pull_requests(self):
        """
        :type: list of :class:`github.PullRequest.PullRequest`
        """
        self._completeIfNotSet(self._pull_requests)
        return self._pull_requests.value

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
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    def get_annotations(self):
        """
        :calls: `GET /repos/{owner}/{repo}/check-runs/{check_run_id}/annotations <https://docs.github.com/en/rest/reference/checks#list-check-run-annotations>`_
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.CheckRunAnnotation.CheckRunAnnotation`
        """
        return github.PaginatedList.PaginatedList(
            github.CheckRunAnnotation.CheckRunAnnotation,
            self._requester,
            f"{self.url}/annotations",
            None,
            headers={"Accept": "application/vnd.github.v3+json"},
        )

    def edit(
        self,
        name=github.GithubObject.NotSet,
        head_sha=github.GithubObject.NotSet,
        details_url=github.GithubObject.NotSet,
        external_id=github.GithubObject.NotSet,
        status=github.GithubObject.NotSet,
        started_at=github.GithubObject.NotSet,
        conclusion=github.GithubObject.NotSet,
        completed_at=github.GithubObject.NotSet,
        output=github.GithubObject.NotSet,
        actions=github.GithubObject.NotSet,
    ):
        """
        :calls: `PATCH /repos/{owner}/{repo}/check-runs/{check_run_id} <https://docs.github.com/en/rest/reference/checks#update-a-check-run>`_
        :param name: string
        :param head_sha: string
        :param details_url: string
        :param external_id: string
        :param status: string
        :param started_at: datetime.datetime
        :param conclusion: string
        :param completed_at: datetime.datetime
        :param output: dict
        :param actions: list of dict
        :rtype: None
        """
        assert name is github.GithubObject.NotSet or isinstance(name, str), name
        assert head_sha is github.GithubObject.NotSet or isinstance(
            head_sha, str
        ), head_sha
        assert details_url is github.GithubObject.NotSet or isinstance(
            details_url, str
        ), details_url
        assert external_id is github.GithubObject.NotSet or isinstance(
            external_id, str
        ), external_id
        assert status is github.GithubObject.NotSet or isinstance(status, str), status
        assert started_at is github.GithubObject.NotSet or isinstance(
            started_at, datetime.datetime
        ), started_at
        assert conclusion is github.GithubObject.NotSet or isinstance(
            conclusion, str
        ), conclusion
        assert completed_at is github.GithubObject.NotSet or isinstance(
            completed_at, datetime.datetime
        ), completed_at
        assert output is github.GithubObject.NotSet or isinstance(output, dict), output
        assert actions is github.GithubObject.NotSet or all(
            isinstance(element, dict) for element in actions
        ), actions

        post_parameters = dict()
        if name is not github.GithubObject.NotSet:
            post_parameters["name"] = name
        if head_sha is not github.GithubObject.NotSet:
            post_parameters["head_sha"] = head_sha
        if details_url is not github.GithubObject.NotSet:
            post_parameters["details_url"] = details_url
        if external_id is not github.GithubObject.NotSet:
            post_parameters["external_id"] = external_id
        if status is not github.GithubObject.NotSet:
            post_parameters["status"] = status
        if started_at is not github.GithubObject.NotSet:
            post_parameters["started_at"] = started_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        if completed_at is not github.GithubObject.NotSet:
            post_parameters["completed_at"] = completed_at.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        if conclusion is not github.GithubObject.NotSet:
            post_parameters["conclusion"] = conclusion
        if output is not github.GithubObject.NotSet:
            post_parameters["output"] = output
        if actions is not github.GithubObject.NotSet:
            post_parameters["actions"] = actions

        headers, data = self._requester.requestJsonAndCheck(
            "PATCH", self.url, input=post_parameters
        )
        self._useAttributes(data)

    def _initAttributes(self):
        self._app = github.GithubObject.NotSet
        self._check_suite_id = github.GithubObject.NotSet
        self._completed_at = github.GithubObject.NotSet
        self._conclusion = github.GithubObject.NotSet
        self._details_url = github.GithubObject.NotSet
        self._external_id = github.GithubObject.NotSet
        self._head_sha = github.GithubObject.NotSet
        self._html_url = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._node_id = github.GithubObject.NotSet
        self._output = github.GithubObject.NotSet
        self._pull_requests = github.GithubObject.NotSet
        self._started_at = github.GithubObject.NotSet
        self._status = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "app" in attributes:  # pragma no branch
            self._app = self._makeClassAttribute(
                github.GithubApp.GithubApp, attributes["app"]
            )
        # This only gives us a dictionary with `id` attribute of `check_suite`
        if (
            "check_suite" in attributes and "id" in attributes["check_suite"]
        ):  # pragma no branch
            self._check_suite_id = self._makeIntAttribute(
                attributes["check_suite"]["id"]
            )
        if "completed_at" in attributes:  # pragma no branch
            self._completed_at = self._makeDatetimeAttribute(attributes["completed_at"])
        if "conclusion" in attributes:  # pragma no branch
            self._conclusion = self._makeStringAttribute(attributes["conclusion"])
        if "details_url" in attributes:  # pragma no branch
            self._details_url = self._makeStringAttribute(attributes["details_url"])
        if "external_id" in attributes:  # pragma no branch
            self._external_id = self._makeStringAttribute(attributes["external_id"])
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
        if "output" in attributes:  # pragma no branch
            self._output = self._makeClassAttribute(
                github.CheckRunOutput.CheckRunOutput, attributes["output"]
            )
        if "pull_requests" in attributes:  # pragma no branch
            self._pull_requests = self._makeListOfClassesAttribute(
                github.PullRequest.PullRequest, attributes["pull_requests"]
            )
        if "started_at" in attributes:  # pragma no branch
            self._started_at = self._makeDatetimeAttribute(attributes["started_at"])
        if "status" in attributes:  # pragma no branch
            self._status = self._makeStringAttribute(attributes["status"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
