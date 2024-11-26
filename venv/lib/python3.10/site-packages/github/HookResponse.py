############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
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


class HookResponse(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents HookResponses
    """

    def __repr__(self):
        return self.get__repr__({"status": self._status.value})

    @property
    def code(self):
        """
        :type: integer
        """
        return self._code.value

    @property
    def message(self):
        """
        :type: string
        """
        return self._message.value

    @property
    def status(self):
        """
        :type: string
        """
        return self._status.value

    def _initAttributes(self):
        self._code = github.GithubObject.NotSet
        self._message = github.GithubObject.NotSet
        self._status = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "code" in attributes:  # pragma no branch
            self._code = self._makeIntAttribute(attributes["code"])
        if "message" in attributes:  # pragma no branch
            self._message = self._makeStringAttribute(attributes["message"])
        if "status" in attributes:  # pragma no branch
            self._status = self._makeStringAttribute(attributes["status"])
