# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from types import MappingProxyType
from typing import Mapping, Union


class HttpResponse:
    def __init__(
        self,
        body: Union[str, bytes],
        status_code: int = 200,
        headers: Mapping[str, str] = MappingProxyType({}),
    ):
        self._body = body
        self._status_code = status_code
        self._headers = headers

    @property
    def body(self) -> Union[str, bytes]:
        return self._body

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def headers(self) -> Mapping[str, str]:
        return self._headers
