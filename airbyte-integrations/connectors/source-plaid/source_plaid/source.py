#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pathlib
from abc import abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .plaid_requester import PlaidRequester

CATALOG_PATH = pathlib.Path(__file__).parent / "catalog.json"
CURSOR_FIELD = "date"


class SourcePlaid(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        try:
            api_requester = PlaidRequester.from_config(**config)
            api_requester.test_connection()
            return True, None
        except Exception as error:
            return False, error

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        plaid_requester = PlaidRequester.from_config(**config)
        return [BalanceStream(plaid_requester), IncrementalTransactionStream(plaid_requester)]


class PlaidStream(Stream):
    def __init__(self, plaid_requester: PlaidRequester):
        self.plaid_requester = plaid_requester

    @property
    def source_defined_cursor(self) -> bool:
        """
        Return False if the cursor can be configured by the user.
        """
        return True

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if sync_mode == SyncMode.incremental:
            yield from self.stream_generator_function(**stream_state)
        else:
            yield from self.stream_generator_function()

    @abstractmethod
    def stream_generator_function(self, **kwargs):
        pass


class BalanceStream(PlaidStream):
    def stream_generator_function(self, **_kwargs):
        yield from self.plaid_requester.balance_generator()

    @property
    def name(self):
        return "balance"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "required": ["account_id", "current"],
            "properties": {
                "account_id": {"type": "string"},
                "available": {"type": ["number", "null"]},
                "current": {"type": "number"},
                "iso_currency_code": {"type": ["string", "null"]},
                "limit": {"type": ["number", "null"]},
                "unofficial_currency_code": {"type": ["string", "null"]},
            },
        }

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "account_id"

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return []


class IncrementalTransactionStream(PlaidStream):
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "transaction_id"

    @property
    def name(self):
        return "transaction"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        return {CURSOR_FIELD: latest_record[CURSOR_FIELD]}

    def stream_generator_function(self, **kwargs):
        try:
            yield from self.plaid_requester.transaction_generator(**kwargs)
        except ValueError:
            pass

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "required": ["account_id", "amount", "iso_currency_code", "name", "transaction_id", "category", "date", "transaction_type"],
            "properties": {
                "account_id": {"type": "string"},
                "amount": {"type": "number"},
                "category": {"type": "array", "items": {"type": "string"}},
                "category_id": {"type": ["string", "null"]},
                "date": {"type": "string"},
                "iso_currency_code": {"type": "string"},
                "name": {"type": "string"},
                "payment_channel": {"type": ["string", "null"]},
                "pending": {"type": ["boolean", "null"]},
                "transaction_id": {"type": "string"},
                "transaction_type": {"type": "string"},
                "location": {
                    "type": ["object", "null"],
                    "properties": {
                        "address": {"type": ["string", "null"]},
                        "city": {"type": ["string", "null"]},
                        "country": {"type": ["string", "null"]},
                        "lat": {"type": ["string", "null"]},
                        "lon": {"type": ["string", "null"]},
                        "postal_code": {"type": ["string", "null"]},
                        "region": {"type": ["string", "null"]},
                        "store_number": {"type": ["string", "null"]},
                    },
                },
                "payment_meta": {
                    "type": ["object", "null"],
                    "properties": {
                        "by_order_of": {"type": ["string", "null"]},
                        "payee": {"type": ["string", "null"]},
                        "payer": {"type": ["string", "null"]},
                        "payment_method": {"type": ["string", "null"]},
                        "payment_processor": {"type": ["string", "null"]},
                        "ppd_id": {"type": ["string", "null"]},
                        "reason": {"type": ["string", "null"]},
                        "reference_number": {"type": ["string", "null"]},
                    },
                },
                "account_owner": {"type": ["string", "null"]},
                "authorized_date": {"type": ["string", "null"]},
                "authorized_datetime": {"type": ["string", "null"]},
                "check_number": {"type": ["string", "null"]},
                "datetime": {"type": ["string", "null"]},
                "merchant_name": {"type": ["string", "null"]},
                "pending_transaction_id": {"type": ["string", "null"]},
                "personal_finance_category": {"type": ["string", "null"]},
                "transaction_code": {"type": ["string", "null"]},
                "unofficial_currency_code": {"type": ["string", "null"]},
            },
        }

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return CURSOR_FIELD
