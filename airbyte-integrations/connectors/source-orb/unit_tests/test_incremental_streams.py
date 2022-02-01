#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_orb.source import CreditsLedgerEntries, Customers, IncrementalOrbStream, OrbStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalOrbStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalOrbStream, "primary_key", "id")
    mocker.patch.object(IncrementalOrbStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalOrbStream()
    expected_cursor_field = "created_at"
    assert stream.cursor_field == expected_cursor_field


@pytest.mark.parametrize(
    ("current_stream_state", "latest_record", "expected_state"),
    [
        (
            dict(created_at="2022-01-25T12:00:00+00:00"),
            dict(created_at="2022-01-26T12:00:00+00:00"),
            dict(created_at="2022-01-26T12:00:00+00:00"),
        ),
        (
            dict(created_at="2022-01-26T12:00:00+00:00"),
            dict(created_at="2022-01-25T12:00:00+00:00"),
            dict(created_at="2022-01-26T12:00:00+00:00"),
        ),
        ({}, dict(created_at="2022-01-25T12:00:00+00:00"), dict(created_at="2022-01-25T12:00:00+00:00")),
    ],
)
def test_get_updated_state(patch_incremental_base_class, mocker, current_stream_state, latest_record, expected_state):
    stream = IncrementalOrbStream()
    inputs = {"current_stream_state": current_stream_state, "latest_record": latest_record}
    assert stream.get_updated_state(**inputs) == expected_state


@pytest.mark.parametrize(
    ("current_stream_state", "next_page_token"),
    [
        (dict(created_at="2022-01-25T12:00:00+00:00"), {"cursor": "f96594d0-8220-11ec-a8a3-0242ac120002"}),
        (dict(created_at="2022-01-25T12:00:00+00:00"), None),
        ({}, None),
    ],
)
def test_request_params(patch_incremental_base_class, mocker, current_stream_state, next_page_token):
    stream = IncrementalOrbStream()
    inputs = {"stream_state": current_stream_state, "next_page_token": next_page_token}

    expected_params = dict(limit=OrbStream.page_size)
    if current_stream_state.get("created_at"):
        expected_params["created_at[gte]"] = current_stream_state["created_at"]
    if next_page_token is not None:
        expected_params["cursor"] = next_page_token["cursor"]

    assert stream.request_params(**inputs) == expected_params


# We have specific unit tests for CreditsLedgerEntries incremental stream
# because that employs slicing logic


@pytest.mark.parametrize(
    ("current_stream_state", "latest_record", "expected_state"),
    [
        # Updates for matching customer already in state
        (
            dict(customer_id_foo=dict(created_at="2022-01-25T12:00:00+00:00")),
            dict(created_at="2022-01-26T12:00:00+00:00", customer=dict(id="customer_id_foo")),
            dict(customer_id_foo=dict(created_at="2022-01-26T12:00:00+00:00")),
        ),
        # No state for customer
        (
            {},
            dict(created_at="2022-01-26T12:00:00+00:00", customer=dict(id="customer_id_foo")),
            dict(customer_id_foo=dict(created_at="2022-01-26T12:00:00+00:00")),
        ),
        # State has different customer than latest record
        (
            dict(customer_id_foo=dict(created_at="2022-01-25T12:00:00+00:00")),
            dict(created_at="2022-01-26T12:00:00+00:00", customer=dict(id="customer_id_bar")),
            dict(
                customer_id_foo=dict(created_at="2022-01-25T12:00:00+00:00"),
                customer_id_bar=dict(created_at="2022-01-26T12:00:00+00:00"),
            ),
        ),
    ],
)
def test_credits_ledger_entries_get_updated_state(mocker, current_stream_state, latest_record, expected_state):
    stream = CreditsLedgerEntries()
    inputs = {"current_stream_state": current_stream_state, "latest_record": latest_record}
    assert stream.get_updated_state(**inputs) == expected_state


def test_credits_ledger_entries_stream_slices(mocker):
    mocker.patch.object(
        Customers, "read_records", return_value=iter([{"id": "1", "name": "Customer Foo"}, {"id": "18", "name": "Customer Bar"}])
    )
    stream = CreditsLedgerEntries()
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [{"customer_id": "1"}, {"customer_id": "18"}]
    assert list(stream.stream_slices(**inputs)) == expected_stream_slice


@pytest.mark.parametrize(
    ("current_stream_state", "current_stream_slice", "next_page_token"),
    [
        # Slice matches customer in state, paginated request
        (
            dict(customer_id_foo=dict(created_at="2022-01-25T12:00:00+00:00")),
            dict(customer_id="customer_id_foo"),
            {"cursor": "f96594d0-8220-11ec-a8a3-0242ac120002"},
        ),
        # Slice matches customer in state, non-paginated request
        (dict(customer_id_foo=dict(created_at="2022-01-25T12:00:00+00:00")), dict(customer_id="customer_id_foo"), None),
        # Slice does not match customer in state, paginated request
        (
            dict(customer_id_foo=dict(created_at="2022-01-25T12:00:00+00:00")),
            dict(customer_id="customer_id_bar"),
            {"cursor": "f96594d0-8220-11ec-a8a3-0242ac120002"},
        ),
        # Slice does not match customer in state, non-paginated request
        (dict(customer_id_foo=dict(created_at="2022-01-25T12:00:00+00:00")), dict(customer_id="customer_id_bar"), None),
        ({}, dict(customer_id="customer_id_baz"), None),
    ],
)
def test_credits_ledger_entries_request_params(mocker, current_stream_state, current_stream_slice, next_page_token):
    stream = CreditsLedgerEntries()
    inputs = {"stream_state": current_stream_state, "stream_slice": current_stream_slice, "next_page_token": next_page_token}
    expected_params = dict(limit=CreditsLedgerEntries.page_size)
    current_slice_state = current_stream_state.get(current_stream_slice["customer_id"], {})
    if current_slice_state.get("created_at"):
        expected_params["created_at[gte]"] = current_slice_state["created_at"]
    if next_page_token is not None:
        expected_params["cursor"] = next_page_token["cursor"]

    assert stream.request_params(**inputs) == expected_params


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalOrbStream, "cursor_field", "dummy_field")
    stream = IncrementalOrbStream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalOrbStream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalOrbStream()
    assert stream.state_checkpoint_interval is None
