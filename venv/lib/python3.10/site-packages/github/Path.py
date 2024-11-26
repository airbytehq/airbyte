############################ Copyrights and license ############################
#                                                                              #
# Copyright 2018 Justin Kufro <jkufro@andrew.cmu.edu>                          #
# Copyright 2018 Ivan Minno <iminno@andrew.cmu.edu>                            #
# Copyright 2018 Zilei Gu <zileig@andrew.cmu.edu>                              #
# Copyright 2018 Yves Zumbach <yzumbach@andrew.cmu.edu>                        #
# Copyright 2018 Leying Chen <leyingc@andrew.cmu.edu>                          #
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


class Path(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents a popular Path for a GitHub repository.
    The reference can be found here https://docs.github.com/en/rest/reference/repos#traffic
    """

    def __repr__(self):
        return self.get__repr__(
            {
                "path": self._path.value,
                "title": self._title.value,
                "count": self._count.value,
                "uniques": self._uniques.value,
            }
        )

    @property
    def path(self):
        """
        :type: string
        """
        return self._path.value

    @property
    def title(self):
        """
        :type: string
        """
        return self._title.value

    @property
    def count(self):
        """
        :type: integer
        """
        return self._count.value

    @property
    def uniques(self):
        """
        :type: integer
        """
        return self._uniques.value

    def _initAttributes(self):
        self._path = github.GithubObject.NotSet
        self._title = github.GithubObject.NotSet
        self._count = github.GithubObject.NotSet
        self._uniques = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "path" in attributes:  # pragma no branch
            self._path = self._makeStringAttribute(attributes["path"])
        if "title" in attributes:  # pragma no branch
            self._title = self._makeStringAttribute(attributes["title"])
        if "count" in attributes:  # pragma no branch
            self._count = self._makeIntAttribute(attributes["count"])
        if "uniques" in attributes:  # pragma no branch
            self._uniques = self._makeIntAttribute(attributes["uniques"])
