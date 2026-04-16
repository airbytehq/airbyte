#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta
from typing import Any, List, Mapping, Tuple

import requests
from requests_oauthlib import OAuth1

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import (
    Accounts,
    AlertDetails,
    Alerts,
    Balances,
    Orders,
    Portfolio,
    ProductLookup,
    Quotes,
    TransactionDetails,
    Transactions,
)


logger = logging.getLogger("airbyte")


class SourceEtrade(AbstractSource):
    @staticmethod
    def _get_auth(config: Mapping[str, Any]) -> OAuth1:
        return OAuth1(
            client_key=config["consumer_key"],
            client_secret=config["consumer_secret"],
            resource_owner_key=config["oauth_token"],
            resource_owner_secret=config["oauth_token_secret"],
            signature_method="HMAC-SHA1",
        )

    @staticmethod
    def _get_base_url(config: Mapping[str, Any]) -> str:
        if config.get("sandbox", False):
            return "https://apisb.etrade.com"
        return "https://api.etrade.com"

    @staticmethod
    def _get_start_date(config: Mapping[str, Any]) -> str:
        start_date = config.get("start_date")
        if start_date:
            return start_date
        # Default to 2 years ago
        return (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        auth = self._get_auth(config)
        base_url = self._get_base_url(config)
        try:
            response = requests.get(
                url=f"{base_url}/v1/accounts/list",
                auth=auth,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return True, None
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            if status_code == 401:
                return (
                    False,
                    "Authentication failed. Access tokens may be expired (tokens expire at midnight US Eastern) or credentials are invalid.",
                )
            if status_code == 403:
                return False, "Access forbidden. The API consumer key may lack required permissions."
            return False, f"HTTP {status_code} error: {e}"
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def _get_account_id_keys(self, config: Mapping[str, Any]) -> List[str]:
        """Retrieve account ID keys either from config or by calling the accounts API."""
        configured_keys = config.get("account_id_keys", [])
        if configured_keys:
            return configured_keys

        auth = self._get_auth(config)
        base_url = self._get_base_url(config)
        response = requests.get(
            url=f"{base_url}/v1/accounts/list",
            auth=auth,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
        accounts = data.get("AccountListResponse", {}).get("Accounts", {}).get("Account", [])
        return [account["accountIdKey"] for account in accounts]

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._get_auth(config)
        base_url = self._get_base_url(config)
        start_date = self._get_start_date(config)
        account_id_keys = self._get_account_id_keys(config)

        common_kwargs = {
            "auth": auth,
            "base_url": base_url,
        }

        account_scoped_kwargs = {
            **common_kwargs,
            "account_id_keys": account_id_keys,
        }

        return [
            Accounts(**common_kwargs),
            Portfolio(**account_scoped_kwargs),
            Balances(**account_scoped_kwargs),
            Orders(start_date=start_date, **account_scoped_kwargs),
            Transactions(start_date=start_date, **account_scoped_kwargs),
            TransactionDetails(start_date=start_date, **account_scoped_kwargs),
            Quotes(**common_kwargs, account_id_keys=account_id_keys),
            ProductLookup(**common_kwargs),
            Alerts(**common_kwargs),
            AlertDetails(**common_kwargs),
        ]
