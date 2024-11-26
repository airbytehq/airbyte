############################ Copyrights and license ############################
#                                                                              #
# Copyright 2017 Jannis Gebauer <ja.geb@me.com>                                #
# Copyright 2017 Simon <spam@esemi.ru>                                         #
# Copyright 2018 Wan Liuyang <tsfdye@gmail.com>                                #
# Copyright 2018 sfdye <tsfdye@gmail.com>                                      #
# Copyright 2019 Rigas Papathanasopoulos <rigaspapas@gmail.com>                #
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

import github.Authorization
import github.Event
import github.Gist
import github.GithubObject
import github.Issue
import github.Notification
import github.Organization
import github.PaginatedList
import github.Plan
import github.Repository
import github.UserKey
from github.Auth import AppAuth

from . import Consts

INTEGRATION_PREVIEW_HEADERS = {"Accept": Consts.mediaTypeIntegrationPreview}


class Installation(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents Installations. The reference can be found here https://docs.github.com/en/rest/reference/apps#installations
    """

    def __init__(self, requester, headers, attributes, completed):
        super().__init__(requester, headers, attributes, completed)

        auth = self._requester.auth if self._requester is not None else None
        # Usually, an Installation is created from a Requester with App authentication
        if isinstance(auth, AppAuth):
            # But the installation has to authenticate as an installation (e.g. for get_repos())
            auth = auth.get_installation_auth(self.id, requester=self._requester)
            self._requester = self._requester.withAuth(auth)

    def __repr__(self):
        return self.get__repr__({"id": self._id.value})

    def get_github_for_installation(self):
        return github.Github(**self._requester.kwargs)

    @property
    def id(self):
        """
        :type: integer
        """
        return self._id.value

    @property
    def app_id(self):
        """
        :type: integer
        """
        return self._app_id.value

    @property
    def target_id(self):
        """
        :type: integer
        """
        return self._target_id.value

    @property
    def target_type(self):
        """
        :type: string
        """
        return self._target_type.value

    def get_repos(self):
        """
        :calls: `GET /installation/repositories <https://docs.github.com/en/rest/reference/integrations/installations#list-repositories>`_
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.Repository.Repository`
        """
        url_parameters = dict()

        return github.PaginatedList.PaginatedList(
            contentClass=github.Repository.Repository,
            requester=self._requester,
            firstUrl="/installation/repositories",
            firstParams=url_parameters,
            headers=INTEGRATION_PREVIEW_HEADERS,
            list_item="repositories",
        )

    def _initAttributes(self):
        self._id = github.GithubObject.NotSet
        self._app_id = github.GithubObject.NotSet
        self._target_id = github.GithubObject.NotSet
        self._target_type = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "app_id" in attributes:  # pragma no branch
            self._app_id = self._makeIntAttribute(attributes["app_id"])
        if "target_id" in attributes:  # pragma no branch
            self._target_id = self._makeIntAttribute(attributes["target_id"])
        if "target_type" in attributes:  # pragma no branch
            self._target_type = self._makeStringAttribute(attributes["target_type"])
