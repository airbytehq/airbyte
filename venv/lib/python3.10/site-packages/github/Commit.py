############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2013 martinqt <m.ki2@laposte.net>                                  #
# Copyright 2014 Andy Casey <acasey@mso.anu.edu.au>                            #
# Copyright 2014 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2016 Jannis Gebauer <ja.geb@me.com>                                #
# Copyright 2016 John Eskew <jeskew@edx.org>                                   #
# Copyright 2016 Peter Buckley <dx-pbuckley@users.noreply.github.com>          #
# Copyright 2018 sfdye <tsfdye@gmail.com>                                      #
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

import github.CheckRun
import github.CheckSuite
import github.CommitCombinedStatus
import github.CommitComment
import github.CommitStats
import github.CommitStatus
import github.File
import github.GitCommit
import github.GithubObject
import github.NamedUser
import github.PaginatedList


class Commit(github.GithubObject.CompletableGithubObject):
    """
    This class represents Commits. The reference can be found here https://docs.github.com/en/rest/reference/git#commits
    """

    def __repr__(self):
        return self.get__repr__({"sha": self._sha.value})

    @property
    def author(self):
        """
        :type: :class:`github.NamedUser.NamedUser`
        """
        self._completeIfNotSet(self._author)
        return self._author.value

    @property
    def comments_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._comments_url)
        return self._comments_url.value

    @property
    def commit(self):
        """
        :type: :class:`github.GitCommit.GitCommit`
        """
        self._completeIfNotSet(self._commit)
        return self._commit.value

    @property
    def committer(self):
        """
        :type: :class:`github.NamedUser.NamedUser`
        """
        self._completeIfNotSet(self._committer)
        return self._committer.value

    @property
    def files(self):
        """
        :type: list of :class:`github.File.File`
        """
        self._completeIfNotSet(self._files)
        return self._files.value

    @property
    def html_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._html_url)
        return self._html_url.value

    @property
    def parents(self):
        """
        :type: list of :class:`github.Commit.Commit`
        """
        self._completeIfNotSet(self._parents)
        return self._parents.value

    @property
    def sha(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._sha)
        return self._sha.value

    @property
    def stats(self):
        """
        :type: :class:`github.CommitStats.CommitStats`
        """
        self._completeIfNotSet(self._stats)
        return self._stats.value

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    def create_comment(
        self,
        body,
        line=github.GithubObject.NotSet,
        path=github.GithubObject.NotSet,
        position=github.GithubObject.NotSet,
    ):
        """
        :calls: `POST /repos/{owner}/{repo}/commits/{sha}/comments <https://docs.github.com/en/rest/reference/repos#comments>`_
        :param body: string
        :param line: integer
        :param path: string
        :param position: integer
        :rtype: :class:`github.CommitComment.CommitComment`
        """
        assert isinstance(body, str), body
        assert line is github.GithubObject.NotSet or isinstance(line, int), line
        assert path is github.GithubObject.NotSet or isinstance(path, str), path
        assert position is github.GithubObject.NotSet or isinstance(
            position, int
        ), position
        post_parameters = {
            "body": body,
        }
        if line is not github.GithubObject.NotSet:
            post_parameters["line"] = line
        if path is not github.GithubObject.NotSet:
            post_parameters["path"] = path
        if position is not github.GithubObject.NotSet:
            post_parameters["position"] = position
        headers, data = self._requester.requestJsonAndCheck(
            "POST", f"{self.url}/comments", input=post_parameters
        )
        return github.CommitComment.CommitComment(
            self._requester, headers, data, completed=True
        )

    def create_status(
        self,
        state,
        target_url=github.GithubObject.NotSet,
        description=github.GithubObject.NotSet,
        context=github.GithubObject.NotSet,
    ):
        """
        :calls: `POST /repos/{owner}/{repo}/statuses/{sha} <https://docs.github.com/en/rest/reference/repos#statuses>`_
        :param state: string
        :param target_url: string
        :param description: string
        :param context: string
        :rtype: :class:`github.CommitStatus.CommitStatus`
        """
        assert isinstance(state, str), state
        assert target_url is github.GithubObject.NotSet or isinstance(
            target_url, str
        ), target_url
        assert description is github.GithubObject.NotSet or isinstance(
            description, str
        ), description
        assert context is github.GithubObject.NotSet or isinstance(
            context, str
        ), context
        post_parameters = {
            "state": state,
        }
        if target_url is not github.GithubObject.NotSet:
            post_parameters["target_url"] = target_url
        if description is not github.GithubObject.NotSet:
            post_parameters["description"] = description
        if context is not github.GithubObject.NotSet:
            post_parameters["context"] = context
        headers, data = self._requester.requestJsonAndCheck(
            "POST",
            f"{self._parentUrl(self._parentUrl(self.url))}/statuses/{self.sha}",
            input=post_parameters,
        )
        return github.CommitStatus.CommitStatus(
            self._requester, headers, data, completed=True
        )

    def get_comments(self):
        """
        :calls: `GET /repos/{owner}/{repo}/commits/{sha}/comments <https://docs.github.com/en/rest/reference/repos#comments>`_
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.CommitComment.CommitComment`
        """
        return github.PaginatedList.PaginatedList(
            github.CommitComment.CommitComment,
            self._requester,
            f"{self.url}/comments",
            None,
        )

    def get_statuses(self):
        """
        :calls: `GET /repos/{owner}/{repo}/statuses/{ref} <https://docs.github.com/en/rest/reference/repos#statuses>`_
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.CommitStatus.CommitStatus`
        """
        return github.PaginatedList.PaginatedList(
            github.CommitStatus.CommitStatus,
            self._requester,
            f"{self._parentUrl(self._parentUrl(self.url))}/statuses/{self.sha}",
            None,
        )

    def get_combined_status(self):
        """
        :calls: `GET /repos/{owner}/{repo}/commits/{ref}/status/ <http://docs.github.com/en/rest/reference/repos#statuses>`_
        :rtype: :class:`github.CommitCombinedStatus.CommitCombinedStatus`
        """
        headers, data = self._requester.requestJsonAndCheck("GET", f"{self.url}/status")
        return github.CommitCombinedStatus.CommitCombinedStatus(
            self._requester, headers, data, completed=True
        )

    def get_pulls(self):
        """
        :calls: `GET /repos/{owner}/{repo}/commits/{sha}/pulls <https://docs.github.com/en/rest/reference/repos#list-pull-requests-associated-with-a-commit>`_
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.PullRequest.PullRequest`
        """
        return github.PaginatedList.PaginatedList(
            github.PullRequest.PullRequest,
            self._requester,
            f"{self.url}/pulls",
            None,
            headers={"Accept": "application/vnd.github.groot-preview+json"},
        )

    def get_check_runs(
        self,
        check_name=github.GithubObject.NotSet,
        status=github.GithubObject.NotSet,
        filter=github.GithubObject.NotSet,
    ):
        """
        :calls: `GET /repos/{owner}/{repo}/commits/{sha}/check-runs <https://docs.github.com/en/rest/reference/checks#list-check-runs-for-a-git-reference>`_
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

    def get_check_suites(
        self, app_id=github.GithubObject.NotSet, check_name=github.GithubObject.NotSet
    ):
        """
        :class: `GET /repos/{owner}/{repo}/commits/{ref}/check-suites <https://docs.github.com/en/rest/reference/checks#list-check-suites-for-a-git-reference>`_
        :param app_id: int
        :param check_name: string
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.CheckSuite.CheckSuite`
        """
        assert app_id is github.GithubObject.NotSet or isinstance(app_id, int), app_id
        assert check_name is github.GithubObject.NotSet or isinstance(
            check_name, str
        ), check_name
        parameters = dict()
        if app_id is not github.GithubObject.NotSet:
            parameters["app_id"] = app_id
        if check_name is not github.GithubObject.NotSet:
            parameters["check_name"] = check_name
        request_headers = {"Accept": "application/vnd.github.v3+json"}
        return github.PaginatedList.PaginatedList(
            github.CheckSuite.CheckSuite,
            self._requester,
            f"{self.url}/check-suites",
            parameters,
            headers=request_headers,
            list_item="check_suites",
        )

    @property
    def _identity(self):
        return self.sha

    def _initAttributes(self):
        self._author = github.GithubObject.NotSet
        self._comments_url = github.GithubObject.NotSet
        self._commit = github.GithubObject.NotSet
        self._committer = github.GithubObject.NotSet
        self._files = github.GithubObject.NotSet
        self._html_url = github.GithubObject.NotSet
        self._parents = github.GithubObject.NotSet
        self._sha = github.GithubObject.NotSet
        self._stats = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "author" in attributes:  # pragma no branch
            self._author = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["author"]
            )
        if "comments_url" in attributes:  # pragma no branch
            self._comments_url = self._makeStringAttribute(attributes["comments_url"])
        if "commit" in attributes:  # pragma no branch
            self._commit = self._makeClassAttribute(
                github.GitCommit.GitCommit, attributes["commit"]
            )
        if "committer" in attributes:  # pragma no branch
            self._committer = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["committer"]
            )
        if "files" in attributes:  # pragma no branch
            self._files = self._makeListOfClassesAttribute(
                github.File.File, attributes["files"]
            )
        if "html_url" in attributes:  # pragma no branch
            self._html_url = self._makeStringAttribute(attributes["html_url"])
        if "parents" in attributes:  # pragma no branch
            self._parents = self._makeListOfClassesAttribute(
                Commit, attributes["parents"]
            )
        if "sha" in attributes:  # pragma no branch
            self._sha = self._makeStringAttribute(attributes["sha"])
        if "stats" in attributes:  # pragma no branch
            self._stats = self._makeClassAttribute(
                github.CommitStats.CommitStats, attributes["stats"]
            )
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
