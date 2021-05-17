from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests

# Chargebee
import chargebee
from chargebee.main import ChargeBee
from chargebee.environment import Environment
from chargebee.models import Subscription, Customer, Invoice
from chargebee.api_error import (
    APIError,
    PaymentError,
    InvalidRequestError,
    OperationFailedError,
)

# Airbyte
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.models import AirbyteStream, SyncMode


class ChargebeeStream(Stream):
    # No support for incremetal sync across Chargebee endpoints
    supports_incremental = True
    primary_key = "id"

    def __init__(self, limit):
        self.limit = limit
        super().__init__()    

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:

        result = self.api.list({
                "limit": self.limit,
        })
        for message in result:
            yield message._response

    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, 
        so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value 
        in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        return {
            self.cursor_field: max(
                latest_record.get(self.cursor_field), 
                current_stream_state.get(self.cursor_field, 0))
        }


class SubscriptionStream(ChargebeeStream):
    name = "Subscription"
    cursor_field = "updated_at"
    api = Subscription


class CustomerStream(ChargebeeStream):
    name = "Customer"
    cursor_field = "updated_at"
    api = Customer

class InvoiceStream(ChargebeeStream):
    name = "Invoice"
    cursor_field = "updated_at"
    api = Invoice

class SourceChargebee(AbstractSource):
    # Class variables
    LIMIT = 100

    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        # Configure the Chargebee Python SDK
        chargebee.configure(
            api_key=config['site_api_token'],
            site=config["site"],
        )
        try:
            # Get one subscription to test connection
            Subscription.list(
                # Set limit
                # to test on a small dataset
                params={
                    "limit": 1,
                },
            )
            return True, None
        except Exception as err:
            # Should catch all exceptions
            # which are already handled by
            # Chargebee Python wrapper
            # https://github.com/chargebee/chargebee-python/blob/5346d833781de78a9eedbf9d12502f52c617c2d2/chargebee/http_request.py
            logger.info(f"CHECK CONNECTION: Failed") # Debugging
            return False, str(err)

    def streams(self, config) -> List[Stream]:
        # Configure the Chargebee Python SDK
        chargebee.configure(
            api_key=config['site_api_token'],
            site=config["site"],
        )
        # Add the streams
        streams = [
            SubscriptionStream(limit=self.LIMIT),
            CustomerStream(limit=self.LIMIT),
            InvoiceStream(limit=self.LIMIT),
        ]
        return streams
