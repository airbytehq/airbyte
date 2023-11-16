#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class IronsourceStream(HttpStream, ABC):
    url_base = "https://api.ironsrc.com/advertisers/v2/"
    use_cache = True  # it is used in all streams

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class Creatives(IronsourceStream):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "creatives"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.text == "":
            return '{}'
        yield from response.json()["creatives"]
