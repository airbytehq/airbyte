#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import copy
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_stripe_alex.streams import (
    InvoiceItems,
    InvoiceLineItems,
    Invoices,
)


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
            "stream_to_cursor_field": config["stream_to_cursor_field"]
        }
        incremental_args = {**args, "lookback_window_days": config.get("lookback_window_days")}

        return [
            InvoiceItems(**copy.deepcopy(incremental_args)),
            InvoiceLineItems(**copy.deepcopy(args)),
            Invoices(**copy.deepcopy(incremental_args))
        ]

    def _get_headers(self, config):
        return {k: v.format(**config) for k, v in config["headers"].items()}

    def _call_api(self, url_base, endpoint, headers, logger):
        url = f"{url_base}/{endpoint}"
        return requests.get(url, headers=headers)
