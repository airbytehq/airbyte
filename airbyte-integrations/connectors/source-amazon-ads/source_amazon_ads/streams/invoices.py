#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from http import HTTPStatus
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from pendulum import Date
from source_amazon_ads.schemas import InvoicePayload
from source_amazon_ads.streams.common import AmazonAdsStream


class Invoices(AmazonAdsStream):
    """
    This stream corresponds to Amazon Advertising API - Billing/Invoices
    https://advertising.amazon.com/API/docs/en-us/invoices/#/

    how this stream work
    step1: call /invoices API to fetch all the invoice summaries.
    step2: iterate through the invoice summaries and check if the 'fromDate' is >= start_date(user provided via config)
    step3: for all the filtered invoice id, call /invoices/{invoice_id} API to fetch invoice details
    """

    model = InvoicePayload
    primary_key = None
    page_size = 100
    REPORT_DATE_FORMAT = "YYYYMMDD"

    _payload_field = "payload"
    _invoice_summaries_field = "invoiceSummaries"
    _next_page_token_field = "nextCursor"
    _current_profile_id = ""
    _ignore_invoice_statuses = ["ACCUMULATING", "PROCESSING"]

    # this variable is used to mark that we have got all invoices with provided start date by user config.
    # when set to True, next_page_token method will not return the cursor value.
    _got_all_invoices = False

    def __init__(self, config: Mapping[str, Any], *args, **kwargs):
        self._start_date: Optional[Date] = config.get("start_date")
        super().__init__(config, *args, **kwargs)

        # create object of _Invoice class
        # this object would be used to fetch individual invoice details
        self._invoice = _Invoice(config, *args, **kwargs)

    def read_records(self, *args, **kvargs) -> Iterable[Mapping[str, Any]]:
        """
        Iterate through self._profiles list and send read all records for each profile.
        """
        for profile in self._profiles:
            try:
                self._current_profile_id = profile.profileId
                yield from super().read_records(*args, **kvargs)
            except Exception as err:
                self.logger.info("some error occurred: %s", err)

    def request_headers(self, *args, **kvargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kvargs)
        headers["Amazon-Advertising-API-Scope"] = str(self._current_profile_id)
        return headers

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if not self._got_all_invoices:
            stream_data = response.json()
            next_page_token = stream_data.get(self._payload_field, {}).get(self._next_page_token_field, "")
            if next_page_token:
                return {self._next_page_token_field: next_page_token}

    def path(self, **kvargs) -> str:
        return "/invoices"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        # count and cursor parameters can not be used together.
        # only return cursor parameter.
        if next_page_token:
            return {"cursor": next_page_token[self._next_page_token_field]}

        # only return count parameter.
        return {"count": self.page_size}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        return an object representing single record in the response
        """
        invoice_summaries = response.json().get(self._payload_field, {}).get(self._invoice_summaries_field, [])
        if response.status_code == HTTPStatus.OK:
            invoice_list = []
            for record in invoice_summaries:
                if record["status"] in self._ignore_invoice_statuses:
                    continue

                from_date = pendulum.from_format(record["fromDate"], self.REPORT_DATE_FORMAT).date()
                # we do not want to fetch the records older than user provided start date
                if from_date < self._start_date:
                    self._got_all_invoices = True
                    break

                # fetch details of individual invoice
                self._invoice.update_vars(record["id"], self._current_profile_id)
                for res in self._invoice.read_records(sync_mode=SyncMode.full_refresh):
                    invoice_list.append(res)

            yield from invoice_list
            return

        # send error response
        self.error_response(response)


class _Invoice(AmazonAdsStream):
    """
    This stream corresponds to Amazon Advertising API - Billing/Invoices
    https://advertising.amazon.com/API/docs/en-us/invoices/#/invoice/getInvoice
    """

    model = None
    primary_key = None

    _payload_field = "payload"

    def __init__(self, config: Mapping[str, Any], *args, **kwargs):
        self._invoice_id = 0
        self._current_profile_id = 0
        super().__init__(config, *args, **kwargs)

    def update_vars(self, invoice_id: str, profile_id: int):
        self._invoice_id = invoice_id
        self._current_profile_id = profile_id

    def path(self, **kvargs) -> str:
        return "/invoices/%s" % self._invoice_id

    def request_headers(self, *args, **kvargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kvargs)
        headers["Amazon-Advertising-API-Scope"] = str(self._current_profile_id)
        return headers

    def read_records(self, *args, **kvargs) -> Iterable[Mapping[str, Any]]:
        yield from super().read_records(*args, **kvargs)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == HTTPStatus.OK:
            yield from [response.json().get(self._payload_field, {})]
            return

        self.error_response(response)
