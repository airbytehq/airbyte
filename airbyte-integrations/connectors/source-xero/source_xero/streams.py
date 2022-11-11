#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import decimal
import re
from abc import ABC
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream


def parse_date(value):
    # Xero datetimes can be .NET JSON date strings which look like
    # "/Date(1419937200000+0000)/"
    # https://developer.xero.com/documentation/api/requests-and-responses
    pattern = r"Date\((\-?\d+)([-+])?(\d+)?\)"
    match = re.search(pattern, value)

    iso8601pattern = r"((\d{4})-([0-2]\d)-0?([0-3]\d)T([0-5]\d):([0-5]\d):([0-6]\d))"

    if not match:
        iso8601match = re.search(iso8601pattern, value)
        if iso8601match:
            try:
                return datetime.strptime(value)
            except Exception:
                return None
        else:
            return None

    millis_timestamp, offset_sign, offset = match.groups()
    if offset:
        if offset_sign == "+":
            offset_sign = 1
        else:
            offset_sign = -1
        offset_hours = offset_sign * int(offset[:2])
        offset_minutes = offset_sign * int(offset[2:])
    else:
        offset_hours = 0
        offset_minutes = 0

    return datetime.fromtimestamp((int(millis_timestamp) / 1000), tz=timezone.utc) + timedelta(hours=offset_hours, minutes=offset_minutes)


def _json_load_object_hook(_dict):
    """Hook for json.parse(...) to parse Xero date formats."""
    # This was taken from the pyxero library and modified
    # to format the dates according to RFC3339
    for key, value in _dict.items():
        if isinstance(value, str):
            value = parse_date(value)
            if value:
                if type(value) is date:
                    value = datetime.combine(value, time.min)
                value = value.replace(tzinfo=timezone.utc)
                _dict[key] = datetime.isoformat(value, timespec="seconds")
    return _dict


class XeroStream(HttpStream, ABC):
    url_base = "https://api.xero.com/api.xro/2.0/"
    page_size = 100
    current_page = 1
    pagination = False

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        records = response.json().get(self.data_field) or []
        if not self.pagination:
            return None
        if len(records) == self.page_size:
            self.current_page += 1
            return {"has_next_page": True}
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {}
        if self.pagination:
            params["page"] = self.current_page
        return params

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        headers = {"Accept": "application/json"}
        return headers

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json(object_hook=_json_load_object_hook, parse_float=decimal.Decimal).get(self.data_field) or []
        for record in records:
            record = record.get(self.data_field) or record
            if self.primary_key in record and record[self.primary_key] is None:
                record[self.primary_key] = 0
            yield record

    def path(self, **kwargs) -> str:
        class_name = self.__class__.__name__
        return f"{class_name[0].lower()}{class_name[1:]}"

    @property
    def data_field(self, **kwargs) -> str:
        class_name = self.__class__.__name__
        re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()
        return class_name


class IncrementalXeroStream(XeroStream, ABC):
    state_checkpoint_interval = 100

    def __init__(self, start_date: datetime, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date

    @property
    def cursor_field(self) -> str:
        return "UpdatedDateUTC"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        request_headers = super().request_headers(stream_state, stream_slice, next_page_token)
        stream_date = stream_state.get("date") or self.start_date
        if isinstance(stream_date, str):
            stream_date = pendulum.parse(stream_date)
        request_headers["If-Modified-Since"] = stream_date.strftime("%Y-%m-%dT%H:%M:%S")

        return request_headers

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        if current_state:
            return {"date": max(latest_state, current_state)}
        return {}


class BankTransactions(IncrementalXeroStream):
    primary_key = "BankTransactionID"
    pagination = True


class Contacts(IncrementalXeroStream):
    primary_key = "ContactID"
    pagination = True


class CreditNotes(IncrementalXeroStream):
    primary_key = "CreditNoteID"
    pagination = True


class Invoices(IncrementalXeroStream):
    primary_key = "InvoiceID"
    pagination = True


class ManualJournals(IncrementalXeroStream):
    primary_key = "ManualJournalID"
    pagination = True


class Overpayments(IncrementalXeroStream):
    primary_key = "OverpaymentID"
    pagination = True


class Prepayments(IncrementalXeroStream):
    primary_key = "PrepaymentID"
    pagination = True


class PurchaseOrders(IncrementalXeroStream):
    primary_key = "PurchaseOrderID"
    pagination = True


class Accounts(IncrementalXeroStream):
    primary_key = "AccountID"


class BankTransfers(IncrementalXeroStream):
    primary_key = "BankTransferID"
    pagination = True

    @property
    def cursor_field(self) -> str:
        return "CreatedDateUTC"


class Employees(IncrementalXeroStream):
    primary_key = "EmployeeID"
    pagination = True


class Items(IncrementalXeroStream):
    primary_key = "ItemID"


class Payments(IncrementalXeroStream):
    primary_key = "PaymentID"
    pagination = True


class Users(IncrementalXeroStream):
    primary_key = "UserID"


class BrandingThemes(XeroStream):
    primary_key = "BrandingThemeID"


class ContactGroups(XeroStream):
    primary_key = "ContactGroupID"


class Currencies(XeroStream):
    primary_key = "Code"


class Organisations(XeroStream):
    primary_key = "OrganisationID"

    def path(self, **kwargs) -> str:
        return "Organisation"


class RepeatingInvoices(XeroStream):
    primary_key = "RepeatingInvoiceID"


class TaxRates(XeroStream):
    primary_key = "Name"


class TrackingCategories(XeroStream):
    primary_key = "TrackingCategoryID"
