#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import copy
from abc import abstractmethod
from typing import Any, Iterable, Mapping, Optional
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


class JsonArrayGetter(ResponseParser):
    def __init__(self, **kwargs):
        self._field_to_get = kwargs["field_to_get"]

    @abstractmethod
    def parse_response(self, response_json, **kwargs) -> Iterable[Mapping]:
        yield from response_json.get(self._field_to_get, [])


class Paginator:
    @abstractmethod
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class PaginatorCursorInHeaderLastObject(Paginator):
    """
    This is probably 2 classes:
    1. track last object id
    2. update the header
    """

    def __init__(self, response_parser, has_more_flag, extra_header):
        self._response_parser = response_parser
        self._has_more_flag = has_more_flag
        self._extra_header = extra_header

    def next_page_token(self, response_json) -> Optional[Mapping[str, Any]]:
        data = [o for o in self._response_parser.parse_response(response_json)]
        if bool(response_json.get(self._has_more_flag, "False")) and data:
            last_object = AttrDict(**data[-1])
            return None
            # FIXME: disabled because this is painfully slow...
            # return {k: v.format(last_object=last_object) for k, v in self._extra_header.items()}
        else:
            return None


class SourceStripeAlex(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        headers = self._get_headers(config)
        res = self._call_api(config["url_base"], config["check_endpoint"], headers, logger)
        connected = res.ok
        return connected, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(config["client_secret"])
        start_date = pendulum.parse(config["start_date"]).int_timestamp
        response_parser = self._get_response_parser(config)
        paginator_config = copy.deepcopy(config)
        paginator_config.update(**{"response_parser": response_parser})
        args = {
            "url_base": config["url_base"],
            "authenticator": authenticator,
            "account_id": config["account_id"],
            "start_date": start_date,
            "headers": self._get_headers(config),
            "request_parameters": config["request_parameters"],
            "stream_to_cursor_field": config["stream_to_cursor_field"],
            "stream_to_path": config["stream_to_path"],
            "response_parser": response_parser,
            "paginator": self._get_paginator(**paginator_config),
            "primary_key": config["primary_key"],
            "incremental_headers": config.get("incremental_headers")  # this needs to be in args because read_records calls parent stream...
        }
        incremental_args = {
            **args,
            "lookback_window_days": config.get("lookback_window_days"),
        }

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

    def _get_paginator(self, **config):
        paginator_config = config["paginator"]
        paginator_type = paginator_config["type"]
        if paginator_type == "PaginatorCursorInHeaderLastObject":
            return PaginatorCursorInHeaderLastObject(config["response_parser"],
                                                     paginator_config["config"]["has_more_flag"],
                                                     paginator_config["config"]["extra_header"])
        else:
            raise Exception(f"unexpected paginator type: {paginator_type}")

    def _get_headers(self, config):
        return {k: v.format(**config) for k, v in config["headers"].items()}

    def _call_api(self, url_base, endpoint, headers, logger):
        url = f"{url_base}/{endpoint}"
        return requests.get(url, headers=headers)
