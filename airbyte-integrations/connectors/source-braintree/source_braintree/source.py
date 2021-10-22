#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Optional, Tuple

import braintree
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.streams.core import Stream
from source_braintree.streams import (
    CustomerStream,
    DiscountStream,
    DisputeStream,
    MerchantAccountStream,
    PlanStream,
    SubscriptionStream,
    TransactionStream,
)


class SourceBraintree(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        # Try to initiate a stream and validate input date params
        try:
            customer_stream = CustomerStream(config)
            customer_stream._gateway.customer.all()

        except Exception as e:
            return False, e

        return True, ""

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        all_streams = [
            CustomerStream(config),
            DisputeStream(config),
            TransactionStream(config),
            MerchantAccountStream(config),
            SubscriptionStream(config),
        ]
        if not config["authorization"]["auth_type"] == "Oauth":
            # Streams are not accessible via oauth because they do not have related scope rule.
            all_streams.extend([PlanStream(config), DiscountStream(config)])
        return all_streams
