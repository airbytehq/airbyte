#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_stripe_alex.streams import Invoices

logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""


# Source
class SourceStripeAlex(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            logger.info(f"config: {config}")
            headers = self._get_headers(config)

            res = self._call_api(config["url_base"], config["check_endpoint"], headers, logger)
            connected = res.ok
            return connected, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        url_base = config["url_base"]
        primary_key = config["primary_key"]
        retry_factor = config["retry_factor"]
        max_retries = config["max_retries"]
        headers = self._get_headers(config)
        response_key = config["response_key"]
        request_parameters = config["request_parameters"]
        start_date = pendulum.parse(config["start_date"]).int_timestamp
        cursor_field = config["cursor_field"]
        return [
            Invoices(
                url_base=url_base,
                primary_key=primary_key,
                retry_factor=retry_factor,
                max_retries=max_retries,
                headers=headers,
                response_key=response_key,
                request_parameters=request_parameters,
                start_date=start_date,
                cursor_field=cursor_field,
                authenticator=NoAuth()
            )
        ]

    def _get_headers(self, config):
        return {k: v.format(**config) for k, v in config["headers"].items()}

    def _call_api(self, url_base, endpoint, headers, logger):
        url = f"{url_base}{endpoint}"
        return requests.get(url, headers=headers)
