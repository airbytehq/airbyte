#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


CURRENCYLAYER_URL = "https://api.currencylayer.com/"


# Basic full refresh stream
class CurrencylayerLive(HttpStream, ABC):
    name = "currencylayer_live"
    url_base = CURRENCYLAYER_URL
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.config_param = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, **kwargs) -> str:
        return f"live?access_key={self.config_param['access_key']}&source={self.config_param['source']}&currencies=JPY,CAD,GBP,EUR"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                quotes = {}
                for key, val in data["quotes"].items():
                    quotes[key[3:6]] = val
                data["quotes"] = quotes
                data.pop("success")
                data.pop("terms")
                data.pop("privacy")
                yield from [data]
            else:
                raise Exception([{"message": "Only AES decryption is implemented. result:"+data}])
        else:
            raise Exception([{"message": "Only AES decryption is implemented."}])

# Source
class SourceCurrencylayer(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url = CURRENCYLAYER_URL+"/list?access_key="+config["access_key"]
        result = requests.get(url)
        if result.status_code == 200:
            data = result.json()
            if not bool(data["success"]):
                return False, f"No streams to connect to from source -> {data['error']}"
            return True, None
        else:
            return False, f"No streams to connect to from source -> {result.text}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [CurrencylayerLive(config=config)]
