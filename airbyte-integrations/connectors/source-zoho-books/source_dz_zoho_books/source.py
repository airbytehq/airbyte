#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime
from types import MappingProxyType
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.core import StreamData
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from source_dz_zoho_books.auth import ZohoBooksAuthenticator
from source_dz_zoho_books.datetimeutil import convert_to_utc
from .api import ZohoBooksAPI


# Basic full refresh stream
class DzZohoBooksStream(HttpStream, ABC):
    def __init__(self, start_date: datetime, base_url, **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date
        self.base_url = base_url

    @property
    def url_base(self) -> str:
        return self.base_url

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.json().get("page_context")
        if (next_page is None) or (not next_page["has_more_page"]):
            return None
        else:
            return {
                "page": next_page["page"] + 1, 
                "per_page": next_page["per_page"]
            }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token is None:
            return {}
        else:
            return {
                "page": next_page_token["page"],
                "per_page": next_page_token["per_page"],
            }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        data = response.json().get(self.name)
        if isinstance(data, list):
            for record in data:
                date = convert_to_utc(record["last_modified_time"])
                if date >= self._start_date:
                    yield self.transform(record=record, **kwargs)
        else:
            date = convert_to_utc(data["last_modified_time"])
            if date >= self._start_date:
                yield self.transform(record=data, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return record


class IncrementalDzZohoBooksStream(DzZohoBooksStream, IncrementalMixin):
    cursor_field = "last_modified_time"

    def __init__(self, start_date: datetime, **kwargs):
        super().__init__(start_date, **kwargs)
        self.start_date = start_date
        self._cursor_value: datetime = None

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return  {self.cursor_field: self._cursor_value}
        else :
            return  {self.cursor_field: self.start_date}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(str(value[self.cursor_field]), '%Y-%m-%dT%H:%M:%S')

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[StreamData]:
        records =  list(super().read_records(sync_mode, cursor_field, stream_slice, stream_state))

        latest_cursor_value : datetime = None
        if not self._cursor_value:
            for record in records:
                current_record_cursor_value = convert_to_utc(record[self.cursor_field])
                latest_cursor_value = max(current_record_cursor_value, latest_cursor_value) if latest_cursor_value else current_record_cursor_value
                yield record
        else:
            for record in records:
                current_record_cursor_value = convert_to_utc(record[self.cursor_field])
                if current_record_cursor_value > self._cursor_value:
                    latest_cursor_value = max(current_record_cursor_value, latest_cursor_value) if latest_cursor_value else current_record_cursor_value
                    yield record
                else:
                    break

        if latest_cursor_value:
            self._cursor_value = latest_cursor_value
            yield from []
        else:
            yield from []

class Contacts(IncrementalDzZohoBooksStream):
    primary_key = "contact_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/contacts?sort_column={self.cursor_field}&sort_order=D"


class Estimates(IncrementalDzZohoBooksStream):
    primary_key = "estimate_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/estimates?sort_column={self.cursor_field}&sort_order=D"


class Salesorders(IncrementalDzZohoBooksStream):
    primary_key = "salesorder_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/salesorders?sort_column={self.cursor_field}&sort_order=D"


class Invoices(IncrementalDzZohoBooksStream):
    primary_key = "invoice_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/invoices?sort_column={self.cursor_field}&sort_order=D"


class RecurringInvoices(IncrementalDzZohoBooksStream):
    primary_key = "recurring_invoice_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/recurringinvoices?sort_column={self.cursor_field}&sort_order=D"


class Creditnotes(IncrementalDzZohoBooksStream):
    primary_key = "creditnote_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/creditnotes?sort_column={self.cursor_field}&sort_order=D"


class Customerpayments(IncrementalDzZohoBooksStream):
    primary_key = "payment_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/customerpayments?sort_column={self.cursor_field}&sort_order=D"


class Expenses(DzZohoBooksStream):
    primary_key = "expense_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v3/expenses"


class RecurringExpenses(DzZohoBooksStream):
    primary_key = "recurring_expense_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v3/recurringexpenses"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        data = response.json().get(self.name)
        if isinstance(data, list):
            for record in data:
                date = convert_to_utc(record["last_modified_time"]) if record["last_modified_time"] != "" else convert_to_utc(record["created_time"])
                if date >= self._start_date:
                    yield self.transform(record=record, **kwargs)
        else:
            date = convert_to_utc(data["last_modified_time"]) if data["last_modified_time"] != "" else convert_to_utc(data["created_time"])
            if date >= self._start_date:
                yield self.transform(record=data, **kwargs)


class Purchaseorders(IncrementalDzZohoBooksStream):
    primary_key = "purchaseorder_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/purchaseorders?sort_column={self.cursor_field}&sort_order=D"


class Bills(IncrementalDzZohoBooksStream):
    primary_key = "bill_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/bills?sort_column={self.cursor_field}&sort_order=D"


class RecurringBills(DzZohoBooksStream):
    primary_key = "recurring_bill_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v3/recurringbills"


class VendorCredits(IncrementalDzZohoBooksStream):
    primary_key = "vendor_credit_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/vendorcredits?sort_column={self.cursor_field}&sort_order=D"


class Vendorpayments(IncrementalDzZohoBooksStream):
    primary_key = "payment_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/vendorpayments?sort_column={self.cursor_field}&sort_order=D"


class Bankaccounts(DzZohoBooksStream):
    primary_key = "account_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v3/bankaccounts"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        data = response.json().get(self.name)
        if isinstance(data, list):
            for record in data:
                yield super().transform(record=record, **kwargs)
        else:
            yield super().transform(record=data, **kwargs)


class Banktransactions(DzZohoBooksStream):
    primary_key = "transaction_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v3/banktransactions"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        data = response.json().get(self.name)
        if isinstance(data, list):
            for record in data:
                date = convert_to_utc(record["date"])
                if date >= self._start_date:
                    yield super().transform(record=record, **kwargs)
        else:
            date = convert_to_utc(data["date"])
            if date >= self._start_date:
                yield super().transform(record=data, **kwargs)


class Chartofaccounts(DzZohoBooksStream):
    primary_key = "account_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v3/chartofaccounts"


class Journals(DzZohoBooksStream):
    primary_key = "journal_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v3/journals"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        data = response.json().get(self.name)
        if isinstance(data, list):
            for record in data:
                date = convert_to_utc(record["journal_date"])
                if date >= self._start_date:
                    yield super().transform(record=record, **kwargs)
        else:
            date = convert_to_utc(data["journal_date"])
            if date >= self._start_date:
                yield super().transform(record=data, **kwargs)


class Projects(IncrementalDzZohoBooksStream):
    primary_key = "Project_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/projects?sort_column={self.cursor_field}&sort_order=D"


class TimeEntries(DzZohoBooksStream):
    primary_key = "time_entry_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v3/projects/timeentries"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        data = response.json().get(self.name)
        if isinstance(data, list):
            for record in data:
                date = convert_to_utc(record["created_time"])
                if date >= self._start_date:
                    yield self.transform(record=record, **kwargs)
        else:
            date = convert_to_utc(data["created_time"])
            if date >= self._start_date:
                yield self.transform(record=data, **kwargs)


class Items(IncrementalDzZohoBooksStream):
    primary_key = "item_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"v3/items?sort_column={self.cursor_field}&sort_order=D"


class Users(DzZohoBooksStream):
    primary_key = "user_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v3/users"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        data = response.json().get(self.name)
        if isinstance(data, list):
            for record in data:
                yield super().transform(record=record, **kwargs)
        else:
            yield super().transform(record=data, **kwargs)


class Currencies(DzZohoBooksStream):
    primary_key = "currency_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v3/settings/currencies"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        data = response.json().get(self.name)
        if isinstance(data, list):
            for record in data:
                yield super().transform(record=record, **kwargs)
        else:
            yield super().transform(record=data, **kwargs)


# Source
class SourceDzZohoBooks(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        api = ZohoBooksAPI(config)
        return api.check_connection()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        auth = ZohoBooksAuthenticator(
            token_refresh_endpoint="https://accounts.zoho.in/oauth/v2/token",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"]
        )

        start_date = convert_to_utc(config["start_date"])
        
        _DC_REGION_TO_API_URL = MappingProxyType(
            {
                "US": "https://www.zohoapis.com/books/",
                "AU": "https://www.zohoapis.com.au/books/",
                "EU": "https://www.zohoapis.eu/books/",
                "IN": "https://www.zohoapis.in/books/",
                "JP": "https://www.zohoapis.jp/books/"
            }
        )
        init_params = {
            "authenticator": auth,
            "start_date": start_date,
            "base_url": _DC_REGION_TO_API_URL[config['dc_region'].upper()]
        }

        return [
            Contacts(**init_params),
            Estimates(**init_params),
            Salesorders(**init_params),
            Invoices(**init_params),
            RecurringInvoices(**init_params),
            Creditnotes(**init_params),
            Customerpayments(**init_params),
            Expenses(**init_params),
            RecurringExpenses(**init_params),
            Purchaseorders(**init_params),
            Bills(**init_params),
            RecurringBills(**init_params),
            VendorCredits(**init_params),
            Vendorpayments(**init_params),
            Bankaccounts(**init_params),
            Banktransactions(**init_params),
            Chartofaccounts(**init_params),
            Journals(**init_params),
            Projects(**init_params),
            TimeEntries(**init_params),
            Items(**init_params),
            Users(**init_params),
            Currencies(**init_params),
        ]
