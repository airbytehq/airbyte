############################ Copyrights and license ############################
#                                                                              #
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


class StatsCodeFrequency(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents statistics of StatsCodeFrequencies. The reference can be found here https://docs.github.com/en/rest/reference/repos#get-the-weekly-commit-activity
    """

    @property
    def week(self):
        """
        :type: datetime.datetime
        """
        return self._week.value

    @property
    def additions(self):
        """
        :type: int
        """
        return self._additions.value

    @property
    def deletions(self):
        """
        :type: int
        """
        return self._deletions.value

    def _initAttributes(self):
        self._week = github.GithubObject.NotSet
        self._additions = github.GithubObject.NotSet
        self._deletions = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        self._week = self._makeTimestampAttribute(attributes[0])
        self._additions = self._makeIntAttribute(attributes[1])
        self._deletions = self._makeIntAttribute(attributes[2])
