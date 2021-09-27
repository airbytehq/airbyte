#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


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
