############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2014 Vincent Jacques <vincent@vincent-jacques.net>                 #
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


class CommitStats(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents CommitStatses.
    """

    @property
    def additions(self):
        """
        :type: integer
        """
        return self._additions.value

    @property
    def deletions(self):
        """
        :type: integer
        """
        return self._deletions.value

    @property
    def total(self):
        """
        :type: integer
        """
        return self._total.value

    def _initAttributes(self):
        self._additions = github.GithubObject.NotSet
        self._deletions = github.GithubObject.NotSet
        self._total = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "additions" in attributes:  # pragma no branch
            self._additions = self._makeIntAttribute(attributes["additions"])
        if "deletions" in attributes:  # pragma no branch
            self._deletions = self._makeIntAttribute(attributes["deletions"])
        if "total" in attributes:  # pragma no branch
            self._total = self._makeIntAttribute(attributes["total"])
