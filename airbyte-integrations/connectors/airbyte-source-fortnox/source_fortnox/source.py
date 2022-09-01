#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Iterator

import requests
from airbyte_cdk.models import ConfiguredAirbyteCatalog, AirbyteMessage
from airbyte_cdk.models import Type
from airbyte_cdk.models.airbyte_protocol import SyncMode, AirbyteStateMessage
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream

from source_fortnox.auth.RemoteTokenAuthenticator import RemoteTokenAuthenticator
from source_fortnox.schema_applier import SchemaApplier
from requests.auth import AuthBase


class FortnoxStream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class FortnoxStream(HttpStream, ABC)` which is the current class
    `class Customers(FortnoxStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(FortnoxStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalFortnoxStream((FortnoxStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://api.fortnox.se/3/"

    def __init__(self, authenticator: AuthBase, ark_salt: str = "", is_dev_env=False, *args, **kwargs):
        super().__init__(authenticator=authenticator)
        self.schema_applier = SchemaApplier(ark_salt.encode())
        self.is_dev_env = is_dev_env

        # According to https://developer.fortnox.se/general/parameters/ limit 500 is max
        self.default_params = {"limit": 500 if not is_dev_env else 10}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.is_dev_env:
            return None

        response_json = response.json()
        if "MetaInformation" in response_json:
            meta_information = response_json["MetaInformation"]
            total_pages = meta_information["@TotalPages"]
            current_page = meta_information["@CurrentPage"]
            return {"page": current_page + 1} if current_page < total_pages else None
        else:
            return None

    def request_params(self, *, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        if next_page_token:
            return {"page": next_page_token["page"], **self.default_params} if "page" in next_page_token else self.default_params
        else:
            return self.default_params


class IncrementalFortnoxStream(FortnoxStream, IncrementalMixin, ABC):
    cursor_field = "lastmodified"

    def __init__(self, *, authenticator, **kwargs):
        super().__init__(authenticator=authenticator, **kwargs)
        self._state = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value


class Accounts(FortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/accounts/
    """
    primary_key = "Number"

    def path(self, **kwargs) -> str:
        return "accounts"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("Accounts", {})


class CompanyInformation(FortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/company-information/
    """
    primary_key = "OrganizationNumber"

    def path(self, **kwargs) -> str:
        return "companyinformation"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json().get("CompanyInformation", {})


class Contracts(FortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/contracts/
    """
    primary_key = "DocumentNumber"

    def path(self, **kwargs) -> str:
        return "contracts"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for contract in response.json().get("Contracts", []):
            del contract["CustomerName"]
            yield contract


class CostCenters(FortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/cost-centers/
    """
    primary_key = "Code"

    def path(self, **kwargs) -> str:
        return "costcenters"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("CostCenters", [])


class Expenses(FortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/expenses/
    """
    primary_key = "Code"

    def path(self, **kwargs) -> str:
        return "expenses"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for expense in response.json().get("Expenses", []):
            del expense["Text"]
            yield expense


class FinancialYears(FortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/financial-years/
    """
    primary_key = "Id"

    def path(self, **kwargs) -> str:
        return "financialyears"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("FinancialYears", [])


class InvoicePayments(FortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/invoice-payments/
    """
    primary_key = "Number"

    def path(self, **kwargs) -> str:
        return "invoicepayments"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("InvoicePayments", [])


class Invoices(FortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/invoices/
    """
    primary_key = "DocumentNumber"

    def path(self, **kwargs) -> str:
        return "invoices"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for invoice in response.json().get("Invoices", []):
            del invoice["CustomerName"]
            yield invoice


class OrderList(IncrementalFortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/orders/
    """
    primary_key = "DocumentNumber"
    use_cache = True

    def path(self, **kwargs) -> str:
        return "orders"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for order in response.json().get("Orders", []):
            yield self.schema_applier.apply_schema_transformations(order, self.get_json_schema())

    def request_params(self, *,
                       next_page_token: Mapping[str, Any] = None,
                       stream_state: Mapping[str, Any] = None,
                       **kwargs) -> MutableMapping[str, Any]:
        return {**super().request_params(next_page_token=next_page_token, **kwargs), "lastmodified": stream_state}


class Orders(HttpSubStream, IncrementalFortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/orders/
    """
    primary_key = "DocumentNumber"

    def __init__(self, **kwargs):
        super().__init__(OrderList(**kwargs), **kwargs)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        document_number = stream_slice["parent"]["DocumentNumber"]
        return f"orders/{document_number}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        order = response.json().get("Order", [])
        yield self.schema_applier.apply_schema_transformations(order, self.get_json_schema())


class SalaryTransactions(FortnoxStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "salarytransactions"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("SalaryTransactions", [])


class SupplierInvoicePayments(FortnoxStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "supplierinvoicepayments"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("SupplierInvoicePayments", [])


class Vouchers(IncrementalFortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/vouchers/
    """
    primary_key = ["VoucherSeries", "VoucherNumber", "Year"]
    use_cache = True

    def path(self, **kwargs) -> str:
        return "vouchers"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for voucher in response.json().get("Vouchers", []):
            del voucher["Description"]
            yield voucher

    def request_params(self, *,
                       next_page_token: Mapping[str, Any] = None,
                       stream_state: Mapping[str, Any] = None,
                       **kwargs) -> MutableMapping[str, Any]:
        return {**super().request_params(next_page_token=next_page_token, **kwargs), "lastmodified": stream_state}


class VoucherDetails(HttpSubStream, IncrementalFortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/vouchers/#Retrieve-a-voucher
    """
    primary_key = ["VoucherSeries", "VoucherNumber", "Year"]

    def __init__(self, **kwargs):
        super().__init__(Vouchers(**kwargs), **kwargs)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        voucher_number = stream_slice["parent"]["VoucherNumber"]
        voucher_series = stream_slice["parent"]["VoucherSeries"]
        return f"vouchers/{voucher_series}/{voucher_number}"

    def request_params(self, *, stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        return {"financialyear": stream_slice["parent"]["Year"]}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        voucher = response.json().get("Voucher", [])
        del voucher["Description"]
        yield voucher


class CustomerList(IncrementalFortnoxStream):
    """
    https://developer.fortnox.se/documentation/resources/customers
    """
    primary_key = ["CustomerNumber"]
    use_cache = True

    def path(self, **kwargs) -> str:
        return "customers"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for customer in response.json().get("Customers", []):
            del customer["Address1"]
            del customer["Address2"]
            del customer["Email"]
            del customer["Name"]
            del customer["OrganisationNumber"]
            del customer["Phone"]
            yield customer

    def request_params(self, *,
                       next_page_token: Mapping[str, Any] = None,
                       stream_state: Mapping[str, Any] = None,
                       **kwargs) -> MutableMapping[str, Any]:
        return {**super().request_params(next_page_token=next_page_token, **kwargs), "lastmodified": stream_state}


class Customers(HttpSubStream, IncrementalFortnoxStream):
    primary_key = ["CustomerNumber"]
    """
    https://developer.fortnox.se/documentation/resources/customers/#Retrieve-a-customer
    """

    def __init__(self, **kwargs):
        super().__init__(CustomerList(**kwargs), **kwargs)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        customer_number = stream_slice["parent"]["CustomerNumber"]
        return f"customers/{customer_number}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        customer_raw = response.json().get("Customer", {})
        customer = {}
        customer["Active"] = customer_raw["Active"]
        customer["CostCenter"] = customer_raw["CostCenter"]
        customer["Country"] = customer_raw["Country"]
        customer["CountryCode"] = customer_raw["CountryCode"]
        customer["Currency"] = customer_raw["Currency"]
        customer["CustomerNumber"] = customer_raw["CustomerNumber"]
        customer["DeliveryCountry"] = customer_raw["DeliveryCountry"]
        customer["DeliveryCountryCode"] = customer_raw["DeliveryCountryCode"]
        customer["InvoiceAdministrationFee"] = customer_raw["InvoiceAdministrationFee"]
        customer["InvoiceDiscount"] = customer_raw["InvoiceDiscount"]
        customer["InvoiceFreight"] = customer_raw["InvoiceFreight"]
        customer["PriceList"] = customer_raw["PriceList"]
        customer["Project"] = customer_raw["Project"]
        customer["SalesAccount"] = customer_raw["SalesAccount"]
        customer["ShowPriceVATIncluded"] = customer_raw["ShowPriceVATIncluded"]
        customer["TermsOfDelivery"] = customer_raw["TermsOfDelivery"]
        customer["TermsOfPayment"] = customer_raw["TermsOfPayment"]
        customer["Type"] = customer_raw["Type"]
        customer["ZipCode"] = customer_raw["ZipCode"]
        yield customer


class SourceFortnox(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            auth = RemoteTokenAuthenticator(service_id="fortnox", **config)
            company_information_stream = CompanyInformation(authenticator=auth, **config)
            for record in company_information_stream.read_records(sync_mode=SyncMode.full_refresh):
                print(f"company information: {record}")
            return True, None
        except Exception as e:
            print(e)
            return False, repr(e)

    def read(self, logger: logging.Logger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog,
             state: MutableMapping[str, Any] = None) -> Iterator[AirbyteMessage]:
        yield from super().read(logger, config, catalog, state)
        date = (datetime.now().date() - timedelta(days=2)).strftime("%Y-%m-%d")
        incremental_syncs = [stream.stream.name for stream in catalog.streams if
                             stream.sync_mode == SyncMode.incremental]
        yield AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={st: date for st in incremental_syncs}))

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        authenticator = RemoteTokenAuthenticator(service_id="fortnox", **config)
        return [
            Accounts(authenticator=authenticator, **config),
            CompanyInformation(authenticator=authenticator, **config),
            Contracts(authenticator=authenticator, **config),
            CostCenters(authenticator=authenticator, **config),
            Expenses(authenticator=authenticator, **config),
            FinancialYears(authenticator=authenticator, **config),
            InvoicePayments(authenticator=authenticator, **config),
            Invoices(authenticator=authenticator, **config),
            Orders(authenticator=authenticator, **config),
            SalaryTransactions(authenticator=authenticator, **config),
            SupplierInvoicePayments(authenticator=authenticator, **config),
            Vouchers(authenticator=authenticator, **config),
            VoucherDetails(authenticator=authenticator, **config),
            Customers(authenticator=authenticator, **config)
        ]
