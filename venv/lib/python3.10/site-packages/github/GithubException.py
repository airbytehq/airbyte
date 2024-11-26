############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Cameron White <cawhite@pdx.edu>                               #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2014 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2016 Peter Buckley <dx-pbuckley@users.noreply.github.com>          #
# Copyright 2016 humbug <bah>                                                  #
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

import json
from typing import Any, Dict, List, Optional, Tuple, Type, Union


class GithubException(Exception):
    """
    Error handling in PyGithub is done with exceptions. This class is the base of all exceptions raised by PyGithub (but :class:`github.GithubException.BadAttributeException`).

    Some other types of exceptions might be raised by underlying libraries, for example for network-related issues.
    """

    def __init__(
        self,
        status: int,
        data: Union[str, Dict[str, Union[str, List[str], List[Dict[str, str]]]]],
        headers: Optional[Dict[str, str]],
    ):
        super().__init__()
        self.__status = status
        self.__data = data
        self.__headers = headers
        self.args = (status, data, headers)

    @property
    def status(self) -> int:
        """
        The status returned by the Github API
        """
        return self.__status

    @property
    def data(
        self,
    ) -> Union[str, Dict[str, Union[str, List[str], List[Dict[str, str]]]]]:
        """
        The (decoded) data returned by the Github API
        """
        return self.__data

    @property
    def headers(self) -> Optional[Dict[str, str]]:
        """
        The headers returned by the Github API
        """
        return self.__headers

    def __str__(self) -> str:
        return f"{self.status} {json.dumps(self.data)}"


class BadCredentialsException(GithubException):
    """
    Exception raised in case of bad credentials (when Github API replies with a 401 or 403 HTML status)
    """


class UnknownObjectException(GithubException):
    """
    Exception raised when a non-existing object is requested (when Github API replies with a 404 HTML status)
    """


class BadUserAgentException(GithubException):
    """
    Exception raised when request is sent with a bad user agent header (when Github API replies with a 403 bad user agent HTML status)
    """


class RateLimitExceededException(GithubException):
    """
    Exception raised when the rate limit is exceeded (when Github API replies with a 403 rate limit exceeded HTML status)
    """


class BadAttributeException(Exception):
    """
    Exception raised when Github returns an attribute with the wrong type.
    """

    def __init__(
        self,
        actualValue: Any,
        expectedType: Union[
            Dict[Tuple[Type[str], Type[str]], Type[dict]],
            Tuple[Type[str], Type[str]],
            List[Type[dict]],
            List[Tuple[Type[str], Type[str]]],
        ],
        transformationException: Optional[Exception],
    ):
        self.__actualValue = actualValue
        self.__expectedType = expectedType
        self.__transformationException = transformationException

    @property
    def actual_value(self) -> Any:
        """
        The value returned by Github
        """
        return self.__actualValue

    @property
    def expected_type(
        self,
    ) -> Union[
        List[Type[dict]],
        Tuple[Type[str], Type[str]],
        Dict[Tuple[Type[str], Type[str]], Type[dict]],
        List[Tuple[Type[str], Type[str]]],
    ]:
        """
        The type PyGithub expected
        """
        return self.__expectedType

    @property
    def transformation_exception(self) -> Optional[Exception]:
        """
        The exception raised when PyGithub tried to parse the value
        """
        return self.__transformationException


class TwoFactorException(GithubException):
    """
    Exception raised when Github requires a onetime password for two-factor authentication
    """


class IncompletableObject(GithubException):
    """
    Exception raised when we can not request an object from Github because the data returned did not include a URL
    """
