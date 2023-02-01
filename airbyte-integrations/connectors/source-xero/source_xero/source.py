#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .oauth import XeroCustomConnectionsOauth2Authenticator
from .streams import (
    Accounts,
    BankTransactions,
    BankTransfers,
    BrandingThemes,
    ContactGroups,
    Contacts,
    CreditNotes,
    Currencies,
    Employees,
    Invoices,
    Items,
    ManualJournals,
    Organisations,
    Overpayments,
    Payments,
    Prepayments,
    PurchaseOrders,
    RepeatingInvoices,
    TaxRates,
    TrackingCategories,
    Users,
)


class SourceXero(AbstractSource):
    config = None

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        self.config = config
        stream_kwargs = self.get_stream_kwargs(config)

        organisations_stream = Organisations(**stream_kwargs)
        organisations_gen = organisations_stream.read_records(sync_mode=SyncMode.full_refresh)

        organisation = next(organisations_gen)

        return organisation["OrganisationID"] == config.get("tenant_id"), None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        self.config = config
        stream_kwargs = self.get_stream_kwargs(config)
        incremental_kwargs = {**stream_kwargs, "start_date": pendulum.parse(config.get("start_date"))}
        streams = [
            BankTransactions(**incremental_kwargs),
            Contacts(**incremental_kwargs),
            CreditNotes(**incremental_kwargs),
            Invoices(**incremental_kwargs),
            ManualJournals(**incremental_kwargs),
            Overpayments(**incremental_kwargs),
            Prepayments(**incremental_kwargs),
            PurchaseOrders(**incremental_kwargs),
            Accounts(**incremental_kwargs),
            BankTransfers(**incremental_kwargs),
            Employees(**incremental_kwargs),
            Items(**incremental_kwargs),
            Payments(**incremental_kwargs),
            Users(**incremental_kwargs),
            BrandingThemes(**stream_kwargs),
            ContactGroups(**stream_kwargs),
            Currencies(**stream_kwargs),
            Organisations(**stream_kwargs),
            RepeatingInvoices(**stream_kwargs),
            TaxRates(**stream_kwargs),
            TrackingCategories(**stream_kwargs),
        ]
        return streams

    @staticmethod
    def get_stream_kwargs(config: Mapping[str, Any]) -> Mapping[str, Any]:
        authentication = config.get("authentication")
        stream_kwargs = dict()
        if authentication.get("auth_type") == "custom_connection":
            stream_kwargs["authenticator"] = XeroCustomConnectionsOauth2Authenticator(
                token_refresh_endpoint="https://identity.xero.com/connect/token",
                client_secret=config.get("client_secret"),
                client_id=config.get("client_id"),
                scopes=config.get("scopes"),
            )
        elif authentication.get("auth_type") == "oauth":
            raise Exception("Config validation error. OAuth connection is not supported yet.")

        return stream_kwargs
