############################ Copyrights and license ############################
#                                                                              #
# Copyright 2020 Dhruv Manilawala <dhruvmanila@gmail.com>                      #
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


class CheckRunOutput(github.GithubObject.NonCompletableGithubObject):
    """This class represents the output of check run."""

    def __repr__(self):
        return self.get__repr__({"title": self._title.value})

    @property
    def annotations_count(self):
        """
        :type: integer
        """
        return self._annotations_count.value

    @property
    def annotations_url(self):
        """
        :type: string
        """
        return self._annotations_url.value

    @property
    def summary(self):
        """
        :type: string
        """
        return self._summary.value

    @property
    def text(self):
        """
        :type: string
        """
        return self._text.value

    @property
    def title(self):
        """
        :type: string
        """
        return self._title.value

    def _initAttributes(self):
        self._annotations_count = github.GithubObject.NotSet
        self._annotations_url = github.GithubObject.NotSet
        self._summary = github.GithubObject.NotSet
        self._text = github.GithubObject.NotSet
        self._title = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "annotations_count" in attributes:  # pragma no branch
            self._annotations_count = self._makeIntAttribute(
                attributes["annotations_count"]
            )
        if "annotations_url" in attributes:  # pragma no branch
            self._annotations_url = self._makeStringAttribute(
                attributes["annotations_url"]
            )
        if "summary" in attributes:  # pragma no branch
            self._summary = self._makeStringAttribute(attributes["summary"])
        if "text" in attributes:  # pragma no branch
            self._text = self._makeStringAttribute(attributes["text"])
        if "title" in attributes:  # pragma no branch
            self._title = self._makeStringAttribute(attributes["title"])
