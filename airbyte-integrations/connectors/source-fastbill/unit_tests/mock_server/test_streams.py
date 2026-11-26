# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64
import json
import logging
from pathlib import Path
from unittest import TestCase

import yaml
from unit_tests.conftest import MANIFEST_PATH, get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_API_URL = "https://my.fastbill.com/api/1.0/api.php"
_CONFIG = {"username": "user@example.com", "api_key": "abc123KEY"}
_AUTHORIZATION = "Basic dXNlckBleGFtcGxlLmNvbTphYmMxMjNLRVk="


def _request(service: str, offset: int | None = None, authorization: str = _AUTHORIZATION) -> HttpRequest:
    body = {"LIMIT": 100, "SERVICE": service, "Content-Type": "application/json"}
    if offset is not None:
        body["OFFSET"] = offset
    return HttpRequest(
        url=_API_URL,
        body=body,
        headers={"Authorization": authorization},
    )


def _response(records_key: str, records: list[dict]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"RESPONSE": {records_key: records}}), status_code=200)


def _read_stream(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)


def _walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_manifest_uses_only_declarative_components():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())

    assert all("class_name" not in item for item in _walk(manifest))
    assert manifest["definitions"]["base_requester"]["authenticator"]["type"] == "BasicHttpAuthenticator"
    assert not MANIFEST_PATH.with_name("components.py").exists()


class TestFastbillStreams(TestCase):
    @HttpMocker()
    def test_basic_auth_header_matches_legacy_encoding_with_ascii_credentials(self, http_mocker: HttpMocker):
        username = "user@example.com"
        password = "abc123KEY"
        legacy_authorization = "Basic " + base64.b64encode(
            b":".join((username.encode("latin1"), password.encode("latin1")))
        ).strip().decode("utf-8")
        assert _AUTHORIZATION == legacy_authorization

        expected_record = {"INVOICE_ID": "invoice-1"}
        request = _request("invoice.get", authorization=_AUTHORIZATION)
        http_mocker.post(request, _response("INVOICES", [expected_record]))
        output = _read_stream("invoices")

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)
        assert [message.record.data for message in output.records] == [expected_record]

    @HttpMocker()
    def test_invoices_paginate_by_offset_until_a_short_page(self, http_mocker: HttpMocker):
        first_page = [{"INVOICE_ID": f"invoice-{index}"} for index in range(100)]
        second_page = [{"INVOICE_ID": "invoice-100"}]
        first_request = _request("invoice.get")
        second_request = _request("invoice.get", offset=100)

        http_mocker.post(first_request, _response("INVOICES", first_page))
        http_mocker.post(second_request, _response("INVOICES", second_page))

        output = _read_stream("invoices")

        assert output.errors == []
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)
        assert [message.record.data for message in output.records] == first_page + second_page

    def _assert_single_page_stream(self, http_mocker: HttpMocker, stream_name: str, service: str, records_key: str, record: dict):
        request = _request(service)
        http_mocker.post(request, _response(records_key, [record]))

        output = _read_stream(stream_name)

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)
        assert [message.record.data for message in output.records] == [record]

    @HttpMocker()
    def test_customers_single_page_records(self, http_mocker: HttpMocker):
        self._assert_single_page_stream(http_mocker, "customers", "customer.get", "CUSTOMERS", {"CUSTOMER_ID": "customer-1"})

    @HttpMocker()
    def test_recurring_invoices_single_page_records(self, http_mocker: HttpMocker):
        self._assert_single_page_stream(
            http_mocker, "recurring_invoices", "recurring.get", "INVOICES", {"INVOICE_ID": "recurring-invoice-1"}
        )

    @HttpMocker()
    def test_products_single_page_records(self, http_mocker: HttpMocker):
        self._assert_single_page_stream(http_mocker, "products", "article.get", "ARTICLES", {"ARTICLE_ID": "product-1"})

    @HttpMocker()
    def test_revenues_single_page_records(self, http_mocker: HttpMocker):
        self._assert_single_page_stream(http_mocker, "revenues", "revenue.get", "REVENUES", {"INVOICE_ID": "revenue-1"})

    @HttpMocker()
    def test_check_succeeds_when_invoices_are_read(self, http_mocker: HttpMocker):
        request = _request("invoice.get")
        http_mocker.post(request, _response("INVOICES", [{"INVOICE_ID": "invoice-1"}]))

        status = get_source(_CONFIG).check(logging.getLogger("airbyte"), _CONFIG)

        assert status.status == Status.SUCCEEDED
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_check_fails_when_invoices_return_unauthorized(self, http_mocker: HttpMocker):
        request = _request("invoice.get")
        http_mocker.post(request, HttpResponse(body='{"error": "Unauthorized"}', status_code=401))

        status = get_source(_CONFIG).check(logging.getLogger("airbyte"), _CONFIG)

        assert status.status == Status.FAILED
        http_mocker.assert_number_of_calls(request, 1)
