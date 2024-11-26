############################ Copyrights and license ############################
#                                                                              #
# Copyright 2020 Steve Kowalik <steven@wedontsleep.org>                        #
# Copyright 2020 Colby Gallup <colbygallup@gmail.com>                          #
# Copyright 2020 Pascal Hofmann <mail@pascalhofmann.de>                        #
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

import github.Consts
import github.DeploymentStatus
import github.GithubObject


class Deployment(github.GithubObject.CompletableGithubObject):
    """
    This class represents Deployments. The reference can be found here https://docs.github.com/en/rest/reference/repos#deployments
    """

    def __repr__(self):
        return self.get__repr__({"id": self._id.value, "url": self._url.value})

    @property
    def id(self):
        """
        :type: int
        """
        self._completeIfNotSet(self._id)
        return self._id.value

    @property
    def ref(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._ref)
        return self._ref.value

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    @property
    def sha(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._sha)
        return self._sha.value

    @property
    def task(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._task)
        return self._task.value

    @property
    def payload(self):
        """
        :type: dict
        """
        self._completeIfNotSet(self._payload)
        return self._payload.value

    @property
    def original_environment(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._original_environment)
        return self._original_environment.value

    @property
    def environment(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._environment)
        return self._environment.value

    @property
    def production_environment(self):
        """
        :type: bool
        """
        self._completeIfNotSet(self._production_environment)
        return self._production_environment.value

    @property
    def transient_environment(self):
        """
        :type: bool
        """
        self._completeIfNotSet(self._transient_environment)
        return self._transient_environment.value

    @property
    def description(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._description)
        return self._description.value

    @property
    def creator(self):
        """
        :type: :class:`github.NamedUser.NamedUser`
        """
        self._completeIfNotSet(self._creator)
        return self._creator.value

    @property
    def created_at(self):
        """
        :type: datetime
        """
        self._completeIfNotSet(self._created_at)
        return self._created_at.value

    @property
    def updated_at(self):
        """
        :type: datetime
        """
        self._completeIfNotSet(self._updated_at)
        return self._updated_at.value

    @property
    def statuses_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._statuses_url)
        return self._statuses_url.value

    @property
    def repository_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._repository_url)
        return self._repository_url.value

    def get_statuses(self):
        """
        :calls: `GET /repos/{owner}/deployments/{deployment_id}/statuses <https://docs.github.com/en/rest/reference/repos#list-deployments>`_
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.DeploymentStatus.DeploymentStatus`
        """
        return github.PaginatedList.PaginatedList(
            github.DeploymentStatus.DeploymentStatus,
            self._requester,
            f"{self.url}/statuses",
            None,
            headers={"Accept": self._get_accept_header()},
        )

    def get_status(self, id_):
        """
        :calls: `GET /repos/{owner}/deployments/{deployment_id}/statuses/{status_id}  <https://docs.github.com/en/rest/reference/repos#get-a-deployment>`_
        :param id_: int
        :rtype: :class:`github.DeploymentStatus.DeploymentStatus`
        """
        assert isinstance(id_, int), id_
        headers, data = self._requester.requestJsonAndCheck(
            "GET",
            f"{self.url}/statuses/{id_}",
            headers={"Accept": self._get_accept_header()},
        )
        return github.DeploymentStatus.DeploymentStatus(
            self._requester, headers, data, completed=True
        )

    def create_status(
        self,
        state,
        target_url=github.GithubObject.NotSet,
        description=github.GithubObject.NotSet,
        environment=github.GithubObject.NotSet,
        environment_url=github.GithubObject.NotSet,
        auto_inactive=github.GithubObject.NotSet,
    ):
        """
        :calls: `POST /repos/{owner}/{repo}/deployments/{deployment_id}/statuses <https://docs.github.com/en/rest/reference/repos#create-a-deployment-status>`_
        :param: state: string
        :param: target_url: string
        :param: description: string
        :param: environment: string
        :param: environment_url: string
        :param: auto_inactive: bool
        :rtype: :class:`github.DeploymentStatus.DeploymentStatus`
        """
        assert isinstance(state, str), state
        assert target_url is github.GithubObject.NotSet or isinstance(
            target_url, str
        ), target_url
        assert description is github.GithubObject.NotSet or isinstance(
            description, str
        ), description
        assert environment is github.GithubObject.NotSet or isinstance(
            environment, str
        ), environment
        assert environment_url is github.GithubObject.NotSet or isinstance(
            environment_url, str
        ), environment_url
        assert auto_inactive is github.GithubObject.NotSet or isinstance(
            auto_inactive, bool
        ), auto_inactive

        post_parameters = {"state": state}
        if target_url is not github.GithubObject.NotSet:
            post_parameters["target_url"] = target_url
        if description is not github.GithubObject.NotSet:
            post_parameters["description"] = description
        if environment is not github.GithubObject.NotSet:
            post_parameters["environment"] = environment
        if environment_url is not github.GithubObject.NotSet:
            post_parameters["environment_url"] = environment_url
        if auto_inactive is not github.GithubObject.NotSet:
            post_parameters["auto_inactive"] = auto_inactive

        headers, data = self._requester.requestJsonAndCheck(
            "POST",
            f"{self.url}/statuses",
            input=post_parameters,
            headers={"Accept": self._get_accept_header()},
        )
        return github.DeploymentStatus.DeploymentStatus(
            self._requester, headers, data, completed=True
        )

    @staticmethod
    def _get_accept_header():
        return ", ".join(
            [
                github.Consts.deploymentEnhancementsPreview,
                github.Consts.deploymentStatusEnhancementsPreview,
            ]
        )

    def _initAttributes(self):
        self._id = github.GithubObject.NotSet
        self._production_environment = github.GithubObject.NotSet
        self._ref = github.GithubObject.NotSet
        self._transient_environment = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet
        self._sha = github.GithubObject.NotSet
        self._task = github.GithubObject.NotSet
        self._payload = github.GithubObject.NotSet
        self._original_environment = github.GithubObject.NotSet
        self._environment = github.GithubObject.NotSet
        self._description = github.GithubObject.NotSet
        self._creator = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet
        self._statuses_url = github.GithubObject.NotSet
        self._repository_url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "production_environment" in attributes:  # pragma no branch
            self._production_environment = self._makeBoolAttribute(
                attributes["production_environment"]
            )
        if "ref" in attributes:  # pragma no branch
            self._ref = self._makeStringAttribute(attributes["ref"])
        if "transient_environment" in attributes:  # pragma no branch
            self._transient_environment = self._makeBoolAttribute(
                attributes["transient_environment"]
            )
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
        if "sha" in attributes:  # pragma no branch
            self._sha = self._makeStringAttribute(attributes["sha"])
        if "task" in attributes:  # pragma no branch
            self._task = self._makeStringAttribute(attributes["task"])
        if "payload" in attributes:  # pragma no branch
            self._payload = self._makeDictAttribute(attributes["payload"])
        if "original_environment" in attributes:  # pragma no branch
            self._original_environment = self._makeStringAttribute(
                attributes["original_environment"]
            )
        if "environment" in attributes:  # pragma no branch
            self._environment = self._makeStringAttribute(attributes["environment"])
        if "description" in attributes:  # pragma no branch
            self._description = self._makeStringAttribute(attributes["description"])
        if "creator" in attributes:  # pragma no branch
            self._creator = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["creator"]
            )
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "updated_at" in attributes:  # pragma no branch
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
        if "statuses_url" in attributes:  # pragma no branch
            self._statuses_url = self._makeStringAttribute(attributes["statuses_url"])
        if "repository_url" in attributes:  # pragma no branch
            self._repository_url = self._makeStringAttribute(
                attributes["repository_url"]
            )
