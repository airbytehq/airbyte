#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.streams.core import Stream
from source_braintree.spec import BraintreeConfig
from source_braintree.streams import (
    BraintreeStream,
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
        config = BraintreeConfig(**config)
        gateway = BraintreeStream.create_gateway(config)
        gateway.customer.all()
        return True, ""

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = BraintreeConfig(**config)
        return [
            CustomerStream(config),
            DiscountStream(config),
            DisputeStream(config),
            TransactionStream(config),
            MerchantAccountStream(config),
            PlanStream(config),
            SubscriptionStream(config),
        ]

    def spec(self, logger: AirbyteLogger) -> ConnectorSpecification:
        return ConnectorSpecification(
            connectionSpecification=BraintreeConfig.schema(), documentationUrl="https://docs.airbyte.com/integrations/sources/braintree"
        )
