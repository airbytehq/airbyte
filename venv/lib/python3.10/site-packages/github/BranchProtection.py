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
import github.NamedUser
import github.RequiredPullRequestReviews
import github.RequiredStatusChecks
import github.Team


class BranchProtection(github.GithubObject.CompletableGithubObject):
    """
    This class represents Branch Protection. The reference can be found here https://docs.github.com/en/rest/reference/repos#get-branch-protection
    """

    def __repr__(self):
        return self.get__repr__({"url": self._url.value})

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    @property
    def required_status_checks(self):
        """
        :type: :class:`github.RequiredStatusChecks.RequiredStatusChecks`
        """
        self._completeIfNotSet(self._required_status_checks)
        return self._required_status_checks.value

    @property
    def enforce_admins(self):
        """
        :type: bool
        """
        self._completeIfNotSet(self._enforce_admins)
        return self._enforce_admins.value

    @property
    def required_pull_request_reviews(self):
        """
        :type: :class:`github.RequiredPullRequestReviews.RequiredPullRequestReviews`
        """
        self._completeIfNotSet(self._required_pull_request_reviews)
        return self._required_pull_request_reviews.value

    def get_user_push_restrictions(self):
        """
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.NamedUser.NamedUser`
        """
        if self._user_push_restrictions is github.GithubObject.NotSet:
            return None
        return github.PaginatedList.PaginatedList(
            github.NamedUser.NamedUser,
            self._requester,
            self._user_push_restrictions,
            None,
        )

    def get_team_push_restrictions(self):
        """
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.Team.Team`
        """
        if self._team_push_restrictions is github.GithubObject.NotSet:
            return None
        return github.PaginatedList.PaginatedList(
            github.Team.Team, self._requester, self._team_push_restrictions, None
        )

    def _initAttributes(self):
        self._url = github.GithubObject.NotSet
        self._required_status_checks = github.GithubObject.NotSet
        self._enforce_admins = github.GithubObject.NotSet
        self._required_pull_request_reviews = github.GithubObject.NotSet
        self._user_push_restrictions = github.GithubObject.NotSet
        self._team_push_restrictions = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
        if "required_status_checks" in attributes:  # pragma no branch
            self._required_status_checks = self._makeClassAttribute(
                github.RequiredStatusChecks.RequiredStatusChecks,
                attributes["required_status_checks"],
            )
        if "enforce_admins" in attributes:  # pragma no branch
            self._enforce_admins = self._makeBoolAttribute(
                attributes["enforce_admins"]["enabled"]
            )
        if "required_pull_request_reviews" in attributes:  # pragma no branch
            self._required_pull_request_reviews = self._makeClassAttribute(
                github.RequiredPullRequestReviews.RequiredPullRequestReviews,
                attributes["required_pull_request_reviews"],
            )
        if "restrictions" in attributes:  # pragma no branch
            self._user_push_restrictions = attributes["restrictions"]["users_url"]
            self._team_push_restrictions = attributes["restrictions"]["teams_url"]
