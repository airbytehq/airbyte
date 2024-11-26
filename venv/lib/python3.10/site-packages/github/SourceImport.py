############################ Copyrights and license ############################
#                                                                              #
# Copyright 2018 Hayden Fuss <wifu1234@gmail.com>                              #
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
from github import Consts


class SourceImport(github.GithubObject.CompletableGithubObject):
    """
    This class represents SourceImports. The reference can be found here https://docs.github.com/en/rest/reference/migrations#source-imports
    """

    def __repr__(self):
        return self.get__repr__(
            {
                "vcs_url": self._vcs_url.value,
                "repository_url": self._repository_url.value,
                "status": self._status.value,
                "url": self._url.value,
            }
        )

    @property
    def authors_count(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._authors_count)
        return self._authors_count.value

    @property
    def authors_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._authors_url)
        return self._authors_url.value

    @property
    def has_large_files(self):
        """
        :type: bool
        """
        self._completeIfNotSet(self._has_large_files)
        return self._has_large_files.value

    @property
    def html_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._html_url)
        return self._html_url.value

    @property
    def large_files_count(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._large_files_count)
        return self._large_files_count.value

    @property
    def large_files_size(self):
        """
        :type: integer
        """
        self._completeIfNotSet(self._large_files_size)
        return self._large_files_size.value

    @property
    def repository_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._repository_url)
        return self._repository_url.value

    @property
    def status(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._status)
        return self._status.value

    @property
    def status_text(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._status_text)
        return self._status_text.value

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    @property
    def use_lfs(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._use_lfs)
        return self._use_lfs.value

    @property
    def vcs(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._vcs)
        return self._vcs.value

    @property
    def vcs_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._vcs_url)
        return self._vcs_url.value

    def update(self):
        import_header = {"Accept": Consts.mediaTypeImportPreview}
        return super().update(additional_headers=import_header)

    def _initAttributes(self):
        self._authors_count = github.GithubObject.NotSet
        self._authors_url = github.GithubObject.NotSet
        self._has_large_files = github.GithubObject.NotSet
        self._html_url = github.GithubObject.NotSet
        self._large_files_count = github.GithubObject.NotSet
        self._large_files_size = github.GithubObject.NotSet
        self._repository_url = github.GithubObject.NotSet
        self._status = github.GithubObject.NotSet
        self._status_text = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet
        self._use_lsf = github.GithubObject.NotSet
        self._vcs = github.GithubObject.NotSet
        self._vcs_url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "authors_count" in attributes:  # pragma no branch
            self._authors_count = self._makeIntAttribute(attributes["authors_count"])
        if "authors_url" in attributes:  # pragma no branch
            self._authors_url = self._makeStringAttribute(attributes["authors_url"])
        if "has_large_files" in attributes:  # pragma no branch
            self._has_large_files = self._makeBoolAttribute(
                attributes["has_large_files"]
            )
        if "html_url" in attributes:  # pragma no branch
            self._html_url = self._makeStringAttribute(attributes["html_url"])
        if "large_files_count" in attributes:  # pragma no branch
            self._large_files_count = self._makeIntAttribute(
                attributes["large_files_count"]
            )
        if "large_files_size" in attributes:  # pragma no branch
            self._large_files_size = self._makeIntAttribute(
                attributes["large_files_size"]
            )
        if "repository_url" in attributes:  # pragma no branch
            self._repository_url = self._makeStringAttribute(
                attributes["repository_url"]
            )
        if "status" in attributes:  # pragma no branch
            self._status = self._makeStringAttribute(attributes["status"])
        if "status_text" in attributes:  # pragma no branch
            self._status_text = self._makeStringAttribute(attributes["status_text"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
        if "use_lfs" in attributes:  # pragma no branch
            self._use_lfs = self._makeStringAttribute(attributes["use_lfs"])
        if "vcs" in attributes:  # pragma no branch
            self._vcs = self._makeStringAttribute(attributes["vcs"])
        if "vcs_url" in attributes:  # pragma no branch
            self._vcs_url = self._makeStringAttribute(attributes["vcs_url"])
