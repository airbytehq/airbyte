############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2014 Thialfihar <thi@thialfihar.org>                               #
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

import base64

import github.GithubObject
import github.Repository


class ContentFile(github.GithubObject.CompletableGithubObject):
    """
    This class represents ContentFiles. The reference can be found here https://docs.github.com/en/rest/reference/repos#contents
    """

    def __repr__(self):
        return self.get__repr__({"path": self._path.value})

    @property
    def content(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._content)
        return self._content.value

    @property
    def decoded_content(self):
        """
        :type: bytes
        """
        assert self.encoding == "base64", f"unsupported encoding: {self.encoding}"
        return base64.b64decode(bytearray(self.content, "utf-8"))

    @property
    def download_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._download_url)
        return self._download_url.value

    @property
    def encoding(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._encoding)
        return self._encoding.value

    @property
    def git_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._git_url)
        return self._git_url.value

    @property
    def html_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._html_url)
        return self._html_url.value

    @property
    def license(self):
        """
        :type: :class:`github.License.License`
        """
        self._completeIfNotSet(self._license)
        return self._license.value

    @property
    def name(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._name)
        return self._name.value

    @property
    def path(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._path)
        return self._path.value

    @property
    def repository(self):
        """
        :type: :class:`github.Repository.Repository`
        """
        if self._repository is github.GithubObject.NotSet:
            # The repository was not set automatically, so it must be looked up by url.
            repo_url = "/".join(
                self.url.split("/")[:6]
            )  # pragma no cover (Should be covered)
            self._repository = github.GithubObject._ValuedAttribute(
                github.Repository.Repository(
                    self._requester, self._headers, {"url": repo_url}, completed=False
                )
            )  # pragma no cover (Should be covered)
        return self._repository.value

    @property
    def sha(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._sha)
        return self._sha.value

    @property
    def size(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._size)
        return self._size.value

    @property
    def type(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._type)
        return self._type.value

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    @property
    def text_matches(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._text_matches)
        return self._text_matches.value

    def _initAttributes(self):
        self._content = github.GithubObject.NotSet
        self._text_matches = github.GithubObject.NotSet
        self._encoding = github.GithubObject.NotSet
        self._download_url = github.GithubObject.NotSet
        self._git_url = github.GithubObject.NotSet
        self._html_url = github.GithubObject.NotSet
        self._license = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._path = github.GithubObject.NotSet
        self._repository = github.GithubObject.NotSet
        self._sha = github.GithubObject.NotSet
        self._size = github.GithubObject.NotSet
        self._type = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "content" in attributes:  # pragma no branch
            self._content = self._makeStringAttribute(attributes["content"])
        if "download_url" in attributes:  # pragma no branch
            self._download_url = self._makeStringAttribute(attributes["download_url"])
        if "encoding" in attributes:  # pragma no branch
            self._encoding = self._makeStringAttribute(attributes["encoding"])
        if "git_url" in attributes:  # pragma no branch
            self._git_url = self._makeStringAttribute(attributes["git_url"])
        if "html_url" in attributes:  # pragma no branch
            self._html_url = self._makeStringAttribute(attributes["html_url"])
        if "license" in attributes:  # pragma no branch
            self._license = self._makeClassAttribute(
                github.License.License, attributes["license"]
            )
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "path" in attributes:  # pragma no branch
            self._path = self._makeStringAttribute(attributes["path"])
        if "repository" in attributes:  # pragma no branch
            self._repository = self._makeClassAttribute(
                github.Repository.Repository, attributes["repository"]
            )
        if "sha" in attributes:  # pragma no branch
            self._sha = self._makeStringAttribute(attributes["sha"])
        if "size" in attributes:  # pragma no branch
            self._size = self._makeIntAttribute(attributes["size"])
        if "type" in attributes:  # pragma no branch
            self._type = self._makeStringAttribute(attributes["type"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
        if "text_matches" in attributes:  # pragma no branch
            self._text_matches = self._makeListOfDictsAttribute(
                attributes["text_matches"]
            )
