############################ Copyrights and license ############################
#                                                                              #
# Copyright 2017 Nicolas Agustín Torres <nicolastrres@gmail.com>              #
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
import github.NamedUser

from . import Consts


class Reaction(github.GithubObject.CompletableGithubObject):
    """
    This class represents Reactions. The reference can be found here https://docs.github.com/en/rest/reference/reactions
    """

    def __repr__(self):
        return self.get__repr__({"id": self._id.value, "user": self._user.value})

    @property
    def content(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._content)
        return self._content.value

    @property
    def created_at(self):
        """
        :type: datetime.datetime
        """
        self._completeIfNotSet(self._created_at)
        return self._created_at.value

    @property
    def id(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._id)
        return self._id.value

    @property
    def user(self):
        """
        :type: :class:`github.NamedUser.NamedUser`
        """
        self._completeIfNotSet(self._user)
        return self._user.value

    def delete(self):
        """
        :calls: `DELETE /reactions/{id} <https://docs.github.com/en/rest/reference/reactions#delete-a-reaction-legacy>`_
        :rtype: None
        """
        self._requester.requestJsonAndCheck(
            "DELETE",
            f"{self._parentUrl('')}/reactions/{self.id}",
            headers={"Accept": Consts.mediaTypeReactionsPreview},
        )

    def _initAttributes(self):
        self._content = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._user = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "content" in attributes:  # pragma no branch
            self._content = self._makeStringAttribute(attributes["content"])
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "user" in attributes:  # pragma no branch
            self._user = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["user"]
            )
