#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_paystack.streams import Customers, Disputes, Invoices, Refunds, Settlements, Subscriptions, Transactions, Transfers


class SourcePaystack(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Check connection by fetching customers

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            authenticator = TokenAuthenticator(token=config["secret_key"])
            stream = Customers(authenticator=authenticator, start_date=config["start_date"])
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None

        except StopIteration:
            # there are no records, but connection was fine
            return True, None

        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Returns list of streams output by the Paystack source connector

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        authenticator = TokenAuthenticator(config["secret_key"])
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
            Transfers(**incremental_args),
        ]
