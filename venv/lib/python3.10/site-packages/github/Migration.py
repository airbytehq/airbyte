############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2013 martinqt <m.ki2@laposte.net>                                  #
# Copyright 2014 Andy Casey <acasey@mso.anu.edu.au>                            #
# Copyright 2014 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2016 Jannis Gebauer <ja.geb@me.com>                                #
# Copyright 2016 John Eskew <jeskew@edx.org>                                   #
# Copyright 2016 Peter Buckley <dx-pbuckley@users.noreply.github.com>          #
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
import github.PaginatedList

from . import Consts


class Migration(github.GithubObject.CompletableGithubObject):
    """
    This class represents Migrations. The reference can be found here https://docs.github.com/en/rest/reference/migrations
    """

    def __repr__(self):
        return self.get__repr__({"state": self._state.value, "url": self._url.value})

    @property
    def id(self):
        """
        :type: int
        """
        return self._id.value

    @property
    def owner(self):
        """
        :type: :class:`github.NamedUser.NamedUser`
        """
        self._completeIfNotSet(self._owner)
        return self._owner.value

    @property
    def guid(self):
        """
        :type: str
        """
        self._completeIfNotSet(self._guid)
        return self._guid.value

    @property
    def state(self):
        """
        :type: str
        """
        self._completeIfNotSet(self._guid)
        return self._state.value

    @property
    def lock_repositories(self):
        """
        :type: bool
        """
        self._completeIfNotSet(self._repositories)
        return self._lock_repositories.value

    @property
    def exclude_attachments(self):
        """
        :type: bool
        """
        self._completeIfNotSet(self._exclude_attachments)
        return self._exclude_attachments.value

    @property
    def repositories(self):
        """
        :type: :class:`github.PaginatedList.PaginatedList` of :class:`github.Repository.Repository`
        """
        self._completeIfNotSet(self._repositories)
        return self._repositories.value

    @property
    def url(self):
        """
        :type: str
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    @property
    def created_at(self):
        """
        :type: datetime.datetime
        :rtype: None
        """
        self._completeIfNotSet(self._created_at)
        return self._created_at.value

    @property
    def updated_at(self):
        """
        :type: datetime.datetime
        :rtype: None
        """
        self._completeIfNotSet(self._updated_at)
        return self._updated_at.value

    def get_status(self):
        """
        :calls: `GET /user/migrations/{migration_id} <https://docs.github.com/en/rest/reference/migrations>`_
        :rtype: str
        """
        headers, data = self._requester.requestJsonAndCheck(
            "GET", self.url, headers={"Accept": Consts.mediaTypeMigrationPreview}
        )
        self._useAttributes(data)
        return self.state

    def get_archive_url(self):
        """
        :calls: `GET /user/migrations/{migration_id}/archive <https://docs.github.com/en/rest/reference/migrations>`_
        :rtype: str
        """
        headers, data = self._requester.requestJsonAndCheck(
            "GET",
            f"{self.url}/archive",
            headers={"Accept": Consts.mediaTypeMigrationPreview},
        )
        return data["data"]

    def delete(self):
        """
        :calls: `DELETE /user/migrations/{migration_id}/archive <https://docs.github.com/en/rest/reference/migrations>`_
        """
        headers, data = self._requester.requestJsonAndCheck(
            "DELETE",
            f"{self.url}/archive",
            headers={"Accept": Consts.mediaTypeMigrationPreview},
        )

    def unlock_repo(self, repo_name):
        """
        :calls: `DELETE /user/migrations/{migration_id}/repos/{repo_name}/lock <https://docs.github.com/en/rest/reference/migrations>`_
        :param repo_name: str
        :rtype: None
        """
        assert isinstance(repo_name, str), repo_name
        headers, data = self._requester.requestJsonAndCheck(
            "DELETE",
            f"{self.url}/repos/{repo_name}/lock",
            headers={"Accept": Consts.mediaTypeMigrationPreview},
        )

    def _initAttributes(self):
        self._id = github.GithubObject.NotSet
        self._owner = github.GithubObject.NotSet
        self._guid = github.GithubObject.NotSet
        self._state = github.GithubObject.NotSet
        self._lock_repositories = github.GithubObject.NotSet
        self._exclude_attachments = github.GithubObject.NotSet
        self._repositories = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "id" in attributes:
            self._id = self._makeIntAttribute(attributes["id"])
        if "owner" in attributes:
            self._owner = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["owner"]
            )
        if "guid" in attributes:
            self._guid = self._makeStringAttribute(attributes["guid"])
        if "state" in attributes:
            self._state = self._makeStringAttribute(attributes["state"])
        if "lock_repositories" in attributes:
            self._lock_repositories = self._makeBoolAttribute(
                attributes["lock_repositories"]
            )
        if "exclude_attachments" in attributes:
            self._exclude_attachments = self._makeBoolAttribute(
                attributes["exclude_attachments"]
            )
        if "repositories" in attributes:
            self._repositories = self._makeListOfClassesAttribute(
                github.Repository.Repository, attributes["repositories"]
            )
        if "url" in attributes:
            self._url = self._makeStringAttribute(attributes["url"])
        if "created_at" in attributes:
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "updated_at" in attributes:
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
