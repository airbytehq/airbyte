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
            connectionSpecification=BraintreeConfig.schema(), documentationUrl="https://docs.airbyte.io/integrations/sources/braintree"
        )
