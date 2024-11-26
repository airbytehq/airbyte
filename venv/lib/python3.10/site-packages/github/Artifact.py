############################ Copyrights and license ############################
#                                                                              #
# Copyright 2022 Aleksei Fedotov <aleksei@fedotov.email>                       #
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
import github.WorkflowRun


class Artifact(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents an Artifact of Github Run
    """

    def __repr__(self):
        return self.get__repr__({"name": self._name.value, "id": self._id.value})

    @property
    def archive_download_url(self):
        """
        :type: string
        """
        return self._archive_download_url.value

    @property
    def created_at(self):
        """
        :type: datetime.datetime
        """
        return self._created_at.value

    @property
    def expired(self):
        """
        :type: bool
        """
        return self._expired.value

    @property
    def expires_at(self):
        """
        :type: datetime.datetime
        """
        return self._expires_at.value

    @property
    def head_sha(self):
        """
        :type: string
        """
        return self._head_sha.value

    @property
    def id(self):
        """
        :type: string
        """
        return self._id.value

    @property
    def name(self):
        """
        :type: string
        """
        return self._name.value

    @property
    def node_id(self):
        """
        :type: string
        """
        return self._node_id.value

    @property
    def size_in_bytes(self):
        """
        :type: integer
        """
        return self._size_in_bytes.value

    @property
    def updated_at(self):
        """
        :type: datetime.datetime
        """
        return self._updated_at.value

    @property
    def url(self):
        """
        :type: string
        """
        return self._url.value

    @property
    def workflow_run(self):
        """
        :type: :class:``
        """
        return self._workflow_run.value

    def delete(self) -> bool:
        """
        :calls: `DELETE /repos/{owner}/{repo}/actions/artifacts/{artifact_id} <https://docs.github.com/en/rest/actions/artifacts#delete-an-artifact>`_
        :rtype: bool
        """
        status, headers, data = self._requester.requestBlob("DELETE", self.url)
        return status == 204

    def _initAttributes(self):
        self._archive_download_url = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._expired = github.GithubObject.NotSet
        self._expires_at = github.GithubObject.NotSet
        self._head_sha = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._name = github.GithubObject.NotSet
        self._node_id = github.GithubObject.NotSet
        self._size_in_bytes = github.GithubObject.NotSet
        self._updated_at = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet
        self._workflow_run = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "archive_download_url" in attributes:  # pragma no branch
            self._archive_download_url = self._makeStringAttribute(
                attributes["archive_download_url"]
            )
        if "created_at" in attributes:  # pragma no branch
            assert attributes["created_at"] is None or isinstance(
                attributes["created_at"], (str,)
            ), attributes["created_at"]
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "expired" in attributes:  # pragma no branch
            self._expired = self._makeBoolAttribute(attributes["expired"])
        if "expires_at" in attributes:  # pragma no branch
            assert attributes["expires_at"] is None or isinstance(
                attributes["expires_at"], (str,)
            ), attributes["expires_at"]
            self._expires_at = self._makeDatetimeAttribute(attributes["expires_at"])
        if "head_sha" in attributes:  # pragma no branch
            self._head_sha = self._makeStringAttribute(attributes["head_sha"])
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "name" in attributes:  # pragma no branch
            self._name = self._makeStringAttribute(attributes["name"])
        if "node_id" in attributes:  # pragma no branch
            self._node_id = self._makeStringAttribute(attributes["node_id"])
        if "size_in_bytes" in attributes:  # pragma no branch
            self._size_in_bytes = self._makeIntAttribute(attributes["size_in_bytes"])
        if "updated_at" in attributes:  # pragma no branch
            assert attributes["updated_at"] is None or isinstance(
                attributes["updated_at"], (str,)
            ), attributes["updated_at"]
            self._updated_at = self._makeDatetimeAttribute(attributes["updated_at"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
        if "workflow_run" in attributes:  # pragma no branch
            self._workflow_run = self._makeClassAttribute(
                github.WorkflowRun.WorkflowRun, attributes["workflow_run"]
            )
