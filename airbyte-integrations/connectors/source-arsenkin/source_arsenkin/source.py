#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple, Optional

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class ArsenkinStream(HttpStream, ABC):
    """Base stream for Arsenkin"""
    url_base = "https://arsenkin.ru/tools/api/task/"

    def __init__(
            self,
            authenticator: Any = None,
            config: Optional[Mapping[str, Any]] = None,
    ):
        super().__init__(authenticator=authenticator)
        self.config = config

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        return response.json()

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        # TODO (may be raise NotImplementedError)
        pass

    def transform_config(self, user_config: dict[str, any], stream: "ArsenkinStream") -> MutableMapping[str, any]:
        """Process config"""
        # TODO
        pass


class ParserADS(ArsenkinStream):
    """Ads parser for Arsenkin"""

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    # TODO: check if this is correct
    primary_key = "task_id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        should return "customers". Required.
        """
        return "set"

    def request_params(
            self, **kwargs
    ) -> MutableMapping[str, Any]:
        # TODO: remake it!
        return {
            "token": self.config["token"],
            "tools_name": "parser-ads",
            "keywords": json.dumps(["Автомобили БУ"]),
            "region_yandex": 213,
            "device": "desktop",
        }


class SourceArsenkin(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        ads_stream: ArsenkinStream = self.streams(config)[0]
        try:
            stream_params: dict[str, any] = ads_stream.request_params().copy()
            stream_params["keywords"] = json.dumps(["Купить холодильник"])
            stream_params["device"] = "desktop"
            stream_params["region_yandex"] = 213
            test_response = requests.get(ads_stream.url_base + ads_stream.path(), params=stream_params)
            if test_response.status_code != 200:
                return False, test_response.text
            else:
                response_json = test_response.json()
                if "task_id" not in response_json:  # Task was not set successfully
                    return False, test_response.text
                else:  # Task was set successfully, cancel it
                    # TODO: discover, how to cancel task
                    return True, None
        except Exception as ex:
            return False, ex

    def streams(self, config: Mapping[str, Any]) -> List[ArsenkinStream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [ParserADS(authenticator=None, config=self.transform_config(config, ParserADS))]
