#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import chargebee
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import (
    Addon,
    AttachedItem,
    Coupon,
    CreditNote,
    Customer,
    Event,
    Invoice,
    Item,
    ItemPrice,
    Order,
    Plan,
    Subscription,
    Transaction,
)


class SourceChargebee(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        # Configure the Chargebee Python SDK
        chargebee.configure(api_key=config["site_api_key"], site=config["site"])
        try:
            subscription_stream = Subscription(start_date=config["start_date"])
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
        product_catalog_version = config["product_catalog"]

        # Below streams are suitable for both `Product Catalog 1.0` and `Product Catalog 2.0`.
        common_streams = [
            Coupon(**kwargs),
            CreditNote(**kwargs),
            Customer(**kwargs),
            Event(**kwargs),
            Invoice(**kwargs),
            Order(**kwargs),
            Subscription(**kwargs),
            Transaction(**kwargs),
        ]

        if product_catalog_version == "1.0":
            # Below streams are suitable only for `Product Catalog 1.0`.
            product_catalog_v1_streams = [
                Addon(**kwargs),
                Plan(**kwargs),
            ]
            return common_streams + product_catalog_v1_streams

        # Below streams are suitable only for `Product Catalog 2.0`.
        product_catalog_v2_streams = [
            Item(**kwargs),
            ItemPrice(**kwargs),
            AttachedItem(**kwargs),
        ]
        return common_streams + product_catalog_v2_streams
