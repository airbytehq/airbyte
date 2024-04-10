#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .oauth import XeroSingleUseRefreshTokenOauth2Authenticator
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
    def _validate_and_transform(self, config: Mapping[str, Any]):
        pendulum.parse(config["start_date"])
        return config

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            config = self._validate_and_transform(config)
            stream = Organisations(authenticator=self.get_authenticator(config), tenant_id=config["tenant_id"])
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            record = next(records)
            return record["OrganisationID"] == config["tenant_id"], None
        except requests.exceptions.HTTPError as e:
            error_message = str(e)
            if e.response.status_code == 403:
                error_message = (
                    "For oauth2 authentication try to re-authenticate and allow all requested scopes, for token authentication please update "
                    "access token with all required scopes mentioned in prerequisites. Full error message: " + error_message
                )
            return False, error_message
        except Exception as e:
            return False, str(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        stream_kwargs = {
            "authenticator": self.get_authenticator(config),
            "tenant_id": config["tenant_id"],
        }
        incremental_kwargs = {**stream_kwargs, "start_date": pendulum.parse(config["start_date"])}
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
    def get_authenticator(config: Mapping[str, Any]) -> Mapping[str, Any]:
        return XeroSingleUseRefreshTokenOauth2Authenticator(
            connector_config=config,
            token_refresh_endpoint="https://identity.xero.com/connect/token",
            client_id=config["authentication"]["client_id"],
            client_secret=config["authentication"]["client_secret"],
            access_token_config_path=["authentication", "access_token"],
            refresh_token_config_path=["authentication", "refresh_token"],
            token_expiry_date_config_path=["authentication", "token_expiry_date"],
        )
