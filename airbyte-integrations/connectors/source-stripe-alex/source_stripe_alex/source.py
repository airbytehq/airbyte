#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_stripe_alex.streams import Invoices
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
        headers = {k: v.format(**config) for k,v in config["headers"].items()}
        res = self._call_api(config["url_base"], config["check_endpoint"], headers, logger)
        connected = res.ok
        return connected, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        print(f"config: {config}")
        url_base = config["url_base"]
        primary_key = config["primary_key"]
        return [Invoices(url_base=url_base, primary_key=primary_key)]

    def _call_api(self, base_url, endpoint, headers, logger):
        url = f"https://{base_url}/{endpoint}"
        return requests.get(url, headers=headers)
