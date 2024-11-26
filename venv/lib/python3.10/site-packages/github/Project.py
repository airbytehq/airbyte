############################ Copyrights and license ############################
#                                                                              #
# Copyright 2018 bbi-yggy <yossarian@blackbirdinteractive.com>                 #
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
import github.ProjectColumn

from . import Consts


class Project(github.GithubObject.CompletableGithubObject):
    """
    This class represents Projects. The reference can be found here https://docs.github.com/en/rest/reference/projects
    """

    def __repr__(self):
        return self.get__repr__({"name": self._name.value})

    @property
    def body(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._body)
        return self._body.value

    @property
    def columns_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._columns_url)
        return self._columns_url.value

    @property
    def created_at(self):
        """
        :type: datetime.datetime
        """
        self._completeIfNotSet(self._created_at)
        return self._created_at.value

    @property
    def creator(self):
        """
        :type: :class:`github.NamedUser.NamedUser`
        """
        self._completeIfNotSet(self._creator)
        return self._creator.value

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
    def number(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._number)
        return self._number.value

    @property
    def owner_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._owner_url)
        return self._owner_url.value

    @property
    def state(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._state)
        return self._state.value

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

    def delete(self):
        """
        :calls: `DELETE /projects/{project_id} <https://docs.github.com/en/rest/reference/projects#delete-a-project>`_
        :rtype: None
        """
        headers, data = self._requester.requestJsonAndCheck(
            "DELETE", self.url, headers={"Accept": Consts.mediaTypeProjectsPreview}
        )

    def edit(
        self,
        name=github.GithubObject.NotSet,
        body=github.GithubObject.NotSet,
        state=github.GithubObject.NotSet,
        organization_permission=github.GithubObject.NotSet,
        private=github.GithubObject.NotSet,
    ):
        """
        :calls: `PATCH /projects/{project_id} <https://docs.github.com/en/rest/reference/projects#update-a-project>`_
        :param name: string
        :param body: string
        :param state: string
        :param organization_permission: string
        :param private: bool
        :rtype: None
        """
        assert name is github.GithubObject.NotSet or isinstance(name, str), name
        assert body is github.GithubObject.NotSet or isinstance(body, str), body
        assert state is github.GithubObject.NotSet or isinstance(state, str), state
        assert organization_permission is github.GithubObject.NotSet or isinstance(
            organization_permission, str
        ), organization_permission
        assert private is github.GithubObject.NotSet or isinstance(
            private, bool
        ), private
        patch_parameters = dict()
        if name is not github.GithubObject.NotSet:
            patch_parameters["name"] = name
        if body is not github.GithubObject.NotSet:
            patch_parameters["body"] = body
        if state is not github.GithubObject.NotSet:
            patch_parameters["state"] = state
        if organization_permission is not github.GithubObject.NotSet:
            patch_parameters["organization_permission"] = organization_permission
        if private is not github.GithubObject.NotSet:
            patch_parameters["private"] = private
        headers, data = self._requester.requestJsonAndCheck(
            "PATCH",
            self.url,
            input=patch_parameters,
            headers={"Accept": Consts.mediaTypeProjectsPreview},
        )
        self._useAttributes(data)

    def get_columns(self):
        """
        :calls: `GET /projects/{project_id}/columns <https://docs.github.com/en/rest/reference/projects#list-project-columns>`_
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.ProjectColumn.ProjectColumn`
        """

        return github.PaginatedList.PaginatedList(
            github.ProjectColumn.ProjectColumn,
            self._requester,
            self.columns_url,
            None,
            {"Accept": Consts.mediaTypeProjectsPreview},
        )

    def create_column(self, name):
        """
        calls: `POST /projects/{project_id}/columns <https://docs.github.com/en/rest/reference/projects#create-a-project-column>`_
        :param name: string
        """
        assert isinstance(name, str), name
        post_parameters = {"name": name}
        import_header = {"Accept": Consts.mediaTypeProjectsPreview}
        headers, data = self._requester.requestJsonAndCheck(
            "POST", f"{self.url}/columns", headers=import_header, input=post_parameters
        )
        return github.ProjectColumn.ProjectColumn(
            self._requester, headers, data, completed=True
        )

    def _initAttributes(self):
        self._body = github.GithubObject.NotSet
        self._columns_url = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._creator = github.GithubObject.NotSet
        self._html_url = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._node_id = github.GithubObject.NotSet
        self._number = github.GithubObject.NotSet
        self._owner_url = github.GithubObject.NotSet
        self._state = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "body" in attributes:  # pragma no branch
            self._body = self._makeStringAttribute(attributes["body"])
        if "columns_url" in attributes:  # pragma no branch
            self._columns_url = self._makeStringAttribute(attributes["columns_url"])
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "creator" in attributes:  # pragma no branch
            self._creator = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["creator"]
            )
        if "html_url" in attributes:  # pragma no branch
            self._html_url = self._makeStringAttribute(attributes["html_url"])
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "node_id" in attributes:  # pragma no branch
            self._node_id = self._makeStringAttribute(attributes["node_id"])
        if "number" in attributes:  # pragma no branch
            self._number = self._makeIntAttribute(attributes["number"])
        if "owner_url" in attributes:  # pragma no branch
            self._owner_url = self._makeStringAttribute(attributes["owner_url"])
        if "state" in attributes:  # pragma no branch
            self._state = self._makeStringAttribute(attributes["state"])
        if "updated_at" in attributes:  # pragma no branch
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
