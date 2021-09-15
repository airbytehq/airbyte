#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from itertools import cycle
from typing import Any, List, Mapping

from requests.auth import AuthBase


class MultipleTokenAuthenticator(AuthBase):
    """
    Builds auth header, based on the list of tokens provided.
    Auth header is changed per each `get_auth_header` call, using each token in cycle.
    The token is attached to each request via the `auth_header` header.
    """

    def __init__(self, tokens: List[str], auth_method: str = "Bearer", auth_header: str = "Authorization"):
        self.auth_method = auth_method
        self.auth_header = auth_header
        self._tokens = tokens
        self._tokens_iter = cycle(self._tokens)

    def __call__(self, request):
        request.headers.update(self.get_auth_header())
        return request

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f"{self.auth_method} {next(self._tokens_iter)}"}


class TokenAuthenticator(MultipleTokenAuthenticator):
    """
    Builds auth header, based on the token provided.
    The token is attached to each request via the `auth_header` header.
    """

    def __init__(self, token: str, auth_method: str = "Bearer", auth_header: str = "Authorization"):
        super().__init__([token], auth_method, auth_header)
