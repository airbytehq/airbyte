#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import copy
from abc import abstractmethod
from typing import Any, Iterable, Mapping
from typing import List, Tuple

import pendulum
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_stripe_alex.streams import (
    InvoiceLineItems,
    meta_incremental
)


class ResponseParser:
    @abstractmethod
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        pass


class JsonArrayGetter:
    def __init__(self, **kwargs):
        self._field_to_get = kwargs["field_to_get"]

    @abstractmethod
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get(self._field_to_get, [])


class SourceStripeAlex(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        headers = self._get_headers(config)
        res = self._call_api(config["url_base"], config["check_endpoint"], headers, logger)
        connected = res.ok
        return connected, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(config["client_secret"])
        start_date = pendulum.parse(config["start_date"]).int_timestamp
        args = {
            "url_base": config["url_base"],
            "authenticator": authenticator,
            "account_id": config["account_id"],
            "start_date": start_date,
            "headers": self._get_headers(config),
            "request_parameters": config["request_parameters"],
            "stream_to_cursor_field": config["stream_to_cursor_field"],
            "stream_to_path": config["stream_to_path"],
            "response_parser": self._get_response_parser(config)
        }
        incremental_args = {**args, "lookback_window_days": config.get("lookback_window_days")}

        invoices_args = {
            **copy.deepcopy(incremental_args),
            **{"name": "invoices"}
        }
        invoice_items_args = {
            **copy.deepcopy(incremental_args),
            **{"name": "invoice_items"}
        }
        invoice_line_items_args = {
            **copy.deepcopy(args),
            **{"name": "invoice_line_items"}
        }

        return [
            meta_incremental("InvoiceItems")(**invoice_items_args),
            InvoiceLineItems(**invoice_line_items_args),
            meta_incremental("Invoices")(**invoices_args)
        ]

    def _get_response_parser(self, config):
        response_parser_config = config["response_parser"]
        parser_type = response_parser_config["type"]
        if parser_type == "JsonArrayGetter":
            return JsonArrayGetter(**response_parser_config["config"])
        else:
            raise Exception(f"unexpected response parser type: {parser_type}")

    def _get_headers(self, config):
        return {k: v.format(**config) for k, v in config["headers"].items()}

    def _call_api(self, url_base, endpoint, headers, logger):
        url = f"{url_base}/{endpoint}"
        return requests.get(url, headers=headers)
