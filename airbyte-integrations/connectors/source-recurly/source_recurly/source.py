#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Optional, Tuple

import backoff
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from recurly import ApiError, Client, NetworkError

from .streams import (
    AccountCouponRedemptions,
    AccountNotes,
    Accounts,
    AddOns,
    BillingInfos,
    Coupons,
    CreditPayments,
    ExportDates,
    Invoices,
    LineItems,
    MeasuredUnits,
    Plans,
    ShippingAddresses,
    ShippingMethods,
    Subscriptions,
    Transactions,
    UniqueCoupons,
)

logger = logging.getLogger("airbyte")


class SourceRecurly(AbstractSource):
    """
    Recurly API Reference: https://developers.recurly.com/api/v2021-02-25/
    """

    def __init__(self):
        super(SourceRecurly, self).__init__()

        self.__client = None

    @backoff.on_exception(
        backoff.expo,
        NetworkError,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        max_tries=5,
        giveup=lambda e: not isinstance(e, NetworkError),
    )
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        try:
            # Checking the API key by trying a test API call to get the first account
            self._client(config["api_key"]).list_accounts().first()
            return True, None
        except NetworkError as error:
            logger.error(f"Caught retryable NetworkError: {error}")
            raise
        except ApiError as err:
            return False, err.args[0]
        except Exception as error:
            return False, error

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        client = self._client(api_key=config["api_key"])

        args = {"client": client, "begin_time": config.get("begin_time"), "end_time": config.get("end_time")}

        return [
            Accounts(**args),
            AccountCouponRedemptions(**args),
            AccountNotes(**args),
            AddOns(**args),
            BillingInfos(**args),
            Coupons(**args),
            CreditPayments(**args),
            ExportDates(**args),
            Invoices(**args),
            LineItems(**args),
            MeasuredUnits(**args),
            Plans(**args),
            ShippingAddresses(**args),
            ShippingMethods(**args),
            Subscriptions(**args),
            Transactions(**args),
            UniqueCoupons(**args),
        ]

    def _client(self, api_key: str) -> Client:
        if not self.__client:
            self.__client = Client(api_key=api_key)

        return self.__client
