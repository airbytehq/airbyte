# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


class HttpResponse:
    def __init__(self, body: str, status_code: int = 200, headers: dict = {}):
        self._body = body
        self._status_code = status_code
        self._headers = headers

    @property
    def body(self) -> str:
        return self._body

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def headers(self) -> dict:
        return self._headers
