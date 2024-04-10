#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import logging
import os
from abc import ABC
from datetime import datetime
from queue import Queue
from typing import Iterable, Mapping, MutableMapping

import requests
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader

from .stream_preprocessor import YandexMetrikaStreamPreprocessor
from ..base_stream import YandexMetrikaStream
from ..utils import (
    daterange_days_list,
    random_output_filename,
)

logger = logging.getLogger("airbyte")


class LogMessagesPoolConsumer:
    def __init__(self, log_messages_pool: Queue):
        self.log_messages_pool = log_messages_pool

    def log_info(self, message: str):
        self.log_messages_pool.put(f"({self.__class__.__name__}) - {message}")


class YandexMetrikaRawDataStream(YandexMetrikaStream, ABC):
    url_base = "https://api-metrika.yandex.net/management/v1/"

    @property
    def primary_key(self) -> str | list[str] | list[list[str]]:
        if self.log_source == "visits":
            return "ym:s:visitID"
        if self.log_source == "hits":
            return "ym:pv:watchID"

    @property
    def name(self) -> str:
        return "raw_data_" + self.log_source

    def __init__(
        self,
        authenticator: TokenAuthenticator,
        counter_id: int,
        date_from: str,
        date_to: str,
        split_range_days_count: Mapping[str, any],
        log_source: str,
        fields: list[str],
        clean_log_requests_before_replication: bool = False,
        clean_slice_after_successfully_loaded: bool = False,
        check_log_requests_ability: bool = False,
        multithreading_threads_count: int = 1,
        created_for_test: bool = False,
        key_map: dict[str, any] | None = None,
    ):
        super().__init__(key_map)
        self.counter_id = counter_id
        self._authenticator = authenticator
        self.date_from = date_from
        self.date_to = date_to
        self.split_range_days_count = split_range_days_count
        self.log_source = log_source
        self.fields = fields
        self.preprocessor = YandexMetrikaStreamPreprocessor(stream_instance=self)
        self.multithreading_threads_count = multithreading_threads_count
        self.clean_slice_after_successfully_loaded = clean_slice_after_successfully_loaded
        self.clean_log_requests_before_replication = clean_log_requests_before_replication
        self.check_log_requests_ability = check_log_requests_ability
        self.created_for_test = created_for_test

        if self.clean_log_requests_before_replication and not self.created_for_test:
            logger.info("Clean all log requests before replication...")
            self.preprocessor.clean_all_log_requests()

        if self.check_log_requests_ability:
            can_replicate, message = self.preprocessor.check_stream_slices_ability()
            if not can_replicate:
                raise Exception(message)

    def get_json_schema(self) -> Mapping[str, any]:
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("yandex_metrika_raw_data_stream")
        for key in self.fields:
            schema["properties"][key] = {"type": ["null", "string"]}

        super().replace_keys(schema["properties"])

        return schema

    def path(
        self,
        next_page_token: Mapping[str, any] = None,
        stream_slice: Mapping[str, any] = None,
        *args,
        **kwargs,
    ) -> str:
        path = f"counter/{self.counter_id}/logrequest/{stream_slice['log_request_id']}/part/{stream_slice['part']['part_number']}/download"
        logger.info(f"Path: {path}")
        return path

    def next_page_token(self, *args, **kwargs) -> Mapping[str, any] | None:
        return None

    def request_params(self, stream_slice: Mapping[str, any] = None, *args, **kwargs) -> MutableMapping[str, any]:
        return {
            "date1": datetime.strftime(stream_slice["date_from"], "%Y-%m-%d"),
            "date2": datetime.strftime(stream_slice["date_to"], "%Y-%m-%d"),
            "fields": ",".join(self.fields),
            "source": self.log_source,
        }

    def request_headers(self, stream_state=None, *args, **kwargs) -> Mapping[str, any]:
        headers = super().request_headers(stream_state, *args, **kwargs)
        headers.update({"Content-Type": "application/x-yametrika+json"})
        return headers

    def should_retry(self, response: requests.Response) -> bool:
        return response.status_code in [429, 400] or 500 <= response.status_code < 600

    def parse_response(
        self,
        response: requests.Response,
        stream_slice: Mapping[str, str],
        *args,
        **kwargs,
    ) -> str:
        logger.info(f"parse_response {response.url}")
        try:
            os.mkdir("output")
        except FileExistsError:
            pass
        filename = random_output_filename()
        logger.info(f"Save slice {stream_slice} data to {filename}")
        with open(filename, "wb") as f:
            f.write(response.content)
        logger.info(f"end of parse_response")
        return [filename]

    def should_retry(self, response: requests.Response) -> bool:
        return super().should_retry(response)

    def stream_slices(self, *args, **kwargs) -> Iterable[Mapping[str, any] | None]:
        if not self.split_range_days_count:
            slices = [{"date_from": self.date_from, "date_to": self.date_to}]
        elif self.split_range_days_count:
            slices = daterange_days_list(self.date_from, self.date_to, self.split_range_days_count)
        else:
            pass
        return slices
