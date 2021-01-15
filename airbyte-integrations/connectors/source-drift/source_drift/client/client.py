"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Iterator, Tuple

from base_python import BaseClient

from .api import APIClient
from .common import AuthError, ValidationError


class Client(BaseClient):
    def __init__(self, access_token: str):
        super().__init__()
        self._client = APIClient(access_token)

    def stream__accounts(self, **kwargs) -> Iterator[dict]:
        yield from self._client.accounts.list()

    def stream__users(self, **kwargs) -> Iterator[dict]:
        yield from self._client.users.list()

    def stream__conversations(self, **kwargs) -> Iterator[dict]:
        yield from self._client.conversations.list()

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            # we don't care about response, just checking authorisation
            self._client.check_token("definitely_not_a_token")
        except ValidationError:  # this is ok because `definitely_not_a_token`
            pass
        except AuthError as error:
            alive = False
            error_msg = str(error)

        return alive, error_msg
