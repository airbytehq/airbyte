#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .streams import Blocks, Databases, Pages, Users


class SourceNotion(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = TokenAuthenticator(config["access_token"])
            stream = Users(authenticator=authenticator, config=config)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        AirbyteLogger().log("INFO", f"Using start_date: {config['start_date']}")

        authenticator = TokenAuthenticator(config["access_token"])
        args = {"authenticator": authenticator, "config": config}

        pages = Pages(**args)
        blocks = Blocks(parent=pages, **args)

        return [Users(**args), Databases(**args), pages, blocks]
