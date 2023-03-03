from typing import Any, List, Mapping, Tuple

import requests
from http import HTTPStatus
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator, NoAuth

from .streams import *


class SourceProjectSync(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        response = requests.get('https://www.xledger.net/')
        if response.status_code == HTTPStatus.OK:
            return True, None
        else:
            return False, 'Failed to connect to https://www.xledger.net/.'

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = NoAuth()
        return [
            FinanceStream(authenticator=auth),
            StaffTrackStream(authenticator=auth)
        ]
