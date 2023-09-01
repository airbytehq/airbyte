#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import pendulum
import stripe
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource

# from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger
from airbyte_cdk.sources.stream_reader.concurrent.concurrent_stream import ConcurrentStream

# from airbyte_cdk.sources.stream_reader.concurrent.concurrent_full_refresh_reader import ConcurrentFullRefreshStreamReader
# from airbyte_cdk.sources.stream_reader.concurrent.partition_generator import PartitionGenerator
# from airbyte_cdk.sources.stream_reader.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_stripe.streams import (
    Accounts,
    ApplicationFees,
    ApplicationFeesRefunds,
    Authorizations,
    BalanceTransactions,
    BankAccounts,
    Cardholders,
    Cards,
    Charges,
    CheckoutSessions,
    CheckoutSessionsLineItems,
    Coupons,
    CreditNotes,
    CustomerBalanceTransactions,
    Customers,
    Disputes,
    EarlyFraudWarnings,
    Events,
    ExternalAccountBankAccounts,
    ExternalAccountCards,
    FileLinks,
    Files,
    InvoiceItems,
    InvoiceLineItems,
    Invoices,
    PaymentIntents,
    PaymentMethods,
    Payouts,
    Persons,
    Plans,
    Prices,
    Products,
    PromotionCodes,
    Refunds,
    Reviews,
    SetupAttempts,
    SetupIntents,
    ShippingRates,
    SubscriptionItems,
    Subscriptions,
    SubscriptionSchedule,
    TopUps,
    Transactions,
    TransferReversals,
    Transfers,
    UsageRecords,
)


class SourceStripe(AbstractSource):
    # def get_full_refresh_stream_reader(self):
    #     max_workers = 10
    #     return ConcurrentFullRefreshStreamReader(PartitionGenerator, PartitionReader, max_workers, DebugSliceLogger())

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            stripe.api_key = config["client_secret"]
            stripe.Account.retrieve(config["account_id"])
            return True, None
        except Exception as e:
            return False, e

    def _get_streams(self, config: Mapping[str, Any]) -> List[AbstractStream]:
        authenticator = TokenAuthenticator(config["client_secret"])
        start_date = pendulum.parse(config["start_date"]).int_timestamp
        args = {
            "authenticator": authenticator,
            "account_id": config["account_id"],
            "start_date": start_date,
            "slice_range": config.get("slice_range"),
        }
        incremental_args = {**args, "lookback_window_days": config.get("lookback_window_days")}
        legacy_streams = [
            Accounts(**args),
            ApplicationFees(**incremental_args),
            ApplicationFeesRefunds(**args),
            Authorizations(**incremental_args),
            BalanceTransactions(**incremental_args),
            BankAccounts(**args),
            Cardholders(**incremental_args),
            Cards(**incremental_args),
            Charges(**incremental_args),
            CheckoutSessions(**args),
            CheckoutSessionsLineItems(**args),
            Coupons(**incremental_args),
            CreditNotes(**args),
            CustomerBalanceTransactions(**args),
            Customers(**incremental_args),
            Disputes(**incremental_args),
            EarlyFraudWarnings(**args),
            Events(**incremental_args),
            ExternalAccountBankAccounts(**args),
            ExternalAccountCards(**args),
            FileLinks(**incremental_args),
            Files(**incremental_args),
            InvoiceItems(**incremental_args),
            InvoiceLineItems(**args),
            Invoices(**incremental_args),
            PaymentIntents(**incremental_args),
            PaymentMethods(**args),
            Payouts(**incremental_args),
            Persons(**incremental_args),
            Plans(**incremental_args),
            Prices(**incremental_args),
            Products(**incremental_args),
            PromotionCodes(**incremental_args),
            Refunds(**incremental_args),
            Reviews(**incremental_args),
            SetupAttempts(**incremental_args),
            SetupIntents(**incremental_args),
            ShippingRates(**incremental_args),
            SubscriptionItems(**args),
            Subscriptions(**incremental_args),
            SubscriptionSchedule(**incremental_args),
            TopUps(**incremental_args),
            Transactions(**incremental_args),
            TransferReversals(**args),
            Transfers(**incremental_args),
            UsageRecords(**args),
        ]
        return [
            ConcurrentStream(
                name=stream.name,
                partition_generator=stream.get_partition_generator(),
                max_workers=10,
                slice_logger=self._slice_logger,
                json_schema=stream.get_json_schema(),
                availability_strategy=stream.availability_strategy,
            )
            for stream in legacy_streams
        ]
