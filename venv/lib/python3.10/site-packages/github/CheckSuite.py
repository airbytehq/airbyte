############################ Copyrights and license ############################
#                                                                              #
# Copyright 2020 Raju Subramanian <coder@mahesh.net>                           #
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

import github


class CheckSuite(github.GithubObject.CompletableGithubObject):
    """
    This class represents check suites. The reference can be found here https://docs.github.com/en/rest/reference/checks#check-suites
    """

    def __repr__(self):
        return self.get__repr__({"id": self._id.value, "url": self._url.value})

    @property
    def after(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._after)
        return self._after.value

    @property
    def app(self):
        """
        :type: :class:`github.GithubApp.GithubApp`
        """
        self._completeIfNotSet(self._app)
        return self._app.value

    @property
    def before(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._before)
        return self._before.value

    @property
    def check_runs_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._check_runs_url)
        return self._check_runs_url.value

    @property
    def conclusion(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._conclusion)
        return self._conclusion.value

    @property
    def created_at(self):
        """
        :type: datetime.datetime
        """
        self._completeIfNotSet(self._created_at)
        return self._created_at.value

    @property
    def head_branch(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._head_branch)
        return self._head_branch.value

    @property
    def head_commit(self):
        """
        :type: :class:`github.GitCommit.GitCommit`
        """
        self._completeIfNotSet(self._head_commit)
        return self._head_commit.value

    @property
    def head_sha(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._head_sha)
        return self._head_sha.value

    @property
    def id(self):
        """
        :type: int
        """
        self._completeIfNotSet(self._id)
        return self._id.value

    @property
    def latest_check_runs_count(self):
        """
        :type: int
        """
        self._completeIfNotSet(self._latest_check_runs_count)
        return self._latest_check_runs_count.value

    @property
    def pull_requests(self):
        """
        :type: list of :class:`github.PullRequest.PullRequest`
        """
        self._completeIfNotSet(self._pull_requests)
        return self._pull_requests.value

    @property
    def repository(self):
        """
        :type: :class:`github.Repository.Repository`
        """
        self._completeIfNotSet(self._repository)
        return self._repository.value

    @property
    def status(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._status)
        return self._status.value

    @property
    def updated_at(self):
        """
        :type: datetime.datetime
        """
        self._completeIfNotSet(self._updated_at)
        return self._updated_at.value

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    def rerequest(self):
        """
        :calls: `POST /repos/{owner}/{repo}/check-suites/{check_suite_id}/rerequest <https://docs.github.com/en/rest/reference/checks#rerequest-a-check-suite>`_
        :rtype: bool
        """
        request_headers = {"Accept": "application/vnd.github.v3+json"}
        status, _, _ = self._requester.requestJson(
            "POST", f"{self.url}/rerequest", headers=request_headers
        )
        return status == 201

    def get_check_runs(
        self,
        check_name=github.GithubObject.NotSet,
        status=github.GithubObject.NotSet,
        filter=github.GithubObject.NotSet,
    ):
        """
        :calls: `GET /repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs <https://docs.github.com/en/rest/reference/checks#list-check-runs-in-a-check-suite>`_
        :param check_name: string
        :param status: string
        :param filter: string
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.CheckRun.CheckRun`
        """
        assert check_name is github.GithubObject.NotSet or isinstance(
            check_name, str
        ), check_name
        assert status is github.GithubObject.NotSet or isinstance(status, str), status
        assert filter is github.GithubObject.NotSet or isinstance(filter, str), filter
        url_parameters = dict()
        if check_name is not github.GithubObject.NotSet:
            url_parameters["check_name"] = check_name
        if status is not github.GithubObject.NotSet:
            url_parameters["status"] = status
        if filter is not github.GithubObject.NotSet:
            url_parameters["filter"] = filter
        return github.PaginatedList.PaginatedList(
            github.CheckRun.CheckRun,
            self._requester,
            f"{self.url}/check-runs",
            url_parameters,
            headers={"Accept": "application/vnd.github.v3+json"},
            list_item="check_runs",
        )

    def _initAttributes(self):
        self._after = github.GithubObject.NotSet
        self._app = github.GithubObject.NotSet
        self._before = github.GithubObject.NotSet
        self._check_runs_url = github.GithubObject.NotSet
        self._conclusion = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._head_branch = github.GithubObject.NotSet
        self._head_commit = github.GithubObject.NotSet
        self._head_sha = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._latest_check_runs_count = github.GithubObject.NotSet
        self._pull_requests = github.GithubObject.NotSet
        self._repository = github.GithubObject.NotSet
        self._status = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "after" in attributes:  # pragma no branch
            self._after = self._makeStringAttribute(attributes["after"])
        if "app" in attributes:  # pragma no branch
            self._app = self._makeClassAttribute(
                github.GithubApp.GithubApp, attributes["app"]
            )
        if "before" in attributes:  # pragma no branch
            self._before = self._makeStringAttribute(attributes["before"])
        if "check_runs_url" in attributes:  # pragma no branch
            self._check_runs_url = self._makeStringAttribute(
                attributes["check_runs_url"]
            )
        if "conclusion" in attributes:  # pragma no branch
            self._conclusion = self._makeStringAttribute(attributes["conclusion"])
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "head_branch" in attributes:  # pragma no branch
            self._head_branch = self._makeStringAttribute(attributes["head_branch"])
        if "head_commit" in attributes:  # pragma no branch
            # This JSON swaps the 'sha' attribute for an 'id' attribute.
            # The GitCommit object only looks for 'sha'
            if "id" in attributes["head_commit"]:
                attributes["head_commit"]["sha"] = attributes["head_commit"]["id"]
            self._head_commit = self._makeClassAttribute(
                github.GitCommit.GitCommit, attributes["head_commit"]
            )
        if "head_sha" in attributes:  # pragma no branch
            self._head_sha = self._makeStringAttribute(attributes["head_sha"])
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "latest_check_runs_count" in attributes:  # pragma no branch
            self._latest_check_runs_count = self._makeIntAttribute(
                attributes["latest_check_runs_count"]
            )
        if "pull_requests" in attributes:  # pragma no branch
            self._pull_requests = self._makeListOfClassesAttribute(
                github.PullRequest.PullRequest, attributes["pull_requests"]
            )
        if "repository" in attributes:  # pragma no branch
            self._repository = self._makeClassAttribute(
                github.Repository.Repository, attributes["repository"]
            )
        if "status" in attributes:  # pragma no branch
            self._status = self._makeStringAttribute(attributes["status"])
        if "updated_at" in attributes:  # pragma no branch
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
