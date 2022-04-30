#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from .streams import Products, ProductOverviews, ProductReviews, Stores, StoreReviews, JunipReviewsStream

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream


class SourceJunipReviews(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        junip_store_key = config["junip_store_key"]
        response = requests.get("https://api.juniphq.com/v1/products", headers={"junip_store_key": junip_store_key})
        try:
            response.raise_for_status()
            connection = True, None
        except Exception as e:
            connection = False, e

        return connection

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = {
            "junip_store_key": config.get("junip_store_key")
        }

        return [
            Products(**args),
            ProductOverviews(**args),
            ProductReviews(**args),
            Stores(**args),
            StoreReviews(**args)
        ]
