############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2014 Andrew Scheller <github@loowis.durge.org>                     #
# Copyright 2014 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2016 Jakub Wilk <jwilk@jwilk.net>                                  #
# Copyright 2016 Jannis Gebauer <ja.geb@me.com>                                #
# Copyright 2016 Peter Buckley <dx-pbuckley@users.noreply.github.com>          #
# Copyright 2016 Sam Corbett <sam.corbett@cloudsoftcorp.com>                   #
# Copyright 2018 Shubham Singh <41840111+singh811@users.noreply.github.com>    #
# Copyright 2018 h.shi <10385628+AnYeMoWang@users.noreply.github.com>          #
# Copyright 2018 sfdye <tsfdye@gmail.com>                                      #
# Copyright 2019 Adam Baratz <adam.baratz@gmail.com>                           #
# Copyright 2019 Steve Kowalik <steven@wedontsleep.org>                        #
# Copyright 2019 Wan Liuyang <tsfdye@gmail.com>                                #
# Copyright 2020 Steve Kowalik <steven@wedontsleep.org>                        #
# Copyright 2021 Steve Kowalik <steven@wedontsleep.org>                        #
# Copyright 2023 Jonathan Leitschuh <Jonathan.Leitschuh@gmail.com>             #
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

import datetime
import typing
from operator import itemgetter
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    Union,
)

from . import Consts
from .GithubException import BadAttributeException, IncompletableObject

if TYPE_CHECKING:
    from .Requester import Requester

T = typing.TypeVar("T")


class Attribute(Generic[T]):
    @property
    def value(self) -> T:
        raise NotImplementedError


class _NotSetType(Attribute):
    def __repr__(self):
        return "NotSet"

    @property
    def value(self):
        return None

    @staticmethod
    def remove_unset_items(data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: value
            for key, value in data.items()
            if not isinstance(value, _NotSetType)
        }


NotSet = _NotSetType()

Opt = Union[T, _NotSetType]


class _ValuedAttribute(Attribute, Generic[T]):
    def __init__(self, value: T):
        self._value = value

    @property
    def value(self) -> T:
        return self._value


class _BadAttribute(Attribute):
    def __init__(
        self, value: Any, expectedType: Any, exception: Optional[Exception] = None
    ):
        self.__value = value
        self.__expectedType = expectedType
        self.__exception = exception

    @property
    def value(self):
        raise BadAttributeException(self.__value, self.__expectedType, self.__exception)


