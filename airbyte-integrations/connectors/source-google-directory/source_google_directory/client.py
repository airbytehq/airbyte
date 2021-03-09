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

from typing import Any, Mapping, Tuple

from base_python import BaseClient

from .api import API, GroupMembersAPI, GroupsAPI, UsersAPI


class Client(BaseClient):
    def __init__(self, credentials_json: str, email: str):
        self._api = API(credentials_json, email)
        self._apis = {"users": UsersAPI(self._api), "groups": GroupsAPI(self._api), "group_members": GroupMembersAPI(self._api)}
        super().__init__()

    def get_stream_state(self, name: str) -> Any:
        pass

    def set_stream_state(self, name: str, state: Any):
        pass

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {name: api.list for name, api in self._apis.items()}

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            params = {"customer": "my_customer"}
            self._api.get(name="users", params=params)
        except Exception as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg
