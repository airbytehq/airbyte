############################ Copyrights and license ############################
#                                                                              #
# Copyright 2015 Dan Vanderkam <danvdk@gmail.com>                              #
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

import github


class Stargazer(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents Stargazers. The reference can be found here https://docs.github.com/en/rest/reference/activity#starring
    """

    def __repr__(self):
        return self.get__repr__({"user": self._user.value._login.value})

    @property
    def starred_at(self):
        """
        :type: datetime.datetime
        """
        return self._starred_at.value

    @property
    def user(self):
        """
        :type: :class:`github.NamedUser`
        """
        return self._user.value

    def _initAttributes(self):
        self._starred_at = github.GithubObject.NotSet
        self._user = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "starred_at" in attributes:
            self._starred_at = self._makeDatetimeAttribute(attributes["starred_at"])
        if "user" in attributes:
            self._user = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["user"]
            )
