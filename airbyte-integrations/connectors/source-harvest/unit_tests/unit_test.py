#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_harvest.source import SourceHarvest
from source_harvest.streams import ExpensesClients, HarvestStream, InvoicePayments

logger = AirbyteLogger()


def test_check_connection_ok(config, mock_stream):
    mock_stream("users", response={"users": [{"id": 1}], "next_page": 2})
    ok, error_msg = SourceHarvest().check_connection(logger, config=config)

    assert ok
    assert not error_msg


def test_check_connection_empty_config(config):
    config = {}

    ok, error_msg = SourceHarvest().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_check_connection_invalid_config(config):
    config.pop("replication_start_date")
    ok, error_msg = SourceHarvest().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_check_connection_exception(config):
    ok, error_msg = SourceHarvest().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_streams(config):
    streams = SourceHarvest().streams(config)

    assert len(streams) == 32


def test_next_page_token(config, mocker):
    next_page = 2
    expected = {"page": next_page}

    instance = HarvestStream(authenticator=NoAuth())

    response = mocker.Mock(spec=requests.Response, request=mocker.Mock(spec=requests.Request))
    response.json.return_value = {"next_page": next_page}

    assert instance.next_page_token(response) == expected


def test_child_stream_slices(config, replication_start_date, mock_stream):
    object_id = 1
    mock_stream("invoices", response={"invoices": [{"id": object_id}]})
    mock_stream(f"invoices/{object_id}/payments", {"invoice_payments": [{"id": object_id}]})

    invoice_payments_instance = InvoicePayments(authenticator=NoAuth(), replication_start_date=replication_start_date)
    stream_slice = next(invoice_payments_instance.stream_slices(sync_mode=None))
    invoice_payments = invoice_payments_instance.read_records(sync_mode=None, stream_slice=stream_slice)

    assert next(invoice_payments)


def test_report_base_stream(config, from_date, mock_stream):
    mock_stream("reports/expenses/clients", response={"results": [{"client_id": 1}]})

    invoice_payments_instance = ExpensesClients(authenticator=NoAuth(), from_date=from_date)
    stream_slice = next(invoice_payments_instance.stream_slices(sync_mode=None))
    invoice_payments = invoice_payments_instance.read_records(sync_mode=None, stream_slice=stream_slice)

    assert next(invoice_payments)
