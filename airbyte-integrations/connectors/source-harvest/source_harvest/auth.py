#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class HarvestTokenAuthenticator(TokenAuthenticator):
    def __init__(self, token: str, account_id: str, account_id_header: str = "Harvest-Account-ID", **kwargs):
        super().__init__(token, **kwargs)
        self.account_id = account_id
        self.account_id_header = account_id_header

    def get_auth_header(self) -> Mapping[str, Any]:
        return {**super().get_auth_header(), self.account_id_header: self.account_id}
