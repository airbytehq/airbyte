############################ Copyrights and license ############################
#                                                                              #
# Copyright 2019 Nick Campbell <nicholas.j.campbell@gmail.com>                 #
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
import github.TimelineEventSource


class TimelineEvent(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents IssueTimelineEvents. The reference can be found here https://docs.github.com/en/rest/reference/issues#timeline
    """

    def __repr__(self):
        return self.get__repr__({"id": self._id.value})

    @property
    def actor(self):
        """
        :type: :class:`github.NamedUser.NamedUser`
        """
        return self._actor.value

    @property
    def commit_id(self):
        """
        :type: string
        """
        return self._commit_id.value

    @property
    def created_at(self):
        """
        :type: datetime.datetime
        """
        return self._created_at.value

    @property
    def event(self):
        """
        :type: string
        """
        return self._event.value

    @property
    def id(self):
        """
        :type: integer
        """
        return self._id.value

    @property
    def node_id(self):
        """
        :type: string
        """
        return self._node_id.value

    @property
    def commit_url(self):
        """
        :type: string
        """
        return self._commit_url.value

    @property
    def source(self):
        """
        :type: :class:`github.TimelineEventSource.TimelineEventSource`
        """
        # only available on `cross-referenced` events.
        if (
            self.event == "cross-referenced"
            and self._source is not github.GithubObject.NotSet
        ):
            return self._source.value
        return None

    @property
    def body(self):
        """
        :type string
        """
        if self.event == "commented" and self._body is not github.GithubObject.NotSet:
            return self._body.value
        return None

    @property
    def author_association(self):
        """
        :type string
        """
        if (
            self.event == "commented"
            and self._author_association is not github.GithubObject.NotSet
        ):
            return self._author_association.value
        return None

    @property
    def url(self):
        """
        :type: string
        """
        return self._url.value

    def _initAttributes(self):
        self._actor = github.GithubObject.NotSet
        self._commit_id = github.GithubObject.NotSet
        self._created_at = github.GithubObject.NotSet
        self._event = github.GithubObject.NotSet
        self._id = github.GithubObject.NotSet
        self._node_id = github.GithubObject.NotSet
        self._commit_url = github.GithubObject.NotSet
        self._source = github.GithubObject.NotSet
        self._body = github.GithubObject.NotSet
        self._author_association = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "actor" in attributes:  # pragma no branch
            self._actor = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["actor"]
            )
        if "commit_id" in attributes:  # pragma no branch
            self._commit_id = self._makeStringAttribute(attributes["commit_id"])
        if "created_at" in attributes:  # pragma no branch
            self._created_at = self._makeDatetimeAttribute(attributes["created_at"])
        if "event" in attributes:  # pragma no branch
            self._event = self._makeStringAttribute(attributes["event"])
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "node_id" in attributes:  # pragma no branch
            self._node_id = self._makeStringAttribute(attributes["node_id"])
        if "commit_url" in attributes:  # pragma no branch
            self._commit_url = self._makeStringAttribute(attributes["commit_url"])
        if "source" in attributes:  # pragma no branch
            self._source = self._makeClassAttribute(
                github.TimelineEventSource.TimelineEventSource, attributes["source"]
            )
        if "body" in attributes:  # pragma no branch
            self._body = self._makeStringAttribute(attributes["body"])
        if "author_association" in attributes:  # pragma no branch
            self._author_association = self._makeStringAttribute(
                attributes["author_association"]
            )
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