class GithubObject:
    """
    Base class for all classes representing objects returned by the API.
    """

    """
    A global debug flag to enable header validation by requester for all objects
    """
    CHECK_AFTER_INIT_FLAG = False
    _url: Attribute[str]

    @classmethod
    def setCheckAfterInitFlag(cls, flag: bool) -> None:
        cls.CHECK_AFTER_INIT_FLAG = flag

    def __init__(
        self,
        requester: "Requester",
        headers: Dict[str, Union[str, int]],
        attributes: Any,
        completed: bool,
    ):
        self._requester = requester
        self._initAttributes()
        self._storeAndUseAttributes(headers, attributes)

        # Ask requester to do some checking, for debug and test purpose
        # Since it's most handy to access and kinda all-knowing
        if self.CHECK_AFTER_INIT_FLAG:  # pragma no branch (Flag always set in tests)
            requester.check_me(self)

    def _storeAndUseAttributes(
        self, headers: Dict[str, Union[str, int]], attributes: Any
    ) -> None:
        # Make sure headers are assigned before calling _useAttributes
        # (Some derived classes will use headers in _useAttributes)
        self._headers = headers
        self._rawData = attributes
        self._useAttributes(attributes)

    @property
    def raw_data(self) -> Dict[str, Any]:
        """
        :type: dict
        """
        self._completeIfNeeded()
        return self._rawData

    @property
    def raw_headers(self) -> Dict[str, Union[str, int]]:
        """
        :type: dict
        """
        self._completeIfNeeded()
        return self._headers

    @staticmethod
    def _parentUrl(url: str) -> str:
        return "/".join(url.split("/")[:-1])

    @staticmethod
    def __makeSimpleAttribute(value: Any, type: Type[T]) -> Attribute[T]:
        if value is None or isinstance(value, type):
            return _ValuedAttribute(value)  # type: ignore
        else:
            return _BadAttribute(value, type)  # type: ignore

    @staticmethod
    def __makeSimpleListAttribute(value: list, type: Type[T]) -> Attribute[T]:
        if isinstance(value, list) and all(
            isinstance(element, type) for element in value
        ):
            return _ValuedAttribute(value)  # type: ignore
        else:
            return _BadAttribute(value, [type])  # type: ignore

    @staticmethod
    def __makeTransformedAttribute(
        value: T, type: Type[T], transform: Callable[[T], Any]
    ) -> Attribute[T]:
        if value is None:
            return _ValuedAttribute(None)  # type: ignore
        elif isinstance(value, type):
            try:
                return _ValuedAttribute(transform(value))
            except Exception as e:
                return _BadAttribute(value, type, e)  # type: ignore
        else:
            return _BadAttribute(value, type)  # type: ignore

    @staticmethod
    def _makeStringAttribute(value: Optional[Union[int, str]]) -> Attribute[str]:
        return GithubObject.__makeSimpleAttribute(value, str)

    @staticmethod
    def _makeIntAttribute(value: Optional[Union[int, str]]) -> Attribute[int]:
        return GithubObject.__makeSimpleAttribute(value, int)

    @staticmethod
    def _makeFloatAttribute(value: Optional[float]) -> Attribute[float]:
        return GithubObject.__makeSimpleAttribute(value, float)

    @staticmethod
    def _makeBoolAttribute(value: Optional[bool]) -> Attribute[bool]:
        return GithubObject.__makeSimpleAttribute(value, bool)

    @staticmethod
    def _makeDictAttribute(value: Dict[str, Any]) -> Attribute[dict]:
        return GithubObject.__makeSimpleAttribute(value, dict)

    @staticmethod
    def _makeTimestampAttribute(value: int) -> Attribute[int]:
        return GithubObject.__makeTransformedAttribute(
            value, int, datetime.datetime.utcfromtimestamp
        )

    @staticmethod
    def _makeDatetimeAttribute(value: Optional[Union[int, str]]) -> Attribute:
        def parseDatetime(s):
            if (
                len(s) == 24
            ):  # pragma no branch (This branch was used only when creating a download)
                # The Downloads API has been removed. I'm keeping this branch because I have no mean
                # to check if it's really useless now.
                return datetime.datetime.strptime(
                    s, "%Y-%m-%dT%H:%M:%S.000Z"
                )  # pragma no cover (This branch was used only when creating a download)
            elif len(s) >= 25:
                return datetime.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S") + (
                    1 if s[19] == "-" else -1
                ) * datetime.timedelta(hours=int(s[20:22]), minutes=int(s[23:25]))
            else:
                return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")

        return GithubObject.__makeTransformedAttribute(value, str, parseDatetime)

    def _makeClassAttribute(self, klass: Any, value: Any) -> Attribute:
        return GithubObject.__makeTransformedAttribute(
            value,
            dict,
            lambda value: klass(self._requester, self._headers, value, completed=False),
        )

    @staticmethod
    def _makeListOfStringsAttribute(
        value: Union[List[List[str]], List[str], List[Union[str, int]]]
    ) -> Attribute:
        return GithubObject.__makeSimpleListAttribute(value, str)

    @staticmethod
    def _makeListOfIntsAttribute(value: List[int]) -> Attribute:
        return GithubObject.__makeSimpleListAttribute(value, int)

    @staticmethod
    def _makeListOfDictsAttribute(
        value: List[Dict[str, Union[str, List[Dict[str, Union[str, List[int]]]]]]]
    ) -> Attribute:
        return GithubObject.__makeSimpleListAttribute(value, dict)

    @staticmethod
    def _makeListOfListOfStringsAttribute(
        value: List[List[str]],
    ) -> Attribute:
        return GithubObject.__makeSimpleListAttribute(value, list)

    def _makeListOfClassesAttribute(
        self, klass: Any, value: Any
    ) -> Union[_ValuedAttribute, _BadAttribute]:
        if isinstance(value, list) and all(
            isinstance(element, dict) for element in value
        ):
            return _ValuedAttribute(
                [
                    klass(self._requester, self._headers, element, completed=False)
                    for element in value
                ]
            )
        else:
            return _BadAttribute(value, [dict])

    def _makeDictOfStringsToClassesAttribute(
        self,
        klass: Type["NonCompletableGithubObject"],
        value: Dict[
            str,
            Union[int, Dict[str, Union[str, int, None]], Dict[str, Union[str, int]]],
        ],
    ) -> Union[_ValuedAttribute, _BadAttribute]:
        if isinstance(value, dict) and all(
            isinstance(key, str) and isinstance(element, dict)
            for key, element in value.items()
        ):
            return _ValuedAttribute(
                {
                    key: klass(self._requester, self._headers, element, completed=False)
                    for key, element in value.items()
                }
            )
        else:
            return _BadAttribute(value, {str: dict})

    @property
    def etag(self) -> Optional[str]:
        """
        :type: str
        """
        return self._headers.get(Consts.RES_ETAG)  # type: ignore

    @property
    def last_modified(self) -> Optional[str]:
        """
        :type: str
        """
        return self._headers.get(Consts.RES_LAST_MODIFIED)  # type: ignore

    def get__repr__(self, params: Dict[str, Any]) -> str:
        """
        Converts the object to a nicely printable string.
        """

        def format_params(params):
            items = list(params.items())
            for k, v in sorted(items, key=itemgetter(0), reverse=True):
                if isinstance(v, bytes):
                    v = v.decode("utf-8")
                if isinstance(v, str):
                    v = f'"{v}"'
                yield f"{k}={v}"

        return "{class_name}({params})".format(
            class_name=self.__class__.__name__,
            params=", ".join(list(format_params(params))),
        )

    def _initAttributes(self):
        raise NotImplementedError("BUG: Not Implemented _initAttributes")

    def _useAttributes(self, attributes):
        raise NotImplementedError("BUG: Not Implemented _useAttributes")

    def _completeIfNeeded(self):
        raise NotImplementedError("BUG: Not Implemented _completeIfNeeded")


