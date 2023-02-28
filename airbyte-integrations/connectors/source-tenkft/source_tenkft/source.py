#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_tenkft.streams import BillRates, ProjectAssignments, Projects, Users


# Source
class SourceTenkft(AbstractSource):
    @staticmethod
    def _get_authenticator(config: Mapping[str, Any]):
        return TenkftAuthenticator(api_key=config["api_key"])

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            args = self.connector_config(config)
            users = Users(**args).read_records(sync_mode=SyncMode.full_refresh)
            next(users, None)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = self.connector_config(config)
        return [Users(**args), Projects(**args), ProjectAssignments(**args), BillRates(**args)]

    def connector_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "authenticator": self._get_authenticator(config),
        }


class TenkftAuthenticator(requests.auth.AuthBase):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def __call__(self, r):
        r.headers["auth"] = self.api_key
        return r
