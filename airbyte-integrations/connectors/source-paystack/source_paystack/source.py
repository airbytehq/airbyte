#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping, Tuple

import requests
import pendulum
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_paystack.constants import PAYSTACK_API_BASE_URL, AUTH_KEY_FIELD
from source_paystack.streams import (
    Customers,
    Disputes,
    Invoices,
    Refunds,
    Settlements,
    Subscriptions,
    Transactions,
    Transfers
)

class SourcePaystack(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Check connection by fetching customers

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            response = requests.get(
                f"{PAYSTACK_API_BASE_URL}customer?page=1&perPage=1", 
                headers={"Authorization": f"Bearer {config[AUTH_KEY_FIELD]}"},
                verify=True
            )
            response.raise_for_status()
        except Exception as e:
            msg = e
            if (
                isinstance(e, requests.exceptions.HTTPError)
                and e.response.status_code == 401
            ):
                msg = 'Connection to Paystack was not authorized. Please check that your secret key is correct.'
            return False, msg

        response_json = response.json()
        if response_json['status'] == False:
            return False, 'Connection test failed due to error: ' + response_json['message']
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Returns list of streams output by the Paystack source connector

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        authenticator = TokenAuthenticator(config[AUTH_KEY_FIELD])
        args = {"authenticator": authenticator, "start_date": config["start_date"]}
        incremental_args = {**args, "lookback_window_days": config.get("lookback_window_days")}
        return [
            Customers(**incremental_args),
            Disputes(**incremental_args),
            Invoices(**incremental_args),
            Refunds(**incremental_args),
            Settlements(**incremental_args),
            Subscriptions(**incremental_args),
            Transactions(**incremental_args),
            Transfers(**incremental_args)
        ]

