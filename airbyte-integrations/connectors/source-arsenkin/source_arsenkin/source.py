#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import time
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple, Optional

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_protocol.models import SyncMode


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

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {"token": self.config["token"]}

    def _set_task_request(self) -> requests.Response:
        """Set task"""
        raise NotImplementedError()

    def _get_task_request(self, task_id) -> requests.Response:
        """Get task status response"""
        raise NotImplementedError()

    def _get_results_request(self, task_id) -> requests.Response:
        """Get results of complete task"""
        raise NotImplementedError()

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: Optional[List[str]] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        """Custom read_records required because of working with tasks"""
        set_task_resp: requests.Response = self._set_task_request()
        if set_task_resp.status_code != 200:
            raise ValueError  # TODO: another error

        task_id: int = set_task_resp.json()["task_id"]
        while True:
            get_task_resp: requests.Response = self._get_task_request(task_id=task_id)
            if get_task_resp.status_code != 200:
                raise ValueError  # TODO: another error
            status_json: dict[str, any] = get_task_resp.json()
            task_status: str = status_json["status"]
            tak_progress: int = status_json["progress"]  # TODO: smart wait based on progress

            if task_status == "Done":
                get_results_resp: requests.Response = self._get_results_request(task_id=task_id)
                for record in self.parse_response(response=get_results_resp):
                    yield record
                break
            else:
                time.sleep(10)


class ParserADS(ArsenkinStream):
    """Ads parser for Arsenkin"""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    # TODO: check if this is correct
    primary_key = "task_id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "set"

    def request_params(
            self, **kwargs
    ) -> MutableMapping[str, Any]:
        base_params = super().request_params(**kwargs).copy()
        base_params.update({
            "tools_name": "parser-ads",
            "keywords": json.dumps(self.config["keywords"]),
            "region_yandex": self.config["region_yandex"],
            "device": self.config["device"]
        })
        return base_params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        response_json: dict[str, any] = response.json()
        keywords: list[str] = response_json["keywords"]
        device: str = response_json["device"]

        for region, data in response_json["ads"]["YA"].items():
            for keyword_index, keyword_result in enumerate(response_json["ads"]["YA"][region]):
                for block, block_results in keyword_result.items():
                    for position, ads_data in block_results.items():
                        record: dict[str, str | int] = {
                            "device": device,
                            "region_yandex": region,
                            "keyword": keywords[keyword_index],
                            "block": block,
                            "host": ads_data["host"],
                            "position_in_block": position,
                            "title": ads_data["title"],
                            "snippet": ads_data["snippet"]
                        }
                        yield record

    @staticmethod
    def transform_config(user_config: Mapping[str, Any]) -> MutableMapping[str, Any]:
        """Pre-process config for Arsenkin ads stream"""
        config = user_config.copy()
        config["device"] = user_config["device"]["device_type"]
        return config

    def _set_task_request(self) -> requests.Response:
        """Set task to parse ads"""
        return requests.get(self.url_base + "set", params=self.request_params())

    def _get_task_request(self, task_id) -> requests.Response:
        """Get task status response"""
        return requests.get(self.url_base + "check", params={"token": self.config["token"], "task_id": task_id})

    def _get_results_request(self, task_id) -> requests.Response:
        """Get results of complete task"""
        return requests.get(self.url_base + "result", params={"token": self.config["token"], "task_id": task_id})


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
            stream_params["keywords"] = json.dumps(["Тест"])
            stream_params["device"] = "desktop"
            stream_params["region_yandex"] = 213
            test_response = requests.get(ads_stream.url_base + ads_stream.path(), params=stream_params)
            if test_response.status_code != 200:
                return False, test_response.text
            else:
                response_json = test_response.json()
                if "task_id" not in response_json:  # Task was not set successfully
                    return False, test_response.text
                else:  # Task was set successfully, connection is ok
                    return True, None
        except Exception as ex:
            return False, ex

    def streams(self, config: Mapping[str, Any]) -> List[ArsenkinStream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [ParserADS(authenticator=None, config=ParserADS.transform_config(user_config=config))]
