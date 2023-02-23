#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import requests
from abc import ABC
from datetime import datetime
from typing import Dict, Generator
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources import Source


class KoboToolStream(HttpStream):
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.uid = config["uid"]
        token = self.get_access_token(config)
        self.auth_token = token[0]

    @property
    def url_base(self) -> str:
        return f"https://kf.kobotoolbox.org/api/v2/assets/{self.uid}/"

    def get_access_token(self, config) -> Tuple[str, any]:
        url = f"https://kf.kobotoolbox.org/token/?format=json"

        try:
            response = requests.post(url, auth=(config["username"], config["password"]))
            response.raise_for_status()
            json_response = response.json()
            return json_response.get("token", None), None if json_response is not None else None, None
        except requests.exceptions.RequestException as e:
            return None, e

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None
    
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "data.json"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Authorization": "Token " + self.auth_token}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        result = json_response.get('results')

        for a in result:
            yield a

class SourceKobotoolbox(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    # def generate_streams(self, config: str) -> List[Stream]:
    #     access_token = self.get_access_token(config)
    #     print(access_token)
    #     auth = access_token[0]
    #     print(f'==================>{auth}')
    #     url = f"https://kf.kobotoolbox.org/api/v2/assets.json"
    #     response = requests.get(url, auth=(config["username"], config["password"]))
    #     json_response = response.json()
    #     key_list=json_response.get('results')
    #     key = "uid"
    #     forms = [a_dict[key] for a_dict in key_list]
    #     print(f'=======assss=======>>>>{forms}')

    #     streams = []
    #     for form_id in forms:
    #         stream = KoboToolStream(config=config, form_id=form_id, auth=auth)
    #         stream.append(stream)
    #     return streams

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [KoboToolStream(config=config)]