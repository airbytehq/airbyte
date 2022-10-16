#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping, Tuple

from airbyte_cdk.sources.deprecated.client import BaseClient

from .api import API, GroupMembersAPI, GroupsAPI, UsersAPI


class Client(BaseClient):
    def __init__(self, credentials: Mapping[str, Any] = None, credentials_json: str = None, email: str = None):
        # supporting old config format
        if not credentials:
            credentials = {"credentials_json": credentials_json, "email": email}
        self._api = API(credentials)
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
