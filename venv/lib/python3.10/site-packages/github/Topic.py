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


class Topic(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents topics as used by https://github.com/topics. The object reference can be found here https://docs.github.com/en/rest/reference/search#search-topics
    """

    def __repr__(self):
        return self.get__repr__({"name": self._name.value})

    @property
    def name(self):
        """
        :type: string
        """
        return self._name.value

    @property
    def display_name(self):
        """
        :type: string
        """
        return self._display_name.value

    @property
    def short_description(self):
        """
        :type: string
        """
        return self._short_description.value

    @property
    def description(self):
        """
        :type: string
        """
        return self._description.value

    @property
    def created_by(self):
        """
        :type: string
        """
        return self._created_by.value

    @property
    def released(self):
        """
        :type: string
        """
        return self._released.value

    @property
    def created_at(self):
        """
        :type: datetime.datetime
        """
        return self._created_at.value

    @property
    def updated_at(self):
        """
        :type: datetime.datetime
        """
        return self._updated_at.value

    @property
    def featured(self):
        """
        :type: bool
        """
        return self._featured.value

    @property
    def curated(self):
        """
        :type: bool
        """
        return self._curated.value

    @property
    def score(self):
        """
        :type: float
        """
        return self._score.value

    def _initAttributes(self):
        self._name = github.GithubObject.NotSet
        self._display_name = github.GithubObject.NotSet
        self._short_description = github.GithubObject.NotSet
        self._description = github.GithubObject.NotSet
        self._created_by = github.GithubObject.NotSet
        self._released = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet
        self._featured = github.GithubObject.NotSet
        self._curated = github.GithubObject.NotSet
        self._score = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "display_name" in attributes:  # pragma no branch
            self._display_name = self._makeStringAttribute(attributes["display_name"])
        if "short_description" in attributes:  # pragma no branch
            self._short_description = self._makeStringAttribute(
                attributes["short_description"]
            )
        if "description" in attributes:  # pragma no branch
            self._description = self._makeStringAttribute(attributes["description"])
        if "created_by" in attributes:  # pragma no branch
            self._created_by = self._makeStringAttribute(attributes["created_by"])
        if "released" in attributes:  # pragma no branch
            self._released = self._makeStringAttribute(attributes["released"])
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "updated_at" in attributes:  # pragma no branch
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
        if "featured" in attributes:  # pragma no branch
            self._featured = self._makeBoolAttribute(attributes["featured"])
        if "curated" in attributes:  # pragma no branch
            self._curated = self._makeBoolAttribute(attributes["curated"])
        if "score" in attributes:  # pragma no branch
            self._score = self._makeFloatAttribute(attributes["score"])
