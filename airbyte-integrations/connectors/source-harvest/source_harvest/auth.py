#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator, TokenAuthenticator


class HarvestMixin:
    def __init__(self, *, account_id: str, account_id_header: str = "Harvest-Account-ID", **kwargs):
        super().__init__(**kwargs)
        self.account_id = account_id
        self.account_id_header = account_id_header

    def get_auth_header(self) -> Mapping[str, Any]:
        return {**super().get_auth_header(), self.account_id_header: self.account_id}


class HarvestTokenAuthenticator(HarvestMixin, TokenAuthenticator):
    pass


class HarvestOauth2Authenticator(HarvestMixin, Oauth2Authenticator):
    pass
