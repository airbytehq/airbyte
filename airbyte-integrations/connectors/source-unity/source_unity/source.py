#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from source_unity.streams import Campaigns, Apps, Creatives, CreativePacks


class SourceUnity(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["auth_token"], auth_method="Basic")
        args = {
            "authenticator": auth,
            "config": config
        }
        return [Campaigns(**args), Apps(**args), Creatives(**args), CreativePacks(**args)]
