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

from . import Consts

# NOTE: There is currently no way to get cards "in triage" for a project.
# https://platform.github.community/t/moving-github-project-cards-that-are-in-triage/3784
#
# See also https://developer.github.com/v4/object/projectcard for the next generation GitHub API,
# which may point the way to where the API is likely headed and what might come back to v3. E.g. ProjectCard.content member.


class ProjectCard(github.GithubObject.CompletableGithubObject):
    """
    This class represents Project Cards. The reference can be found here https://docs.github.com/en/rest/reference/projects#cards
    """

    def __repr__(self):
        return self.get__repr__({"id": self._id.value})

    @property
    def archived(self):
        """
        :type: bool
        """
        return self._archived.value

    @property
    def column_url(self):
        """
        :type: string
        """
        return self._column_url.value

    @property
    def content_url(self):
        """
        :type: string
        """
        return self._content_url.value

    @property
    def created_at(self):
        """
        :type: datetime.datetime
        """
        return self._created_at.value

    @property
    def creator(self):
        """
        :type: :class:`github.NamedUser.NamedUser`
        """
        return self._creator.value

    @property
    def id(self):
        """
        :type: integer
        """
        return self._id.value

    @property
    def node_id(self):
        """
        :type: string
        """
        return self._node_id.value

    @property
    def note(self):
        """
        :type: string
        """
        return self._note.value

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

    # Note that the content_url for any card will be an "issue" URL, from
    # which you can retrieve either an Issue or a PullRequest. Unfortunately
    # the API doesn't make it clear which you are dealing with.
    def get_content(self, content_type=github.GithubObject.NotSet):
        """
        :calls: `GET /repos/{owner}/{repo}/pulls/{number} <https://docs.github.com/en/rest/reference/pulls#get-a-pull-request>`_
        :param content_type: string, optional
        :rtype: :class:`github.PullRequest.PullRequest` or :class:`github.Issue.Issue`
        """
        assert content_type is github.GithubObject.NotSet or isinstance(
            content_type, str
        ), content_type
        if self.content_url is None:
            return None

        if content_type == "PullRequest":
            url = self.content_url.replace("issues", "pulls")
            retclass = github.PullRequest.PullRequest
        elif content_type is github.GithubObject.NotSet or content_type == "Issue":
            url = self.content_url
            retclass = github.Issue.Issue
        else:
            raise ValueError(f"Unknown content type: {content_type}")
        headers, data = self._requester.requestJsonAndCheck("GET", url)
        return retclass(self._requester, headers, data, completed=True)

    def move(self, position, column):
        """
        :calls: `POST /projects/columns/cards/{card_id}/moves <https://docs.github.com/en/rest/reference/projects#cards>`_
        :param position: string
        :param column: :class:`github.ProjectColumn.ProjectColumn` or int
        :rtype: bool
        """
        assert isinstance(position, str), position
        assert isinstance(column, github.ProjectColumn.ProjectColumn) or isinstance(
            column, int
        ), column
        post_parameters = {
            "position": position,
            "column_id": column.id
            if isinstance(column, github.ProjectColumn.ProjectColumn)
            else column,
        }
        status, _, _ = self._requester.requestJson(
            "POST",
            f"{self.url}/moves",
            input=post_parameters,
            headers={"Accept": Consts.mediaTypeProjectsPreview},
        )
        return status == 201

    def delete(self):
        """
        :calls: `DELETE /projects/columns/cards/{card_id} <https://docs.github.com/en/rest/reference/projects#cards>`_
        :rtype: bool
        """
        status, _, _ = self._requester.requestJson(
            "DELETE",
            self.url,
            headers={"Accept": Consts.mediaTypeProjectsPreview},
        )
        return status == 204

    def edit(
        self, note=github.GithubObject.NotSet, archived=github.GithubObject.NotSet
    ):
        """
        :calls: `PATCH /projects/columns/cards/{card_id} <https://docs.github.com/en/rest/reference/projects#cards>`_
        :param note: string
        :param archived: bool
        :rtype: None
        """
        assert note is github.GithubObject.NotSet or isinstance(note, str), note
        assert archived is github.GithubObject.NotSet or isinstance(
            archived, bool
        ), archived
        patch_parameters = dict()
        if note is not github.GithubObject.NotSet:
            patch_parameters["note"] = note
        if archived is not github.GithubObject.NotSet:
            patch_parameters["archived"] = archived
        headers, data = self._requester.requestJsonAndCheck(
            "PATCH",
            self.url,
            input=patch_parameters,
            headers={"Accept": Consts.mediaTypeProjectsPreview},
        )
        self._useAttributes(data)

    def _initAttributes(self):
        self._archived = github.GithubObject.NotSet
        self._column_url = github.GithubObject.NotSet
        self._content_url = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._creator = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._node_id = github.GithubObject.NotSet
        self._note = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "archived" in attributes:  # pragma no branch
            self._archived = self._makeBoolAttribute(attributes["archived"])
        if "column_url" in attributes:  # pragma no branch
            self._column_url = self._makeStringAttribute(attributes["column_url"])
        if "content_url" in attributes:  # pragma no branch
            self._content_url = self._makeStringAttribute(attributes["content_url"])
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "creator" in attributes:  # pragma no branch
            self._creator = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["creator"]
            )
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "node_id" in attributes:  # pragma no branch
            self._node_id = self._makeStringAttribute(attributes["node_id"])
        if "note" in attributes:  # pragma no branch
            self._note = self._makeStringAttribute(attributes["note"])
        if "updated_at" in attributes:  # pragma no branch
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
