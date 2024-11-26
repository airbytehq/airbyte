############################ Copyrights and license ############################
#                                                                              #
# Copyright 2017 Chris McBride <thehighlander@users.noreply.github.com>        #
# Copyright 2017 Simon <spam@esemi.ru>                                         #
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


class GitReleaseAsset(github.GithubObject.CompletableGithubObject):
    """
    This class represents GitReleaseAssets. The reference can be found here https://docs.github.com/en/rest/reference/repos#releases
    """

    def __repr__(self):
        return self.get__repr__({"url": self.url})

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    @property
    def id(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._id)
        return self._id.value

    @property
    def name(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._name)
        return self._name.value

    @property
    def label(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._label)
        return self._label.value

    @property
    def content_type(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._content_type)
        return self._content_type.value

    @property
    def state(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._state)
        return self._state.value

    @property
    def size(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._size)
        return self._size.value

    @property
    def download_count(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._download_count)
        return self._download_count.value

    @property
    def created_at(self):
        """
        :type: datetime
        """
        self._completeIfNotSet(self._created_at)
        return self._created_at.value

    @property
    def updated_at(self):
        """
        :type: datetime
        """
        self._completeIfNotSet(self._updated_at)
        return self._updated_at.value

    @property
    def browser_download_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._browser_download_url)
        return self._browser_download_url.value

    @property
    def uploader(self):
        """
        :type: github.NamedUser.NamedUser
        """
        self._completeIfNotSet(self._uploader)
        return self._uploader.value

    def delete_asset(self):
        """
        Delete asset from the release.
        :rtype: bool
        """
        headers, data = self._requester.requestJsonAndCheck("DELETE", self.url)
        return True

    def update_asset(self, name, label=""):
        """
        Update asset metadata.
        :rtype: github.GitReleaseAsset.GitReleaseAsset
        """
        assert isinstance(name, str), name
        assert isinstance(label, str), label
        post_parameters = {"name": name, "label": label}
        headers, data = self._requester.requestJsonAndCheck(
            "PATCH", self.url, input=post_parameters
        )
        return GitReleaseAsset(self._requester, headers, data, completed=True)

    def _initAttributes(self):
        self._url = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._label = github.GithubObject.NotSet
        self._uploader = github.GithubObject.NotSet
        self._content_type = github.GithubObject.NotSet
        self._state = github.GithubObject.NotSet
        self._size = github.GithubObject.NotSet
        self._download_count = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet
        self._browser_download_url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "label" in attributes:  # pragma no branch
            self._label = self._makeStringAttribute(attributes["label"])
        if "uploader" in attributes:  # pragma no branch
            self._uploader = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["uploader"]
            )
        if "content_type" in attributes:  # pragma no branch
            self._content_type = self._makeStringAttribute(attributes["content_type"])
        if "state" in attributes:  # pragma no branch
            self._state = self._makeStringAttribute(attributes["state"])
        if "size" in attributes:  # pragma no branch
            self._size = self._makeIntAttribute(attributes["size"])
        if "download_count" in attributes:  # pragma no branch
            self._download_count = self._makeIntAttribute(attributes["download_count"])
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "updated_at" in attributes:  # pragma no branch
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
        if "browser_download_url" in attributes:  # pragma no branch
            self._browser_download_url = self._makeStringAttribute(
                attributes["browser_download_url"]
            )
