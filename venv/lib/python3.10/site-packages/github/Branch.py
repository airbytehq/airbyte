############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2013 martinqt <m.ki2@laposte.net>                                  #
# Copyright 2014 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2015 Kyle Hornberg <khornberg@users.noreply.github.com>            #
# Copyright 2016 Jannis Gebauer <ja.geb@me.com>                                #
# Copyright 2016 Peter Buckley <dx-pbuckley@users.noreply.github.com>          #
# Copyright 2018 Steve Kowalik <steven@wedontsleep.org>                        #
# Copyright 2018 Wan Liuyang <tsfdye@gmail.com>                                #
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

import github.BranchProtection
import github.Commit
import github.GithubObject
import github.RequiredPullRequestReviews
import github.RequiredStatusChecks

from . import Consts


class Branch(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents Branches. The reference can be found here https://docs.github.com/en/rest/reference/repos#branches
    """

    def __repr__(self):
        return self.get__repr__({"name": self._name.value})

    @property
    def commit(self):
        """
        :type: :class:`github.Commit.Commit`
        """
        return self._commit.value

    @property
    def name(self):
        """
        :type: string
        """
        return self._name.value

    @property
    def protected(self):
        """
        :type: bool
        """
        return self._protected.value

    @property
    def protection_url(self):
        """
        :type: string
        """
        return self._protection_url.value

    def _initAttributes(self):
        self._commit = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._protection_url = github.GithubObject.NotSet
        self._protected = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "commit" in attributes:  # pragma no branch
            self._commit = self._makeClassAttribute(
                github.Commit.Commit, attributes["commit"]
            )
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "protection_url" in attributes:  # pragma no branch
            self._protection_url = self._makeStringAttribute(
                attributes["protection_url"]
            )
        if "protected" in attributes:  # pragma no branch
            self._protected = self._makeBoolAttribute(attributes["protected"])

    def get_protection(self):
        """
        :calls: `GET /repos/{owner}/{repo}/branches/{branch}/protection <https://docs.github.com/en/rest/reference/repos#branches>`_
        """
        headers, data = self._requester.requestJsonAndCheck(
            "GET",
            self.protection_url,
            headers={"Accept": Consts.mediaTypeRequireMultipleApprovingReviews},
        )
        return github.BranchProtection.BranchProtection(
            self._requester, headers, data, completed=True
        )

    def edit_protection(
        self,
        strict=github.GithubObject.NotSet,
        contexts=github.GithubObject.NotSet,
        enforce_admins=github.GithubObject.NotSet,
        dismissal_users=github.GithubObject.NotSet,
        dismissal_teams=github.GithubObject.NotSet,
        dismissal_apps=github.GithubObject.NotSet,
        dismiss_stale_reviews=github.GithubObject.NotSet,
        require_code_owner_reviews=github.GithubObject.NotSet,
        required_approving_review_count=github.GithubObject.NotSet,
        user_push_restrictions=github.GithubObject.NotSet,
        team_push_restrictions=github.GithubObject.NotSet,
        app_push_restrictions=github.GithubObject.NotSet,
        required_linear_history=github.GithubObject.NotSet,
        allow_force_pushes=github.GithubObject.NotSet,
        required_conversation_resolution=github.GithubObject.NotSet,
        lock_branch=github.GithubObject.NotSet,
        allow_fork_syncing=github.GithubObject.NotSet,
        users_bypass_pull_request_allowances=github.GithubObject.NotSet,
        teams_bypass_pull_request_allowances=github.GithubObject.NotSet,
        apps_bypass_pull_request_allowances=github.GithubObject.NotSet,
        block_creations=github.GithubObject.NotSet,
    ):
        """
        :calls: `PUT /repos/{owner}/{repo}/branches/{branch}/protection <https://docs.github.com/en/rest/reference/repos#get-branch-protection>`_
        :strict: bool
        :contexts: list of strings
        :enforce_admins: bool
        :dismissal_users: list of strings
        :dismissal_teams: list of strings
        :dismissal_apps: list of strings
        :dismiss_stale_reviews: bool
        :require_code_owner_reviews: bool
        :required_approving_review_count: int
        :user_push_restrictions: list of strings
        :team_push_restrictions: list of strings
        :app_push_restrictions: list of strings
        :required_linear_history: bool
        :allow_force_pushes: bool
        :required_conversation_resolution: bool
        :lock_branch: bool
        :allow_fork_syncing: bool
        :users_bypass_pull_request_allowances: list of strings
        :teams_bypass_pull_request_allowances: list of strings
        :apps_bypass_pull_request_allowances: list of strings
        :block_creations: bool

        NOTE: The GitHub API groups strict and contexts together, both must
        be submitted. Take care to pass both as arguments even if only one is
        changing. Use edit_required_status_checks() to avoid this.
        """
        assert strict is github.GithubObject.NotSet or isinstance(strict, bool), strict
        assert contexts is github.GithubObject.NotSet or all(
            isinstance(element, str) for element in contexts
        ), contexts
        assert enforce_admins is github.GithubObject.NotSet or isinstance(
            enforce_admins, bool
        ), enforce_admins
        assert dismissal_users is github.GithubObject.NotSet or all(
            isinstance(element, str) for element in dismissal_users
        ), dismissal_users
        assert dismissal_teams is github.GithubObject.NotSet or all(
            isinstance(element, str) for element in dismissal_teams
        ), dismissal_teams
        assert dismissal_apps is github.GithubObject.NotSet or all(
            isinstance(element, str) for element in dismissal_apps
        ), dismissal_apps
        assert dismiss_stale_reviews is github.GithubObject.NotSet or isinstance(
            dismiss_stale_reviews, bool
        ), dismiss_stale_reviews
        assert require_code_owner_reviews is github.GithubObject.NotSet or isinstance(
            require_code_owner_reviews, bool
        ), require_code_owner_reviews
        assert (
            required_approving_review_count is github.GithubObject.NotSet
            or isinstance(required_approving_review_count, int)
        ), (required_approving_review_count)
        assert required_linear_history is github.GithubObject.NotSet or isinstance(
            required_linear_history, bool
        ), required_linear_history
        assert allow_force_pushes is github.GithubObject.NotSet or isinstance(
            allow_force_pushes, bool
        ), allow_force_pushes
        assert (
            required_conversation_resolution is github.GithubObject.NotSet
            or isinstance(required_linear_history, bool)
        ), required_conversation_resolution
        assert lock_branch is github.GithubObject.NotSet or isinstance(
            lock_branch, bool
        ), lock_branch
        assert allow_fork_syncing is github.GithubObject.NotSet or isinstance(
            allow_fork_syncing, bool
        ), allow_fork_syncing
        assert (
            users_bypass_pull_request_allowances is github.GithubObject.NotSet
            or all(
                isinstance(element, str)
                for element in users_bypass_pull_request_allowances
            )
        ), (users_bypass_pull_request_allowances)
        assert (
            teams_bypass_pull_request_allowances is github.GithubObject.NotSet
            or all(
                isinstance(element, str)
                for element in teams_bypass_pull_request_allowances
            )
        ), (teams_bypass_pull_request_allowances)
        assert apps_bypass_pull_request_allowances is github.GithubObject.NotSet or all(
            isinstance(element, str) for element in apps_bypass_pull_request_allowances
        ), apps_bypass_pull_request_allowances

        post_parameters = {}
        if (
            strict is not github.GithubObject.NotSet
            or contexts is not github.GithubObject.NotSet
        ):
            if strict is github.GithubObject.NotSet:
                strict = False
            if contexts is github.GithubObject.NotSet:
                contexts = []
            post_parameters["required_status_checks"] = {
                "strict": strict,
                "contexts": contexts,
            }
        else:
            post_parameters["required_status_checks"] = None

        if enforce_admins is not github.GithubObject.NotSet:
            post_parameters["enforce_admins"] = enforce_admins
        else:
            post_parameters["enforce_admins"] = None

        if (
            dismissal_users is not github.GithubObject.NotSet
            or dismissal_teams is not github.GithubObject.NotSet
            or dismissal_apps is not github.GithubObject.NotSet
            or dismiss_stale_reviews is not github.GithubObject.NotSet
            or require_code_owner_reviews is not github.GithubObject.NotSet
            or required_approving_review_count is not github.GithubObject.NotSet
            or users_bypass_pull_request_allowances is not github.GithubObject.NotSet
            or teams_bypass_pull_request_allowances is not github.GithubObject.NotSet
            or apps_bypass_pull_request_allowances is not github.GithubObject.NotSet
        ):
            post_parameters["required_pull_request_reviews"] = {}
            if dismiss_stale_reviews is not github.GithubObject.NotSet:
                post_parameters["required_pull_request_reviews"][
                    "dismiss_stale_reviews"
                ] = dismiss_stale_reviews
            if require_code_owner_reviews is not github.GithubObject.NotSet:
                post_parameters["required_pull_request_reviews"][
                    "require_code_owner_reviews"
                ] = require_code_owner_reviews
            if required_approving_review_count is not github.GithubObject.NotSet:
                post_parameters["required_pull_request_reviews"][
                    "required_approving_review_count"
                ] = required_approving_review_count

            if (
                dismissal_users is not github.GithubObject.NotSet
                or dismissal_teams is not github.GithubObject.NotSet
                or dismissal_apps is not github.GithubObject.NotSet
            ):
                post_parameters["required_pull_request_reviews"][
                    "dismissal_restrictions"
                ] = {}

            if dismissal_users is not github.GithubObject.NotSet:
                post_parameters["required_pull_request_reviews"][
                    "dismissal_restrictions"
                ]["users"] = dismissal_users
            if dismissal_teams is not github.GithubObject.NotSet:
                post_parameters["required_pull_request_reviews"][
                    "dismissal_restrictions"
                ]["teams"] = dismissal_teams
            if dismissal_apps is not github.GithubObject.NotSet:
                post_parameters["required_pull_request_reviews"][
                    "dismissal_restrictions"
                ]["apps"] = dismissal_apps

            if (
                users_bypass_pull_request_allowances is not github.GithubObject.NotSet
                or teams_bypass_pull_request_allowances
                is not github.GithubObject.NotSet
                or apps_bypass_pull_request_allowances is not github.GithubObject.NotSet
            ):
                post_parameters["required_pull_request_reviews"][
                    "bypass_pull_request_allowances"
                ] = {}
                if users_bypass_pull_request_allowances is github.GithubObject.NotSet:
                    users_bypass_pull_request_allowances = []
                if teams_bypass_pull_request_allowances is github.GithubObject.NotSet:
                    teams_bypass_pull_request_allowances = []
                if apps_bypass_pull_request_allowances is github.GithubObject.NotSet:
                    apps_bypass_pull_request_allowances = []
                post_parameters["required_pull_request_reviews"][
                    "bypass_pull_request_allowances"
                ] = {
                    "users": users_bypass_pull_request_allowances,
                    "teams": teams_bypass_pull_request_allowances,
                    "apps": apps_bypass_pull_request_allowances,
                }
            else:
                post_parameters["required_pull_request_reviews"][
                    "bypass_pull_request_allowances"
                ] = None
        else:
            post_parameters["required_pull_request_reviews"] = None
        if (
            user_push_restrictions is not github.GithubObject.NotSet
            or team_push_restrictions is not github.GithubObject.NotSet
            or app_push_restrictions is not github.GithubObject.NotSet
        ):
            if user_push_restrictions is github.GithubObject.NotSet:
                user_push_restrictions = []
            if team_push_restrictions is github.GithubObject.NotSet:
                team_push_restrictions = []
            if app_push_restrictions is github.GithubObject.NotSet:
                app_push_restrictions = []
            post_parameters["restrictions"] = {
                "users": user_push_restrictions,
                "teams": team_push_restrictions,
                "apps": app_push_restrictions,
            }
        else:
            post_parameters["restrictions"] = None
        if required_linear_history is not github.GithubObject.NotSet:
            post_parameters["required_linear_history"] = required_linear_history
        else:
            post_parameters["required_linear_history"] = None
        if allow_force_pushes is not github.GithubObject.NotSet:
            post_parameters["allow_force_pushes"] = allow_force_pushes
        else:
            post_parameters["allow_force_pushes"] = None
        if required_conversation_resolution is not github.GithubObject.NotSet:
            post_parameters[
                "required_conversation_resolution"
            ] = required_conversation_resolution
        else:
            post_parameters["required_conversation_resolution"] = None
        if lock_branch is not github.GithubObject.NotSet:
            post_parameters["lock_branch"] = lock_branch
        else:
            post_parameters["lock_branch"] = None
        if allow_fork_syncing is not github.GithubObject.NotSet:
            post_parameters["allow_fork_syncing"] = allow_fork_syncing
        else:
            post_parameters["allow_fork_syncing"] = None
        if block_creations is not github.GithubObject.NotSet:
            post_parameters["block_creations"] = block_creations
        else:
            post_parameters["block_creations"] = None

        headers, data = self._requester.requestJsonAndCheck(
            "PUT",
            self.protection_url,
            headers={"Accept": Consts.mediaTypeRequireMultipleApprovingReviews},
            input=post_parameters,
        )

    def remove_protection(self):
        """
        :calls: `DELETE /repos/{owner}/{repo}/branches/{branch}/protection <https://docs.github.com/en/rest/reference/repos#branches>`_
        """
        headers, data = self._requester.requestJsonAndCheck(
            "DELETE",
            self.protection_url,
        )

    def get_required_status_checks(self):
        """
        :calls: `GET /repos/{owner}/{repo}/branches/{branch}/protection/required_status_checks <https://docs.github.com/en/rest/reference/repos#branches>`_
        :rtype: :class:`github.RequiredStatusChecks.RequiredStatusChecks`
        """
        headers, data = self._requester.requestJsonAndCheck(
            "GET", f"{self.protection_url}/required_status_checks"
        )
        return github.RequiredStatusChecks.RequiredStatusChecks(
            self._requester, headers, data, completed=True
        )

    def edit_required_status_checks(
        self, strict=github.GithubObject.NotSet, contexts=github.GithubObject.NotSet
    ):
        """
        :calls: `PATCH /repos/{owner}/{repo}/branches/{branch}/protection/required_status_checks <https://docs.github.com/en/rest/reference/repos#branches>`_
        :strict: bool
        :contexts: list of strings
        """
        assert strict is github.GithubObject.NotSet or isinstance(strict, bool), strict
        assert contexts is github.GithubObject.NotSet or all(
            isinstance(element, str) for element in contexts
        ), contexts

        post_parameters = {}
        if strict is not github.GithubObject.NotSet:
            post_parameters["strict"] = strict
        if contexts is not github.GithubObject.NotSet:
            post_parameters["contexts"] = contexts
        headers, data = self._requester.requestJsonAndCheck(
            "PATCH",
            f"{self.protection_url}/required_status_checks",
            input=post_parameters,
        )

    def remove_required_status_checks(self):
        """
        :calls: `DELETE /repos/{owner}/{repo}/branches/{branch}/protection/required_status_checks <https://docs.github.com/en/rest/reference/repos#branches>`_
        """
        headers, data = self._requester.requestJsonAndCheck(
            "DELETE",
            f"{self.protection_url}/required_status_checks",
        )

    def get_required_pull_request_reviews(self):
        """
        :calls: `GET /repos/{owner}/{repo}/branches/{branch}/protection/required_pull_request_reviews <https://docs.github.com/en/rest/reference/repos#branches>`_
        :rtype: :class:`github.RequiredPullRequestReviews.RequiredPullRequestReviews`
        """
        headers, data = self._requester.requestJsonAndCheck(
            "GET",
            f"{self.protection_url}/required_pull_request_reviews",
            headers={"Accept": Consts.mediaTypeRequireMultipleApprovingReviews},
        )
        return github.RequiredPullRequestReviews.RequiredPullRequestReviews(
            self._requester, headers, data, completed=True
        )

    def edit_required_pull_request_reviews(
        self,
        dismissal_users=github.GithubObject.NotSet,
        dismissal_teams=github.GithubObject.NotSet,
        dismissal_apps=github.GithubObject.NotSet,
        dismiss_stale_reviews=github.GithubObject.NotSet,
        require_code_owner_reviews=github.GithubObject.NotSet,
        required_approving_review_count=github.GithubObject.NotSet,
    ):
        """
        :calls: `PATCH /repos/{owner}/{repo}/branches/{branch}/protection/required_pull_request_reviews <https://docs.github.com/en/rest/reference/repos#branches>`_
        :dismissal_users: list of strings
        :dismissal_teams: list of strings
        :dismissal_apps: list of strings
        :dismiss_stale_reviews: bool
        :require_code_owner_reviews: bool
        :required_approving_review_count: int
        """
        assert dismissal_users is github.GithubObject.NotSet or all(
            isinstance(element, str) for element in dismissal_users
        ), dismissal_users
        assert dismissal_teams is github.GithubObject.NotSet or all(
            isinstance(element, str) for element in dismissal_teams
        ), dismissal_teams
        assert dismiss_stale_reviews is github.GithubObject.NotSet or isinstance(
            dismiss_stale_reviews, bool
        ), dismiss_stale_reviews
        assert require_code_owner_reviews is github.GithubObject.NotSet or isinstance(
            require_code_owner_reviews, bool
        ), require_code_owner_reviews
        assert (
            required_approving_review_count is github.GithubObject.NotSet
            or isinstance(required_approving_review_count, int)
        ), (required_approving_review_count)

        post_parameters = {}
        if (
            dismissal_users is not github.GithubObject.NotSet
            or dismissal_teams is not github.GithubObject.NotSet
            or dismissal_apps is not github.GithubObject.NotSet
        ):
            post_parameters["dismissal_restrictions"] = {}

        if dismissal_users is not github.GithubObject.NotSet:
            post_parameters["dismissal_restrictions"]["users"] = dismissal_users
        if dismissal_teams is not github.GithubObject.NotSet:
            post_parameters["dismissal_restrictions"]["teams"] = dismissal_teams
        if dismissal_apps is not github.GithubObject.NotSet:
            post_parameters["dismissal_restrictions"]["apps"] = dismissal_apps

        if dismiss_stale_reviews is not github.GithubObject.NotSet:
            post_parameters["dismiss_stale_reviews"] = dismiss_stale_reviews
        if require_code_owner_reviews is not github.GithubObject.NotSet:
            post_parameters["require_code_owner_reviews"] = require_code_owner_reviews
        if required_approving_review_count is not github.GithubObject.NotSet:
            post_parameters[
                "required_approving_review_count"
            ] = required_approving_review_count
        headers, data = self._requester.requestJsonAndCheck(
            "PATCH",
            f"{self.protection_url}/required_pull_request_reviews",
            headers={"Accept": Consts.mediaTypeRequireMultipleApprovingReviews},
            input=post_parameters,
        )

    def remove_required_pull_request_reviews(self):
        """
        :calls: `DELETE /repos/{owner}/{repo}/branches/{branch}/protection/required_pull_request_reviews <https://docs.github.com/en/rest/reference/repos#branches>`_
        """
        headers, data = self._requester.requestJsonAndCheck(
            "DELETE",
            f"{self.protection_url}/required_pull_request_reviews",
        )

    def get_admin_enforcement(self):
        """
        :calls: `GET /repos/{owner}/{repo}/branches/{branch}/protection/enforce_admins <https://docs.github.com/en/rest/reference/repos#branches>`_
        :rtype: bool
        """
        headers, data = self._requester.requestJsonAndCheck(
            "GET", f"{self.protection_url}/enforce_admins"
        )
        return data["enabled"]

    def set_admin_enforcement(self):
        """
        :calls: `POST /repos/{owner}/{repo}/branches/{branch}/protection/enforce_admins <https://docs.github.com/en/rest/reference/repos#branches>`_
        """
        headers, data = self._requester.requestJsonAndCheck(
            "POST", f"{self.protection_url}/enforce_admins"
        )

    def remove_admin_enforcement(self):
        """
        :calls: `DELETE /repos/{owner}/{repo}/branches/{branch}/protection/enforce_admins <https://docs.github.com/en/rest/reference/repos#branches>`_
        """
        headers, data = self._requester.requestJsonAndCheck(
            "DELETE", f"{self.protection_url}/enforce_admins"
        )

    def get_user_push_restrictions(self):
        """
        :calls: `GET /repos/{owner}/{repo}/branches/{branch}/protection/restrictions/users <https://docs.github.com/en/rest/reference/repos#branches>`_
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.NamedUser.NamedUser`
        """
        return github.PaginatedList.PaginatedList(
            github.NamedUser.NamedUser,
            self._requester,
            f"{self.protection_url}/restrictions/users",
            None,
        )

    def get_team_push_restrictions(self):
        """
        :calls: `GET /repos/{owner}/{repo}/branches/{branch}/protection/restrictions/teams <https://docs.github.com/en/rest/reference/repos#branches>`_
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.Team.Team`
        """
        return github.PaginatedList.PaginatedList(
            github.Team.Team,
            self._requester,
            f"{self.protection_url}/restrictions/teams",
            None,
        )

    def add_user_push_restrictions(self, *users):
        """
        :calls: `POST /repos/{owner}/{repo}/branches/{branch}/protection/restrictions/users <https://docs.github.com/en/rest/reference/repos#branches>`_
        :users: list of strings (user names)
        """
        assert all(isinstance(element, str) for element in users), users

        headers, data = self._requester.requestJsonAndCheck(
            "POST", f"{self.protection_url}/restrictions/users", input=users
        )

    def replace_user_push_restrictions(self, *users):
        """
        :calls: `PUT /repos/{owner}/{repo}/branches/{branch}/protection/restrictions/users <https://docs.github.com/en/rest/reference/repos#branches>`_
        :users: list of strings (user names)
        """
        assert all(isinstance(element, str) for element in users), users

        headers, data = self._requester.requestJsonAndCheck(
            "PUT", f"{self.protection_url}/restrictions/users", input=users
        )

    def remove_user_push_restrictions(self, *users):
        """
        :calls: `DELETE /repos/{owner}/{repo}/branches/{branch}/protection/restrictions/users <https://docs.github.com/en/rest/reference/repos#branches>`_
        :users: list of strings (user names)
        """
        assert all(isinstance(element, str) for element in users), users

        headers, data = self._requester.requestJsonAndCheck(
            "DELETE", f"{self.protection_url}/restrictions/users", input=users
        )

    def add_team_push_restrictions(self, *teams):
        """
        :calls: `POST /repos/{owner}/{repo}/branches/{branch}/protection/restrictions/teams <https://docs.github.com/en/rest/reference/repos#branches>`_
        :teams: list of strings (team slugs)
        """
        assert all(isinstance(element, str) for element in teams), teams

        headers, data = self._requester.requestJsonAndCheck(
            "POST", f"{self.protection_url}/restrictions/teams", input=teams
        )

    def replace_team_push_restrictions(self, *teams):
        """
        :calls: `PUT /repos/{owner}/{repo}/branches/{branch}/protection/restrictions/teams <https://docs.github.com/en/rest/reference/repos#branches>`_
        :teams: list of strings (team slugs)
        """
        assert all(isinstance(element, str) for element in teams), teams

        headers, data = self._requester.requestJsonAndCheck(
            "PUT", f"{self.protection_url}/restrictions/teams", input=teams
        )

    def remove_team_push_restrictions(self, *teams):
        """
        :calls: `DELETE /repos/{owner}/{repo}/branches/{branch}/protection/restrictions/teams <https://docs.github.com/en/rest/reference/repos#branches>`_
        :teams: list of strings (team slugs)
        """
        assert all(isinstance(element, str) for element in teams), teams

        headers, data = self._requester.requestJsonAndCheck(
            "DELETE", f"{self.protection_url}/restrictions/teams", input=teams
        )

    def remove_push_restrictions(self):
        """
        :calls: `DELETE /repos/{owner}/{repo}/branches/{branch}/protection/restrictions <https://docs.github.com/en/rest/reference/repos#branches>`_
        """
        headers, data = self._requester.requestJsonAndCheck(
            "DELETE", f"{self.protection_url}/restrictions"
        )

    def get_required_signatures(self):
        """
        :calls: `GET /repos/{owner}/{repo}/branches/{branch}/protection/required_signatures <https://docs.github.com/en/rest/reference/repos#branches>`_
        """
        headers, data = self._requester.requestJsonAndCheck(
            "GET",
            f"{self.protection_url}/required_signatures",
            headers={"Accept": Consts.signaturesProtectedBranchesPreview},
        )
        return data["enabled"]

    def add_required_signatures(self):
        """
        :calls: `POST /repos/{owner}/{repo}/branches/{branch}/protection/required_signatures <https://docs.github.com/en/rest/reference/repos#branches>`_
        """
        headers, data = self._requester.requestJsonAndCheck(
            "POST",
            f"{self.protection_url}/required_signatures",
            headers={"Accept": Consts.signaturesProtectedBranchesPreview},
        )

    def remove_required_signatures(self):
        """
        :calls: `DELETE /repos/{owner}/{repo}/branches/{branch}/protection/required_signatures <https://docs.github.com/en/rest/reference/repos#branches>`_
        """
        headers, data = self._requester.requestJsonAndCheck(
            "DELETE",
            f"{self.protection_url}/required_signatures",
            headers={"Accept": Consts.signaturesProtectedBranchesPreview},
        )
