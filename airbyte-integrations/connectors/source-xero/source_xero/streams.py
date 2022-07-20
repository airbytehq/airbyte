#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import datetime
import logging
from abc import ABC
from typing import Any, Iterable, Mapping, Optional, Union, Dict
from urllib.parse import urljoin

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.exceptions import RequestBodyException


class XeroHttpStream(HttpStream, ABC):
    url_base = "http://abilling01.prod.dld"
    xero_id = ""
    BODY_REQUEST_METHODS = ("POST", "PUT", "PATCH", "GET")
    dolead_id = "ed4cac23-e9fe-4e05-89d6-b5c9fc6d2a32"
    dolead_inc_id = "c1de2758-b8aa-45d7-8c01-163c3bbf8c39"
    dolead_uk_id = "bfa6caee-df20-41f8-a42b-8b73603159d7"
    dolead_dds_id = "8cfa6be1-0d88-4046-b9d4-e5055b0ade76"

    # Set this as a noop.
    primary_key = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def retry_factor(self) -> float:
        """
        Override if needed. Specifies factor for backoff policy.
        """
        return 40

    def path(self, **kwargs) -> str:
        return ""

    def next_page_token(self, response: requests.Response, **kwargs) -> int:
        decoded_response = response.json()
        if decoded_response.get("data") != []:
            last_object_page = decoded_response.get("page")
            return int(last_object_page) + 1
        else:
            return None

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def _create_prepared_request(
            self, path: str, headers: Mapping = None, params: Mapping = None, json: Any = None, data: Any = None
    ) -> requests.PreparedRequest:
        args = {"method": self.http_method, "url": urljoin(self.url_base, path), "headers": headers, "params": params}
        if self.http_method.upper() in self.BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data

        return self._session.prepare_request(requests.Request(**args))

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        return response.json()


class XeroPaginatedData(XeroHttpStream):

    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_id, "page": str(next_page_token)}

    def parse_response(self,
                       response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("data")

    def next_page_token(self, response: requests.Response, **kwargs) -> int:
        decoded_response = response.json()
        if decoded_response.get("data") != []:
            last_object_page = decoded_response.get("page")
            return int(last_object_page) + 1
        else:
            return None


class TrackingCategories(XeroHttpStream):

    def next_page_token(self, response: requests.Response, **kwargs) -> int:
        return None

    def path(self, **kwargs) -> str:
        return "/xero/tracking_categories"


class DoleadManualJournals(XeroPaginatedData):

    def path(self, **kwargs) -> str:
        return "/xero/manualjournals"

    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_id, "page": "0"}


class DoleadIncManualJournals(DoleadManualJournals):
    dolead_id = "c1de2758-b8aa-45d7-8c01-163c3bbf8c39"


class DoleadUkManualJournals(DoleadManualJournals):
    dolead_id = "bfa6caee-df20-41f8-a42b-8b73603159d7"


class DoleadDdsManualJournals(DoleadManualJournals):
    dolead_id = "8cfa6be1-0d88-4046-b9d4-e5055b0ade76"


class Journals(XeroHttpStream):
    date_range = datetime.datetime.today() - datetime.timedelta(days=1825)
    date_range = date_range.date().isoformat()

    def path(self, **kwargs) -> str:
        return "/xero/journals"

    def parse_response(self,
                       response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("data")

    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_id, "since": next_page_token}
        else:
            return {"tenant_id": self.dolead_id, "since": self.date_range}

    def next_page_token(self, response: requests.Response, **kwargs) -> int:
        decoded_response = response.json()
        if decoded_response.get("data"):
            # Get the last "CreatedDateUTC" from the batch
            last_object_date = decoded_response.get("data")[len(decoded_response.get("data")) - 1].get("CreatedDateUTC")
            next_page_token = datetime.datetime.fromisoformat(last_object_date) + datetime.timedelta(seconds=1)
            return datetime.datetime.isoformat(next_page_token)
        else:
            return None


class DoleadJournals(Journals):
    dolead_id = "ed4cac23-e9fe-4e05-89d6-b5c9fc6d2a32"


class DoleadIncJournals(DoleadJournals):
    dolead_id = "c1de2758-b8aa-45d7-8c01-163c3bbf8c39"


class DoleadUkJournals(DoleadJournals):
    dolead_id = "bfa6caee-df20-41f8-a42b-8b73603159d7"


class DoleadDdsJournals(DoleadJournals):
    dolead_id = "8cfa6be1-0d88-4046-b9d4-e5055b0ade76"


class Contacts(XeroHttpStream):

    def next_page_token(self, response: requests.Response, **kwargs) -> int:
        return None

    def path(self, **kwargs) -> str:
        return "/xero/all_contacts"


class Accounts(XeroHttpStream):

    def next_page_token(self, response: requests.Response, **kwargs) -> int:
        return None

    def path(self, **kwargs) -> str:
        return "/xero/accounts"


class DoleadInvoices(XeroPaginatedData):
    def path(self, **kwargs) -> str:
        return "/xero/all_invoices"

    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_id, "page": "1"}


class DoleadIncInvoices(DoleadInvoices):
    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_inc_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_inc_id, "page": "1"}


class DoleadUkInvoices(DoleadInvoices):
    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_uk_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_uk_id, "page": "1"}


class DoleadDdsInvoices(DoleadInvoices):
    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_dds_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_dds_id, "page": "1"}


class DoleadCreditNotes(XeroPaginatedData):
    def path(self, **kwargs) -> str:
        return "/xero/credit_notes"

    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_id, "page": "1"}


class DoleadIncCreditNotes(DoleadCreditNotes):
    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_inc_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_inc_id, "page": "1"}


class DoleadUkCreditNotes(DoleadCreditNotes):
    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_uk_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_uk_id, "page": "1"}


class DoleadDdsCreditNotes(DoleadCreditNotes):
    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_dds_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_dds_id, "page": "1"}


class DoleadBankTransactions(XeroPaginatedData):
    def path(self, **kwargs) -> str:
        return "/xero/bank_transactions"

    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_id, "page": "1"}


class DoleadIncBankTransactions(DoleadBankTransactions):
    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_inc_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_inc_id, "page": "1"}


class DoleadUkBankTransactions(DoleadBankTransactions):
    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_uk_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_uk_id, "page": "1"}


class DoleadDdsBankTransactions(DoleadBankTransactions):
    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Dict:
        if next_page_token:
            return {"tenant_id": self.dolead_dds_id, "page": str(next_page_token)}
        else:
            return {"tenant_id": self.dolead_dds_id, "page": "1"}


class Tenants(XeroHttpStream):
    url_base = "http://acore01.prod.dld/"
    headers = {"Dolead-Current-User": "1", "Dolead-User": "1", "User-Agent": "dolead_client/billing"}

    def next_page_token(self, response: requests.Response, **kwargs) -> int:
        return None

    def path(self, **kwargs) -> str:
        return "biller/list"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return self.headers

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        return response.json()
