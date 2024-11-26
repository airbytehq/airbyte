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

import github.GithubObject
import github.NamedUser


class GithubApp(github.GithubObject.CompletableGithubObject):
    """
    This class represents github apps. The reference can be found here https://docs.github.com/en/rest/reference/apps
    """

    def __repr__(self):
        return self.get__repr__({"id": self._id.value, "url": self._url.value})

    @property
    def created_at(self):
        """
        :type: datetime.datetime
        """
        self._completeIfNotSet(self._created_at)
        return self._created_at.value

    @property
    def description(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._description)
        return self._description.value

    @property
    def events(self):
        """
        :type: list of string
        """
        self._completeIfNotSet(self._events)
        return self._events.value

    @property
    def external_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._external_url)
        return self._external_url.value

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
        :type: int
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
    def owner(self):
        """
        :type: :class:`Github.NamedUser.NamedUser`
        """
        self._completeIfNotSet(self._owner)
        return self._owner.value

    @property
    def permissions(self):
        """
        :type: dict
        """
        self._completeIfNotSet(self._permissions)
        return self._permissions.value

    @property
    def slug(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._slug)
        return self._slug.value

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
        return self._url.value

    def _initAttributes(self):
        self._created_at = github.GithubObject.NotSet
        self._description = github.GithubObject.NotSet
        self._events = github.GithubObject.NotSet
        self._external_url = github.GithubObject.NotSet
        self._html_url = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._owner = github.GithubObject.NotSet
        self._permissions = github.GithubObject.NotSet
        self._slug = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "description" in attributes:  # pragma no branch
            self._description = self._makeStringAttribute(attributes["description"])
        if "events" in attributes:  # pragma no branch
            self._events = self._makeListOfStringsAttribute(attributes["events"])
        if "external_url" in attributes:  # pragma no branch
            self._external_url = self._makeStringAttribute(attributes["external_url"])
        if "html_url" in attributes:  # pragma no branch
            self._html_url = self._makeStringAttribute(attributes["html_url"])
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "owner" in attributes:  # pragma no branch
            self._owner = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["owner"]
            )
        if "permissions" in attributes:  # pragma no branch
            self._permissions = self._makeDictAttribute(attributes["permissions"])
        if "slug" in attributes:  # pragma no branch
            self._slug = self._makeStringAttribute(attributes["slug"])
            self._url = self._makeStringAttribute(f"/apps/{attributes['slug']}")
        if "updated_at" in attributes:  # pragma no branch
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
        if "url" in attributes:
            self._url = self._makeStringAttribute(attributes["url"])
