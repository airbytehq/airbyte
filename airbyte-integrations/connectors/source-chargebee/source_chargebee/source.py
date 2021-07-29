#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from typing import Any, List, Mapping, Tuple

import chargebee
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from chargebee import APIError

from .streams import AddonStream, CustomerStream, InvoiceStream, OrderStream, PlanStream, SubscriptionStream


class SourceChargebee(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        # Configure the Chargebee Python SDK
        chargebee.configure(api_key=config["site_api_key"], site=config["site"])
        try:
            subscription_stream = SubscriptionStream(start_date=config["start_date"])
            next(subscription_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as err:
            # Should catch all exceptions which are already handled by Chargebee Python wrapper.
            # https://github.com/chargebee/chargebee-python/blob/5346d833781de78a9eedbf9d12502f52c617c2d2/chargebee/http_request.py
            return False, repr(err)

    def streams(self, config) -> List[Stream]:
        # Configure the Chargebee Python SDK
        chargebee.configure(api_key=config["site_api_key"], site=config["site"])

        kwargs = {"start_date": config["start_date"]}
        product_catalog_version = 1
        try:
            plan_stream_records = PlanStream(**kwargs).read_records(sync_mode=SyncMode.full_refresh)
            next(plan_stream_records)
        except APIError as err:
            if err.http_code == requests.codes.BAD_REQUEST and err.error_code == "api_restricted":
                product_catalog_version = 2
        except StopIteration:
            # This means that user has access to `plan` stream, but there is no data.
            pass

        # Below streams are suitable for both `Product Catalog 1.0` and `Product Catalog 2.0`.
        common_streams = [
            CustomerStream(**kwargs),
            InvoiceStream(**kwargs),
            OrderStream(**kwargs),
            SubscriptionStream(**kwargs),
        ]

        if product_catalog_version == 1:
            # Below streams are suitable only for `Product Catalog 1.0`.
            product_catalog_v1_streams = [
                AddonStream(**kwargs),
                PlanStream(**kwargs),
            ]
            return common_streams + product_catalog_v1_streams

        if product_catalog_version == 2:
            # Below streams are suitable only for `Product Catalog 2.0`.
            return common_streams
