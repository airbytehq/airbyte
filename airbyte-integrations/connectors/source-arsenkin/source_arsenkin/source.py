#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple, Optional

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_protocol.models import SyncMode
from source_arsenkin.tasks import ArsenkinTask, TaskStatus


class ArsenkinStream(HttpStream, ABC):
    """Base stream for Arsenkin"""
    url_base: str = "https://arsenkin.ru/tools/api/task/"
    task_done: str = "Done"

    def __init__(
            self,
            authenticator: Any = None,
            config: Optional[Mapping[str, Any]] = None,
    ):
        super().__init__(authenticator=authenticator)
        self.config = config

        self.device = self.config["device"]
        self.keywords = self.config["keywords"]
        self.region_yandex = self.config["region_yandex"]

        self.tasks: list[ArsenkinTask] = [ArsenkinTask(token=self.token, request_params=self.request_params())]

    @property
    def token(self) -> str:
        return self.config["token"]

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        raise NotImplementedError()

    def stream_slices(
            self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        self.tasks: list
        for task in self.tasks:
            task.start()
            yield {"task": task}

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: Optional[List[str]] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        """Custom read_records required because of working with tasks"""

        task = stream_slice["task"]
        task.wait_until_completed()
        for record in self.parse_response(response=task.result, stream_slice=stream_slice):
            yield record


class Ads(ArsenkinStream):
    """Ads parser for Arsenkin"""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    primary_key = None

    def path(
            self, *, stream_state: Optional[Mapping[str, Any]] = None, stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Optional[Mapping[str, Any]] = None
    ) -> str:
        return ""  # stream type for Arsenkin is a query param, not defined by path

    def request_params(
            self, **kwargs
    ) -> MutableMapping[str, Any]:
        return {
            "token": self.token,
            "tools_name": "parser-ads",
            "keywords": json.dumps(self.config["keywords"]),
            "region_yandex": self.config["region_yandex"],
            "device": self.config["device"]
        }

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
                            "region_yandex": int(region),
                            "keyword": keywords[keyword_index],
                            "block": block,
                            "host": ads_data["host"],
                            "position_in_block": int(position),
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


class SourceArsenkin(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        ads_stream: ArsenkinStream = self.streams(config)[0]
        try:
            task = ArsenkinTask(token=config["token"], request_params=ads_stream.request_params() | {
                "keywords": json.dumps(["Test"]),
                "region_yandex": 213,
                "device": "desktop",
            })
            task.start()
            return task.start != TaskStatus.FAILED, None
        except Exception as ex:
            return False, ex

    def streams(self, config: Mapping[str, Any]) -> List[ArsenkinStream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [Ads(authenticator=None, config=Ads.transform_config(user_config=config))]
