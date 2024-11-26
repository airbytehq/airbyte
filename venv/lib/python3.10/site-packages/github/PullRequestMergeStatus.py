############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2013 martinqt <m.ki2@laposte.net>                                  #
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


class PullRequestMergeStatus(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents PullRequestMergeStatuses. The reference can be found here https://docs.github.com/en/rest/reference/pulls#check-if-a-pull-request-has-been-merged
    """

    def __repr__(self):
        return self.get__repr__({"sha": self._sha.value, "merged": self._merged.value})

    @property
    def merged(self):
        """
        :type: bool
        """
        return self._merged.value

    @property
    def message(self):
        """
        :type: string
        """
        return self._message.value

    @property
    def sha(self):
        """
        :type: string
        """
        return self._sha.value

    def _initAttributes(self):
        self._merged = github.GithubObject.NotSet
        self._message = github.GithubObject.NotSet
        self._sha = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "merged" in attributes:  # pragma no branch
            self._merged = self._makeBoolAttribute(attributes["merged"])
        if "message" in attributes:  # pragma no branch
            self._message = self._makeStringAttribute(attributes["message"])
        if "sha" in attributes:  # pragma no branch
            self._sha = self._makeStringAttribute(attributes["sha"])
