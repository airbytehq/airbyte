#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_yandex_metrika.stream_preprocessor import YandexMetrikaStreamPreprocessor
from queue import Queue
from .utils import daterange_days_list, today_minus_n_days_date, yesterday_date

logger = logging.getLogger("airbyte")


class LogMessagesPoolConsumer:
    def __init__(self, log_messages_pool: Queue):
        self.log_messages_pool = log_messages_pool

    def log_info(self, message: str):
        self.log_messages_pool.put(f'({self.__class__.__name__}) - {message}')


class YandexMetrikaStream(HttpStream, ABC):

    url_base = "https://api-metrika.yandex.net/management/v1/"

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        if self.log_source == "visits":
            return "ym:s:visitID"
        if self.log_source == "hits":
            return "ym:pv:watchID"

    def __init__(
        self,
        authenticator: TokenAuthenticator,
        counter_id: int,
        date_from: str,
        date_to: str,
        last_days: int,
        split_reports: Mapping[str, Any],
        log_source: str,
        fields: List[str],
        client_name_const: str,
        product_name_const: str,
        custom_data_const={},
        clean_log_requests_before_replication: bool = False,
        clean_slice_after_successfully_loaded: bool = False,
        check_log_requests_ability: bool = False,
        multithreading_threads_count: int = 1,
        created_for_test: bool = False,
    ):
        super().__init__(authenticator=None)
        self.counter_id = counter_id
        self._authenticator = authenticator
        self.date_from = date_from
        if last_days:
            logger.info(f"last_days {last_days}")
            self.date_from = today_minus_n_days_date(last_days)
            self.date_to = yesterday_date()
            logger.info(f"{self.date_from} {self.date_to}")
        else:
            if date_from and date_to:
                self.date_from = date_from
                self.date_to = date_to
            else:
                self.date_from = yesterday_date()
                self.date_to = yesterday_date()
        self.split_reports = split_reports
        self.log_source = log_source
        self.fields = fields
        self.preprocessor = YandexMetrikaStreamPreprocessor(
            stream_instance=self)
        self.product_name_const = product_name_const
        self.client_name_const = client_name_const
        self.custom_data_const = custom_data_const
        self.multithreading_threads_count = multithreading_threads_count
        self.clean_slice_after_successfully_loaded = clean_slice_after_successfully_loaded
        self.clean_log_requests_before_replication = clean_log_requests_before_replication
        self.check_log_requests_ability = check_log_requests_ability
        self.created_for_test = created_for_test

        if self.clean_log_requests_before_replication and not self.created_for_test:
            logger.info('Clean all log requests before replication...')
            self.preprocessor.clean_all_log_requests()

        if self.check_log_requests_ability:
            can_replicate, message = self.preprocessor.check_stream_slices_ability()
            if not can_replicate:
                raise Exception(message)

    def add_constants_to_record(self, record):
        constants = {
            "__productName": self.product_name_const,
            "__clientName": self.client_name_const,
        }
        constants.update(self.custom_data_const)
        record.update(constants)
        return record

    def get_json_schema(self):
        schema = super().get_json_schema()
        properties = self.fields + ["__productName", "__clientName"]
        custom_keys = self.custom_data_const.keys()
        properties.extend(custom_keys)
        for key in properties:
            schema["properties"][key] = {"type": ["null", "string"]}

        return schema

    def path(self, next_page_token: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> str:
        path = f"counter/{self.counter_id}/logrequest/{stream_slice['log_request_id']}/part/{stream_slice['part']['part_number']}/download"
        logger.info(f"Path: {path}")
        return path

    def next_page_token(self, *args, **kwargs) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> MutableMapping[str, Any]:
        return {
            "date1": stream_slice["date_from"],
            "date2": stream_slice["date_to"],
            "fields": ",".join(self.fields),
            "source": self.log_source,
        }

    def request_headers(self, stream_state=None, *args, **kwargs) -> Mapping[str, Any]:
        headers = super().request_headers(stream_state, *args, **kwargs)
        headers.update({"Content-Type": "application/x-yametrika+json"})
        return headers

    def should_retry(self, response: requests.Response) -> bool:
        return response.status_code in [429, 400] or 500 <= response.status_code < 600

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        logger.info(f"parse_response {response.url}")
        raw_data_lines = response.content.split(b"\n")
        del response

        for line_n, line in enumerate(raw_data_lines):
            if not line.strip():
                continue
            if line_n == 0:
                continue

            # zip values list to named dict
            zipped_object = dict(zip(self.fields, line.decode().split("\t")))
            yield self.add_constants_to_record(zipped_object)
        logger.info(f"end of parse_response")

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        if self.split_reports["split_mode_type"] == "do_not_split_mode":
            slices = [{"date_from": self.date_from, "date_to": self.date_to}]
        elif self.split_reports["split_mode_type"] == "split_date_mode":
            slices = daterange_days_list(
                self.date_from, self.date_to, self.split_reports["split_range_days_count"])
        else:
            pass
        return slices
