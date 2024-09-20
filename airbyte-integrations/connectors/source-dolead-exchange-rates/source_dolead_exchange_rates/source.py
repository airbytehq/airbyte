#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


# Basic full refresh stream
class DoleadExchangeRatesStream(HttpStream, ABC):
    # Get the current date in YYYY-MM-DD format
    current_date = datetime.now().strftime("%Y-%m-%d")
    url_base = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{current_date}/v1/currencies/"
    primary_key = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_json_schema(self):
        schema = super().get_json_schema()
        schema['properties']["date"] = {"type": "string"}
        schema['properties']["input_currency"] = {"type": "string"}
        schema['properties']["output_currency"] = {"type": "string"}
        schema['properties']["rate"] = {"type": "number"}
        return schema

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, **kwargs) -> str:
        # This defines the path to the endpoint that we want to hit.
        return f"{self.output_currency}.min.json"

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"input_currency": self.output_currency}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()


class Usd(DoleadExchangeRatesStream):
    output_currency = "usd"
    input_currencies = ["eur", "gbp", "cad", "aud"]

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response = super().parse_response(response)
        record = []
        for input_currency in self.input_currencies:
            line = {}
            rate = response[self.output_currency][input_currency]
            rate = 1 / rate
            line["date"] = response["date"]
            line["input_currency"] = input_currency
            line["output_currency"] = self.output_currency
            line["rate"] = rate
            record.append(line)
        return record


class Eur(DoleadExchangeRatesStream):
    output_currency = "eur"
    input_currencies = ["usd", "gbp", "cad", "aud"]

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response = super().parse_response(response)
        record = []
        for input_currency in self.input_currencies:
            line = {}
            rate = response[self.output_currency][input_currency]
            rate = 1 / rate
            line["date"] = response["date"]
            line["input_currency"] = input_currency
            line["output_currency"] = self.output_currency
            line["rate"] = rate
            record.append(line)
        return record


# Source
class SourceDoleadExchangeRates(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Eur(), Usd()]
