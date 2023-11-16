#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from source_ironsource.streams import Creatives


# Basic full refresh stream
class SourceIronsource(AbstractSource):

    def get_access_token(self, config) -> str:
        headers = {
            "secretkey": config["secret_key"],
            "refreshToken": config["refresh_token"]
        }

        url = f"https://platform.ironsrc.com/partners/publisher/auth"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        token = response.text.replace('"', "")
        return token

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        access_token = self.get_access_token(config)

        if access_token:
            auth = TokenAuthenticator(token=access_token).get_auth_header()

            try:
                response = requests.get(f"https://api.ironsrc.com/advertisers/v2/creatives", headers=auth)
                response.raise_for_status()
                return True, None
            except requests.exceptions.RequestException as e:
                return False, e
        return False, "Token not found"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        print(self.check_connection(None, config))
        access_token = self.get_access_token(config)
        auth = TokenAuthenticator(token=access_token)

        args = {
            "authenticator": auth
        }
        return [Creatives(**args)]
