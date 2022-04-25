#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from .streams import Products, ProductOverviews, ProductReviews, Stores, StoreReviews, JunipReviewsStream

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream


class IncrementalJunipReviewsStream(JunipReviewsStream, ABC):
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class SourceJunipReviews(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        url = "https://api.juniphq.com/v1/product_overviews"
        headers = {
            'Junip-Store-Key': config["junip_store_key"]
        }

        try:
            response = requests.request("GET", url, headers=headers)
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