class NonCompletableGithubObject(GithubObject):
    def _completeIfNeeded(self) -> None:
        pass


class CompletableGithubObject(GithubObject):
    def __init__(
        self,
        requester: "Requester",
        headers: Dict[str, Union[str, int]],
        attributes: Dict[str, Any],
        completed: bool,
    ):
        super().__init__(requester, headers, attributes, completed)
        self.__completed = completed

    def __eq__(self, other: Any) -> bool:
        return other.__class__ is self.__class__ and other._url.value == self._url.value

    def __hash__(self):
        return hash(self._url.value)

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def _completeIfNotSet(self, value: Attribute) -> None:
        if isinstance(value, _NotSetType):
            self._completeIfNeeded()

    def _completeIfNeeded(self) -> None:
        if not self.__completed:
            self.__complete()

    def __complete(self):
        if self._url.value is None:
            raise IncompletableObject(400, "Returned object contains no URL", None)
        headers, data = self._requester.requestJsonAndCheck("GET", self._url.value)
        self._storeAndUseAttributes(headers, data)
        self.__completed = True

    def update(self, additional_headers: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check and update the object with conditional request
        :rtype: Boolean value indicating whether the object is changed
        """
        conditionalRequestHeader = dict()
        if self.etag is not None:
            conditionalRequestHeader[Consts.REQ_IF_NONE_MATCH] = self.etag
        if self.last_modified is not None:
            conditionalRequestHeader[Consts.REQ_IF_MODIFIED_SINCE] = self.last_modified
        if additional_headers is not None:
            conditionalRequestHeader.update(additional_headers)

        status, responseHeaders, output = self._requester.requestJson(
            "GET", self._url.value, headers=conditionalRequestHeader
        )
        if status == 304:
            return False
        else:
            headers, data = self._requester._Requester__check(  # type: ignore
                status, responseHeaders, output
            )
            self._storeAndUseAttributes(headers, data)
            self.__completed = True
            return True
