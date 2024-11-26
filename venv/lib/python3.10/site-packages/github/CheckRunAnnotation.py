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


class CheckRunAnnotation(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents check run annotations.
    The reference can be found here: https://docs.github.com/en/rest/reference/checks#list-check-run-annotations
    """

    def __repr__(self):
        return self.get__repr__({"title": self._title.value})

    @property
    def annotation_level(self):
        """
        :type: string
        """
        return self._annotation_level.value

    @property
    def end_column(self):
        """
        :type: integer
        """
        return self._end_column.value

    @property
    def end_line(self):
        """
        :type: integer
        """
        return self._end_line.value

    @property
    def message(self):
        """
        :type: string
        """
        return self._message.value

    @property
    def path(self):
        """
        :type: string
        """
        return self._path.value

    @property
    def raw_details(self):
        """
        :type: string
        """
        return self._raw_details.value

    @property
    def start_column(self):
        """
        :type: integer
        """
        return self._start_column.value

    @property
    def start_line(self):
        """
        :type: integer
        """
        return self._start_line.value

    @property
    def title(self):
        """
        :type: string
        """
        return self._title.value

    def _initAttributes(self):
        self._annotation_level = github.GithubObject.NotSet
        self._end_column = github.GithubObject.NotSet
        self._end_line = github.GithubObject.NotSet
        self._message = github.GithubObject.NotSet
        self._path = github.GithubObject.NotSet
        self._raw_details = github.GithubObject.NotSet
        self._start_column = github.GithubObject.NotSet
        self._start_line = github.GithubObject.NotSet
        self._title = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "annotation_level" in attributes:  # pragma no branch
            self._annotation_level = self._makeStringAttribute(
                attributes["annotation_level"]
            )
        if "end_column" in attributes:  # pragma no branch
            self._end_column = self._makeIntAttribute(attributes["end_column"])
        if "end_line" in attributes:  # pragma no branch
            self._end_line = self._makeIntAttribute(attributes["end_line"])
        if "message" in attributes:  # pragma no branch
            self._message = self._makeStringAttribute(attributes["message"])
        if "path" in attributes:  # pragma no branch
            self._path = self._makeStringAttribute(attributes["path"])
        if "raw_details" in attributes:  # pragma no branch
            self._raw_details = self._makeStringAttribute(attributes["raw_details"])
        if "start_column" in attributes:  # pragma no branch
            self._start_column = self._makeIntAttribute(attributes["start_column"])
        if "start_line" in attributes:  # pragma no branch
            self._start_line = self._makeIntAttribute(attributes["start_line"])
        if "title" in attributes:  # pragma no branch
            self._title = self._makeStringAttribute(attributes["title"])
