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
import github.Project
import github.ProjectCard

from . import Consts


class ProjectColumn(github.GithubObject.CompletableGithubObject):
    """
    This class represents Project Columns. The reference can be found here https://docs.github.com/en/rest/reference/projects#columns
    """

    def __repr__(self):
        return self.get__repr__({"name": self._name.value})

    @property
    def cards_url(self):
        """
        :type: string
        """
        return self._cards_url.value

    @property
    def created_at(self):
        """
        :type: datetime.datetime
        """
        return self._created_at.value

    @property
    def id(self):
        """
        :type: integer
        """
        return self._id.value

    @property
    def name(self):
        """
        :type: string
        """
        return self._name.value

    @property
    def node_id(self):
        """
        :type: string
        """
        return self._node_id.value

    @property
    def project_url(self):
        """
        :type: string
        """
        return self._project_url.value

    @property
    def updated_at(self):
        """
        :type: datetime.datetime
        """
        return self._updated_at.value

    @property
    def url(self):
        """
        :type: string
        """
        return self._url.value

    def get_cards(self, archived_state=github.GithubObject.NotSet):
        """
        :calls: `GET /projects/columns/{column_id}/cards <https://docs.github.com/en/rest/reference/projects#list-project-cards>`_
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.ProjectCard.ProjectCard`
        :param archived_state: string
        """
        assert archived_state is github.GithubObject.NotSet or isinstance(
            archived_state, str
        ), archived_state

        url_parameters = dict()
        if archived_state is not github.GithubObject.NotSet:
            url_parameters["archived_state"] = archived_state

        return github.PaginatedList.PaginatedList(
            github.ProjectCard.ProjectCard,
            self._requester,
            f"{self.url}/cards",
            url_parameters,
            {"Accept": Consts.mediaTypeProjectsPreview},
        )

    def create_card(
        self,
        note=github.GithubObject.NotSet,
        content_id=github.GithubObject.NotSet,
        content_type=github.GithubObject.NotSet,
    ):
        """
        :calls: `POST /projects/columns/{column_id}/cards <https://docs.github.com/en/rest/reference/projects#create-a-project-card>`_
        :param note: string
        :param content_id: integer
        :param content_type: string

        :rtype: :class:`github.ProjectCard.ProjectCard`:
        """
        if isinstance(note, str):
            assert content_id is github.GithubObject.NotSet, content_id
            assert content_type is github.GithubObject.NotSet, content_type
            post_parameters = {"note": note}
        else:
            assert note is github.GithubObject.NotSet, note
            assert isinstance(content_id, int), content_id
            assert isinstance(content_type, str), content_type
            post_parameters = {"content_id": content_id, "content_type": content_type}

        import_header = {"Accept": Consts.mediaTypeProjectsPreview}
        headers, data = self._requester.requestJsonAndCheck(
            "POST", f"{self.url}/cards", headers=import_header, input=post_parameters
        )
        return github.ProjectCard.ProjectCard(
            self._requester, headers, data, completed=True
        )

    def move(self, position):
        """
        :calls: `POST POST /projects/columns/{column_id}/moves <https://docs.github.com/en/rest/reference/projects#move-a-project-column>`_
        :param position: string

        :rtype: bool
        """
        assert isinstance(position, str), position
        post_parameters = {"position": position}
        status, _, _ = self._requester.requestJson(
            "POST",
            f"{self.url}/moves",
            input=post_parameters,
            headers={"Accept": Consts.mediaTypeProjectsPreview},
        )
        return status == 201

    def delete(self):
        """
        :calls: `DELETE /projects/columns/{column_id} <https://docs.github.com/en/rest/reference/projects#delete-a-project-column>`_
        :rtype: bool
        """
        status, _, _ = self._requester.requestJson(
            "DELETE",
            self.url,
            headers={"Accept": Consts.mediaTypeProjectsPreview},
        )
        return status == 204

    def edit(self, name):
        """
        :calls: `PATCH /projects/columns/{column_id} <https://docs.github.com/en/rest/reference/projects#update-an-existing-project-column>`_
        :param name: string
        :rtype: None
        """
        assert isinstance(name, str), name
        patch_parameters = {"name": name}

        headers, data = self._requester.requestJsonAndCheck(
            "PATCH",
            self.url,
            input=patch_parameters,
            headers={"Accept": Consts.mediaTypeProjectsPreview},
        )

        self._useAttributes(data)

    def _initAttributes(self):
        self._cards_url = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._node_id = github.GithubObject.NotSet
        self._project_url = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "cards_url" in attributes:  # pragma no branch
            self._cards_url = self._makeStringAttribute(attributes["cards_url"])
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "node_id" in attributes:  # pragma no branch
            self._node_id = self._makeStringAttribute(attributes["node_id"])
        if "project_url" in attributes:  # pragma no branch
            self._project_url = self._makeStringAttribute(attributes["project_url"])
        if "updated_at" in attributes:  # pragma no branch
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
