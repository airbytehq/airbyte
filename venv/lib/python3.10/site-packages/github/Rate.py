############################ Copyrights and license ############################
#                                                                              #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2014 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2016 Jannis Gebauer <ja.geb@me.com>                                #
# Copyright 2016 Peter Buckley <dx-pbuckley@users.noreply.github.com>          #
# Copyright 2018 Wan Liuyang <tsfdye@gmail.com>                                #
# Copyright 2018 sfdye <tsfdye@gmail.com>                                      #
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


class Rate(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents Rates. The reference can be found here https://docs.github.com/en/rest/reference/rate-limit
    """

    def __repr__(self):
        return self.get__repr__(
            {
                "limit": self._limit.value,
                "remaining": self._remaining.value,
                "reset": self._reset.value,
            }
        )

    @property
    def limit(self):
        """
        :type: integer
        """
        return self._limit.value

    @property
    def remaining(self):
        """
        :type: integer
        """
        return self._remaining.value

    @property
    def reset(self):
        """
        :type: datetime.datetime
        """
        return self._reset.value

    def _initAttributes(self):
        self._limit = github.GithubObject.NotSet
        self._remaining = github.GithubObject.NotSet
        self._reset = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "limit" in attributes:  # pragma no branch
            self._limit = self._makeIntAttribute(attributes["limit"])
        if "remaining" in attributes:  # pragma no branch
            self._remaining = self._makeIntAttribute(attributes["remaining"])
        if "reset" in attributes:  # pragma no branch
            self._reset = self._makeTimestampAttribute(attributes["reset"])
