#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_xero.streams import BankTransactions, IncrementalXeroStream

from .utils import read_incremental


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalXeroStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalXeroStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalXeroStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalXeroStream(tenant_id="tenant_id", start_date=datetime.datetime.now())
    expected_cursor_field = "UpdatedDateUTC"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalXeroStream(tenant_id="tenant_id", start_date=datetime.datetime.now())
    date = datetime.datetime.now().replace(microsecond=0)
    inputs = {"current_stream_state": {"UpdatedDateUTC": "2022-01-01"}, "latest_record": {"UpdatedDateUTC": date.isoformat()}}
    expected_state = {"UpdatedDateUTC": date.isoformat()}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalXeroStream(tenant_id="tenant_id", start_date=datetime.datetime.now())
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalXeroStream, "cursor_field", "dummy_field")
    stream = IncrementalXeroStream(tenant_id="tenant_id", start_date=datetime.datetime.now())
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalXeroStream(tenant_id="tenant_id", start_date=datetime.datetime.now())
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalXeroStream(tenant_id="tenant_id", start_date=datetime.datetime.now())
    expected_checkpoint_interval = 100
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


def test_read_incremental(requests_mock):

    json_responses = iter([
        {
            'BankTransactions': [
                {'BankTransactionID': '4848c602-aeba-4e01-a533-8eae3e090633', 'UpdatedDateUTC': '/Date(1630412754013+0000)/'},
                {'BankTransactionID': '550c811d-66d3-4b72-9334-4555d22c85b5', 'UpdatedDateUTC': '/Date(1630413087633+0000)/'},
            ]
        },
        {
            'BankTransactions': [
                {'BankTransactionID': '9a704749-8084-4eed-9554-4edccaa1b6ce', 'UpdatedDateUTC': '/Date(1630413149867+0000)/'}
            ]
        }
    ])

    requests_mock.get(
        "https://api.xero.com/api.xro/2.0/bankTransactions",
        json=lambda request, context: next(json_responses),
    )

    start_date = datetime.datetime(2021, 8, 31, 0, 0, 0, 0)
    stream = BankTransactions(tenant_id="tenant_id", start_date=start_date)
    stream_state = {}
    records = read_incremental(stream, stream_state)
    assert records == [
        {'BankTransactionID': '4848c602-aeba-4e01-a533-8eae3e090633', 'UpdatedDateUTC': '2021-08-31T12:25:54+00:00'},
        {'BankTransactionID': '550c811d-66d3-4b72-9334-4555d22c85b5', 'UpdatedDateUTC': '2021-08-31T12:31:27+00:00'}
    ]
    assert stream_state == {'UpdatedDateUTC': '2021-08-31T12:31:27+00:00'}
    records = read_incremental(stream, stream_state)
    assert stream_state == {'UpdatedDateUTC': '2021-08-31T12:32:29+00:00'}
    assert records == [
        {'BankTransactionID': '9a704749-8084-4eed-9554-4edccaa1b6ce', 'UpdatedDateUTC': '2021-08-31T12:32:29+00:00'}
    ]
