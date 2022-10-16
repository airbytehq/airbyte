#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Dict, Iterator, Tuple

from airbyte_cdk.sources.deprecated.client import BaseClient

from .api import APIClient
from .common import AuthError, ValidationError


class DriftAuthenticator:
    def __init__(self, config: Dict):
        self.config = config

    def get_token(self) -> str:
        access_token = self.config.get("access_token")
        if access_token:
            return access_token
        else:
            return self.config.get("credentials").get("access_token")


class Client(BaseClient):
    def __init__(self, **config: Dict):
        super().__init__()
        self._client = APIClient(access_token=DriftAuthenticator(config).get_token())

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
