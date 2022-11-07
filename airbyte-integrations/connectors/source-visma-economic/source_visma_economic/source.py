#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream


class VismaEconomicStream(HttpStream, ABC):
    url_base: str = "https://restapi.e-conomic.com/"
    page_size: int = 1000

    def __init__(self, app_secret_token: str = None, agreement_grant_token: str = None):
        self.app_secret_token: str = app_secret_token
        self.agreement_grant_token: str = agreement_grant_token
        super().__init__()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        if "nextPage" in response_json.get("pagination", {}).keys():
            parsed_url = urlparse(response_json["pagination"]["nextPage"])
            query_params = parse_qs(parsed_url.query)
            return query_params
        else:
            return None

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        if next_page_token:
            return dict(next_page_token)
        else:
            return {"skippages": 0, "pagesize": self.page_size}

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"X-AppSecretToken": self.app_secret_token, "X-AgreementGrantToken": self.agreement_grant_token}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("collection", [])


class Accounts(VismaEconomicStream):
    primary_key = "accountNumber"

    def path(self, **kwargs) -> str:
        return "accounts"


class Customers(VismaEconomicStream):
    primary_key = "customerNumber"

    def path(self, **kwargs) -> str:
        return "customers"


class Products(VismaEconomicStream):
    primary_key = "productNumber"

    def path(self, **kwargs) -> str:
        return "products"


class InvoicesTotal(VismaEconomicStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "invoices/totals"


class InvoicesPaid(VismaEconomicStream):
    primary_key = "bookedInvoiceNumber"

    def path(self, **kwargs) -> str:
        return "invoices/paid"


class InvoicesBooked(VismaEconomicStream):
    primary_key = "bookedInvoiceNumber"

    def path(self, **kwargs) -> str:
        return "invoices/booked"


class InvoicesBookedDocument(HttpSubStream, VismaEconomicStream):
    primary_key = "bookedInvoiceNumber"

    def __init__(self, **kwargs):
        super().__init__(InvoicesBooked(**kwargs), **kwargs)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        booked_invoice_number = stream_slice["parent"]["bookedInvoiceNumber"]
        return f"invoices/booked/{booked_invoice_number}"

    def __is_missing_booked_invoice_number(self, response: requests.Response) -> bool:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            response_json = response.json()
            if "error_code" in response_json and response_json.get("error_code") == "NO_SUCH_BOOKED_INVOICE_NUMBER":
                self.logger.info(response.text)
                return True
            else:
                self.logger.error(response.text)
                raise exc

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if not self.__is_missing_booked_invoice_number(response):
            yield response.json()


class SourceVismaEconomic(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        try:
            stream = Accounts(**config)
            stream.page_size = 1
            _ = list(stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            logger.error(e)
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        stream_list = [
            Accounts(**config),
            Customers(**config),
            InvoicesBooked(**config),
            InvoicesPaid(**config),
            InvoicesTotal(**config),
            Products(**config),
            InvoicesBookedDocument(**config),
        ]

        return stream_list
