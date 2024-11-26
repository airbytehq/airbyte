############################ Copyrights and license ############################
#                                                                              #
# Copyright 2019 Adam Baratz <adam.baratz@gmail.com>                           #
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


class TeamDiscussion(github.GithubObject.CompletableGithubObject):
    """
    This class represents TeamDiscussions. The reference can be found here https://docs.github.com/en/rest/reference/teams#discussions
    """

    def __repr__(self):
        return self.get__repr__(
            {"number": self._number.value, "title": self._title.value}
        )

    @property
    def author(self):
        """
        :type: :class:`github.NamedUser.NamedUser`
        """
        self._completeIfNotSet(self._author)
        return self._author.value

    @property
    def body(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._body)
        return self._body.value

    @property
    def body_html(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._body_html)
        return self._body_html.value

    @property
    def body_version(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._body_version)
        return self._body_version.value

    @property
    def comments_count(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._comments_count)
        return self._comments_count.value

    @property
    def comments_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._comments_url)
        return self._comments_url.value

    @property
    def created_at(self):
        """
        :type: datetime.datetime
        """
        self._completeIfNotSet(self._created_at)
        return self._created_at.value

    @property
    def html_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._html_url)
        return self._html_url.value

    @property
    def last_edited_at(self):
        """
        :type: datetime.datetime
        """
        self._completeIfNotSet(self._last_edited_at)
        return self._last_edited_at.value

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
    def pinned(self):
        """
        :type: bool
        """
        self._completeIfNotSet(self._pinned)
        return self._pinned.value

    @property
    def private(self):
        """
        :type: bool
        """
        self._completeIfNotSet(self._private)
        return self._private.value

    @property
    def team_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._team_url)
        return self._team_url.value

    @property
    def title(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._title)
        return self._title.value

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

    def _initAttributes(self):
        self._author = github.GithubObject.NotSet
        self._body = github.GithubObject.NotSet
        self._body_html = github.GithubObject.NotSet
        self._body_version = github.GithubObject.NotSet
        self._comments_count = github.GithubObject.NotSet
        self._comments_url = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._html_url = github.GithubObject.NotSet
        self._last_edited_at = github.GithubObject.NotSet
        self._node_id = github.GithubObject.NotSet
        self._number = github.GithubObject.NotSet
        self._pinned = github.GithubObject.NotSet
        self._private = github.GithubObject.NotSet
        self._team_url = github.GithubObject.NotSet
        self._title = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "author" in attributes:  # pragma no branch
            self._author = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["author"]
            )
        if "body" in attributes:  # pragma no branch
            self._body = self._makeStringAttribute(attributes["body"])
        if "body_html" in attributes:  # pragma no branch
            self._body_html = self._makeStringAttribute(attributes["body_html"])
        if "body_version" in attributes:  # pragma no branch
            self._body_version = self._makeStringAttribute(attributes["body_version"])
        if "comments_count" in attributes:  # pragma no branch
            self._comments_count = self._makeIntAttribute(attributes["comments_count"])
        if "comments_url" in attributes:  # pragma no branch
            self._comments_url = self._makeStringAttribute(attributes["comments_url"])
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "html_url" in attributes:  # pragma no branch
            self._html_url = self._makeStringAttribute(attributes["html_url"])
        if "last_edited_at" in attributes:  # pragma no branch
            self._last_edited_at = self._makeDatetimeAttribute(
                attributes["last_edited_at"]
            )
        if "node_id" in attributes:  # pragma no branch
            self._node_id = self._makeStringAttribute(attributes["node_id"])
        if "number" in attributes:  # pragma no branch
            self._number = self._makeIntAttribute(attributes["number"])
        if "pinned" in attributes:  # pragma no branch
            self._pinned = self._makeBoolAttribute(attributes["pinned"])
        if "private" in attributes:  # pragma no branch
            self._private = self._makeBoolAttribute(attributes["private"])
        if "team_url" in attributes:  # pragma no branch
            self._team_url = self._makeStringAttribute(attributes["team_url"])
        if "title" in attributes:
            self._title = self._makeStringAttribute(attributes["title"])
        if "updated_at" in attributes:  # pragma no branch
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
