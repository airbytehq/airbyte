############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
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
from datetime import datetime
from typing import Any, Dict, Optional

import github.GithubObject
from github.GithubObject import Attribute, NotSet


class HookDeliverySummary(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents a Summary of HookDeliveries
    """

    def __repr__(self) -> str:
        return self.get__repr__({"id": self._id.value})

    @property
    def id(self) -> Optional[int]:
        """
        :type: integer
        """
        return self._id.value

    @property
    def guid(self) -> Optional[str]:
        """
        :type: string
        """
        return self._guid.value

    @property
    def delivered_at(self) -> Optional[datetime]:
        """
        :type: datetime
        """
        return self._delivered_at.value

    @property
    def redelivery(self) -> Optional[bool]:
        """
        :type: boolean
        """
        return self._redelivery.value

    @property
    def duration(self) -> Optional[float]:
        """
        :type: float
        """
        return self._duration.value

    @property
    def status(self) -> Optional[str]:
        """
        :type: string
        """
        return self._status.value

    @property
    def status_code(self) -> Optional[int]:
        """
        :type: integer
        """
        return self._status_code.value

    @property
    def event(self) -> Optional[str]:
        """
        :type: string
        """
        return self._event.value

    @property
    def action(self) -> Optional[str]:
        """
        :type: string
        """
        return self._action.value

    @property
    def installation_id(self) -> Optional[int]:
        """
        :type: integer
        """
        return self._installation_id.value

    @property
    def repository_id(self) -> Optional[int]:
        """
        :type: integer
        """
        return self._repository_id.value

    @property
    def url(self) -> Optional[str]:
        """
        :type: string
        """
        return self._url.value

    def _initAttributes(self) -> None:
        self._id: Attribute[int] = NotSet
        self._guid: Attribute[str] = NotSet
        self._delivered_at: Attribute[datetime] = NotSet
        self._redelivery: Attribute[bool] = NotSet
        self._duration: Attribute[float] = NotSet
        self._status: Attribute[str] = NotSet
        self._status_code: Attribute[int] = NotSet
        self._event: Attribute[str] = NotSet
        self._action: Attribute[str] = NotSet
        self._installation_id: Attribute[int] = NotSet
        self._repository_id: Attribute[int] = NotSet
        self._url: Attribute[str] = NotSet

    def _useAttributes(self, attributes: Dict[str, Any]):
        if "id" in attributes:  # pragma no branch
            self._id = self._makeIntAttribute(attributes["id"])
        if "guid" in attributes:  # pragma no branch
            self._guid = self._makeStringAttribute(attributes["guid"])
        if "delivered_at" in attributes:  # pragma no branch
            self._delivered_at = self._makeDatetimeAttribute(attributes["delivered_at"])
        if "redelivery" in attributes:  # pragma no branch
            self._redelivery = self._makeBoolAttribute(attributes["redelivery"])
        if "duration" in attributes:  # pragma no branch
            self._duration = self._makeFloatAttribute(attributes["duration"])
        if "status" in attributes:  # pragma no branch
            self._status = self._makeStringAttribute(attributes["status"])
        if "status_code" in attributes:  # pragma no branch
            self._status_code = self._makeIntAttribute(attributes["status_code"])
        if "event" in attributes:  # pragma no branch
            self._event = self._makeStringAttribute(attributes["event"])
        if "action" in attributes:  # pragma no branch
            self._action = self._makeStringAttribute(attributes["action"])
        if "installation_id" in attributes:  # pragma no branch
            self._installation_id = self._makeIntAttribute(
                attributes["installation_id"]
            )
        if "repository_id" in attributes:  # pragma no branch
            self._repository_id = self._makeIntAttribute(attributes["repository_id"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])


class HookDeliveryRequest(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents a HookDeliveryRequest
    """

    def __repr__(self) -> str:
        return self.get__repr__({"payload": self._payload.value})

    @property
    def headers(self) -> Optional[dict]:
        """
        :type: dict
        """
        return self._request_headers.value

    @property
    def payload(self) -> Optional[dict]:
        """
        :type: dict
        """
        return self._payload.value

    def _initAttributes(self) -> None:
        self._request_headers: Attribute[Dict] = NotSet
        self._payload: Attribute[Dict] = NotSet

    def _useAttributes(self, attributes: Dict[str, Any]) -> None:
        if "headers" in attributes:  # pragma no branch
            self._request_headers = self._makeDictAttribute(attributes["headers"])
        if "payload" in attributes:  # pragma no branch
            self._payload = self._makeDictAttribute(attributes["payload"])


class HookDeliveryResponse(github.GithubObject.NonCompletableGithubObject):
    """
    This class represents a HookDeliveryResponse
    """

    def __repr__(self) -> str:
        return self.get__repr__({"payload": self._payload.value})

    @property
    def headers(self) -> Optional[dict]:
        """
        :type: dict
        """
        return self._response_headers.value

    @property
    def payload(self) -> Optional[str]:
        """
        :type: str
        """
        return self._payload.value

    def _initAttributes(self) -> None:
        self._response_headers: Attribute[Dict] = NotSet
        self._payload: Attribute[str] = NotSet

    def _useAttributes(self, attributes: Dict[str, Any]) -> None:
        if "headers" in attributes:  # pragma no branch
            self._response_headers = self._makeDictAttribute(attributes["headers"])
        if "payload" in attributes:  # pragma no branch
            self._payload = self._makeStringAttribute(attributes["payload"])


class HookDelivery(HookDeliverySummary):
    """
    This class represents a HookDelivery
    """

    def __repr__(self) -> str:
        return self.get__repr__({"id": self._id.value})

    @property
    def request(self) -> Optional[HookDeliveryRequest]:
        """
        :type: :class:`HookDeliveryRequest`
        """
        return self._request.value

    @property
    def response(self) -> Optional[HookDeliveryResponse]:
        """
        :type: :class:`HookDeliveryResponse`
        """
        return self._response.value

    def _initAttributes(self) -> None:
        super()._initAttributes()
        self._request: Attribute[HookDeliveryRequest] = NotSet
        self._response: Attribute[HookDeliveryResponse] = NotSet

    def _useAttributes(self, attributes: Dict[str, Any]) -> None:
        super()._useAttributes(attributes)
        if "request" in attributes:  # pragma no branch
            self._request = self._makeClassAttribute(
                HookDeliveryRequest, attributes["request"]
            )
        if "response" in attributes:  # pragma no branch
            self._response = self._makeClassAttribute(
                HookDeliveryResponse, attributes["response"]
            )
            # self._response = self._makeDictAttribute(attributes["response"])
