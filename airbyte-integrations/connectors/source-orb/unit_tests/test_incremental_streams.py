#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pendulum
import pytest
import responses
from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_orb.source import (
    CreditsLedgerEntries,
    Customers,
    IncrementalOrbStream,
    Invoices,
    OrbStream,
    Plans,
    Subscriptions,
    SubscriptionUsage,
)


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
    ("config", "current_stream_state", "next_page_token", "expected_params"),
    [
        (
            {},
            dict(created_at="2022-01-25T12:00:00+00:00"),
            {"cursor": "f96594d0-8220-11ec-a8a3-0242ac120002"},
            {"created_at[gte]": "2022-01-25T12:00:00+00:00", "cursor": "f96594d0-8220-11ec-a8a3-0242ac120002"},
        ),
        ({}, dict(created_at="2022-01-25T12:00:00+00:00"), None, {"created_at[gte]": "2022-01-25T12:00:00+00:00"}),
        # Honors lookback_window_days
        (
            dict(lookback_window_days=3),
            dict(created_at="2022-01-25T12:00:00+00:00"),
            None,
            {"created_at[gte]": "2022-01-22T12:00:00+00:00"},
        ),
        ({}, {}, None, None),
        (dict(start_date=pendulum.parse("2022-01-25T12:00:00+00:00")), {}, None, {"created_at[gte]": "2022-01-25T12:00:00+00:00"}),
        (
            dict(start_date=pendulum.parse("2022-01-25T12:00:00+00:00")),
            dict(created_at="2022-01-26T12:00:00+00:00"),
            None,
            {"created_at[gte]": "2022-01-26T12:00:00+00:00"},
        ),
        # Honors lookback_window_days
        (
            dict(start_date=pendulum.parse("2022-01-25T12:00:00+00:00"), lookback_window_days=2),
            dict(created_at="2022-01-26T12:00:00+00:00"),
            None,
            {"created_at[gte]": "2022-01-24T12:00:00+00:00"},
        ),
    ],
)
def test_request_params(patch_incremental_base_class, mocker, config, current_stream_state, next_page_token, expected_params):
    stream = IncrementalOrbStream(**config)
    inputs = {"stream_state": current_stream_state, "next_page_token": next_page_token}
    expected_params = expected_params or {}
    expected_params["limit"] = OrbStream.page_size
    assert stream.request_params(**inputs) == expected_params


@pytest.mark.parametrize(
    ("config", "current_stream_state", "next_page_token", "expected_params"),
    [
        (
            {},
            dict(invoice_date="2022-01-25T12:00:00+00:00"),
            {"cursor": "f96594d0-8220-11ec-a8a3-0242ac120002"},
            {"invoice_date[gte]": "2022-01-25T12:00:00+00:00", "cursor": "f96594d0-8220-11ec-a8a3-0242ac120002"},
        ),
        ({}, dict(invoice_date="2022-01-25T12:00:00+00:00"), None, {"invoice_date[gte]": "2022-01-25T12:00:00+00:00"}),
        # Honors lookback_window_days
        (
            dict(lookback_window_days=3),
            dict(invoice_date="2022-01-25T12:00:00+00:00"),
            None,
            {"invoice_date[gte]": "2022-01-22T12:00:00+00:00"},
        ),
        ({}, {}, None, None),
    ],
)
def test_invoices_request_params(patch_incremental_base_class, mocker, config, current_stream_state, next_page_token, expected_params):
    stream = Invoices(**config)
    inputs = {"stream_state": current_stream_state, "next_page_token": next_page_token}
    expected_params = expected_params or {}
    expected_params["limit"] = OrbStream.page_size
    expected_params["status[]"] = ["void", "paid", "issued", "synced"]
    assert stream.request_params(**inputs) == expected_params


# We have specific unit tests for CreditsLedgerEntries incremental stream
# because that employs slicing logic


@pytest.mark.parametrize(
    ("current_stream_state", "latest_record", "expected_state"),
    [
        # Updates for matching customer already in state
        (
            dict(customer_id_foo=dict(created_at="2022-01-25T12:00:00+00:00")),
            dict(created_at="2022-01-26T12:00:00+00:00", customer_id="customer_id_foo"),
            dict(customer_id_foo=dict(created_at="2022-01-26T12:00:00+00:00")),
        ),
        # No state for customer
        (
            {},
            dict(created_at="2022-01-26T12:00:00+00:00", customer_id="customer_id_foo"),
            dict(customer_id_foo=dict(created_at="2022-01-26T12:00:00+00:00")),
        ),
        # State has different customer than latest record
        (
            dict(customer_id_foo=dict(created_at="2022-01-25T12:00:00+00:00")),
            dict(created_at="2022-01-26T12:00:00+00:00", customer_id="customer_id_bar"),
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


@pytest.mark.parametrize(
    ("current_stream_state", "latest_record", "expected_state"),
    [
        # No state
        (
            {},
            dict(invoice_date="2022-01-26T12:00:00+00:00"),
            dict(invoice_date="2022-01-26T12:00:00+00:00"),
        ),
        # Existing state
        (
            dict(invoice_date="2022-01-26T12:00:00+00:00"),
            dict(invoice_date="2023-01-26T12:00:00+00:00"),
            dict(invoice_date="2023-01-26T12:00:00+00:00"),
        ),
    ],
)
def test_invoices_get_updated_state(mocker, current_stream_state, latest_record, expected_state):
    stream = Invoices()
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
    expected_params = dict(limit=CreditsLedgerEntries.page_size, entry_status="committed")
    current_slice_state = current_stream_state.get(current_stream_slice["customer_id"], {})
    if current_slice_state.get("created_at"):
        expected_params["created_at[gte]"] = current_slice_state["created_at"]
    if next_page_token is not None:
        expected_params["cursor"] = next_page_token["cursor"]

    assert stream.request_params(**inputs) == expected_params


def test_credits_ledger_entries_transform_record(mocker):
    stream = CreditsLedgerEntries()
    ledger_entry_record = {
        "event_id": "foo-event-id",
        "entry_type": "decrement",
        "customer": {
            "id": "foo-customer-id",
        },
        "credit_block": {"expiry_date": "2023-01-25T12:00:00+00:00", "id": "2k6hj0s8dfhj0d7h", "per_unit_cost_basis": "2.50"},
    }

    # Validate that calling transform record unwraps nested customer and credit block fields.
    assert stream.transform_record(ledger_entry_record) == {
        "event_id": "foo-event-id",
        "entry_type": "decrement",
        "customer_id": "foo-customer-id",
        "block_expiry_date": "2023-01-25T12:00:00+00:00",
        "credit_block_id": "2k6hj0s8dfhj0d7h",
        "credit_block_per_unit_cost_basis": "2.50",
    }


@responses.activate
def test_credits_ledger_entries_no_matching_events(mocker):
    stream = CreditsLedgerEntries(string_event_properties_keys=["ping"])
    ledger_entries = [{"event_id": "foo-event-id", "entry_type": "decrement", "created_at": "2022-02-21T07:00:00+00:00"}, {"event_id": "bar-event-id", "entry_type": "decrement", "created_at": "2022-02-21T07:00:00+00:00"}]
    mock_response = {
        "data": [
            {
                "customer_id": "foo-customer-id",
                "event_name": "foo-name",
                # Does not match either event_id that we'd expect
                "id": "foo-event-id-2",
                "properties": {"ping": "pong"},
                "timestamp": "2022-02-21T07:00:00+00:00",
            }
        ],
        "pagination_metadata": {"has_more": False, "next_cursor": None},
    }
    responses.add(responses.POST, f"{stream.url_base}events", json=mock_response, status=200)
    enriched_entries = stream.enrich_ledger_entries_with_event_data(ledger_entries)

    # We failed to enrich either event, but still check that the schema was
    # transformed as expected
    assert enriched_entries == [
        {"event": {"id": "foo-event-id"}, "entry_type": "decrement", "created_at": "2022-02-21T07:00:00+00:00"},
        {"event": {"id": "bar-event-id"}, "entry_type": "decrement", "created_at": "2022-02-21T07:00:00+00:00"},
    ]


@pytest.mark.parametrize(
    ("event_properties", "selected_string_property_keys", "selected_numeric_property_keys", "resulting_properties"),
    [
        ({}, ["event-property-foo"], [], {}),
        ({"ping": "pong"}, ["ping"], [], {"ping": "pong"}),
        ({"ping": "pong", "unnamed_property": "foo"}, ["ping"], [], {"ping": "pong"}),
        ({"unnamed_property": "foo"}, ["ping"], [], {}),
        ({"numeric_property": 1}, ["ping"], ["numeric_property"], {"numeric_property": 1}),
        ({"ping": "pong", "numeric_property": 1}, ["ping"], ["numeric_property"], {"ping": "pong", "numeric_property": 1}),
    ],
)
@responses.activate
def test_credits_ledger_entries_enriches_selected_property_keys(
    mocker, event_properties, selected_string_property_keys, selected_numeric_property_keys, resulting_properties
):
    stream = CreditsLedgerEntries(
        string_event_properties_keys=selected_string_property_keys, numeric_event_properties_keys=selected_numeric_property_keys
    )
    original_entry_1 = {"entry_type": "increment"}
    ledger_entries = [{"event_id": "foo-event-id", "entry_type": "decrement", "created_at": "2022-02-21T07:00:00+00:00"}, original_entry_1]
    mock_response = {
        "data": [
            {
                "customer_id": "foo-customer-id",
                "event_name": "foo-name",
                "id": "foo-event-id",
                "properties": event_properties,
                "timestamp": "2022-02-21T07:00:00+00:00",
            }
        ],
        "pagination_metadata": {"has_more": False, "next_cursor": None},
    }
    responses.add(responses.POST, f"{stream.url_base}events", json=mock_response, status=200)
    enriched_entries = stream.enrich_ledger_entries_with_event_data(ledger_entries)

    assert enriched_entries[0] == {"entry_type": "decrement", "created_at": "2022-02-21T07:00:00+00:00", "event": {"id": "foo-event-id", "properties": resulting_properties}}
    # Does not enrich, but still passes back, irrelevant (for enrichment purposes) ledger entry
    assert enriched_entries[1] == original_entry_1


@responses.activate
def test_credits_ledger_entries_enriches_with_multiple_entries_per_event(mocker):
    stream = CreditsLedgerEntries(string_event_properties_keys=["ping"])
    ledger_entries = [{"event_id": "foo-event-id", "entry_type": "decrement", "created_at": "2022-02-21T07:00:00+00:00",}, {"event_id": "foo-event-id", "entry_type": "decrement", "created_at": "2022-02-21T07:00:00+00:00",}]
    mock_response = {
        "data": [
            {
                "customer_id": "foo-customer-id",
                "event_name": "foo-name",
                "id": "foo-event-id",
                "properties": {"ping": "pong"},
                "timestamp": "2022-02-21T07:00:00+00:00",
            }
        ],
        "pagination_metadata": {"has_more": False, "next_cursor": None},
    }
    responses.add(responses.POST, f"{stream.url_base}events", json=mock_response, status=200)
    enriched_entries = stream.enrich_ledger_entries_with_event_data(ledger_entries)

    # We expect both events are enriched correctly
    assert enriched_entries == [
        {"event": {"id": "foo-event-id", "properties": {"ping": "pong"}}, "entry_type": "decrement", "created_at": "2022-02-21T07:00:00+00:00",},
        {"event": {"id": "foo-event-id", "properties": {"ping": "pong"}}, "entry_type": "decrement", "created_at": "2022-02-21T07:00:00+00:00",},
    ]


# We have specific unit tests for SubscriptionUsage incremental stream
# because its logic differs from other IncrementalOrbStreams


@pytest.mark.parametrize(
    ("current_stream_state", "latest_record", "expected_state"),
    [
        # Updates for matching customer already in state
        (
            dict(subscription_id_foo=dict(timeframe_start="2022-01-25T12:00:00+00:00")),
            dict(timeframe_start="2022-01-26T12:00:00+00:00", subscription_id="subscription_id_foo"),
            dict(subscription_id_foo=dict(timeframe_start="2022-01-26T12:00:00+00:00")),
        ),
        # No state for subscription
        (
            {},
            dict(timeframe_start="2022-01-26T12:00:00+00:00", subscription_id="subscription_id_foo"),
            dict(subscription_id_foo=dict(timeframe_start="2022-01-26T12:00:00+00:00")),
        ),
        # State has different subscription than latest record
        (
            dict(subscription_id_foo=dict(timeframe_start="2022-01-25T12:00:00+00:00")),
            dict(timeframe_start="2022-01-26T12:00:00+00:00", subscription_id="subscription_id_bar"),
            dict(
                subscription_id_foo=dict(timeframe_start="2022-01-25T12:00:00+00:00"),
                subscription_id_bar=dict(timeframe_start="2022-01-26T12:00:00+00:00"),
            ),
        ),
    ],
)
def test_subscription_usage_get_updated_state(mocker, current_stream_state, latest_record, expected_state):
    stream = SubscriptionUsage(start_date="2022-01-25T12:00:00+00:00", end_date="2022-01-26T12:00:00+00:00")
    inputs = {"current_stream_state": current_stream_state, "latest_record": latest_record}
    assert stream.get_updated_state(**inputs) == expected_state


def test_subscription_usage_stream_slices(mocker):
    mocker.patch.object(
        Subscriptions,
        "read_records",
        return_value=iter(
            [
                {"id": "1", "plan_id": "2"},
                {"id": "11", "plan_id": "2"},
                {"id": "111", "plan_id": "3"},  # should be ignored because plan_id set to 2
            ]
        ),
    )
    stream = SubscriptionUsage(plan_id="2", start_date="2022-01-25T12:00:00+00:00", end_date="2022-01-26T12:00:00+00:00")
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [
        {"subscription_id": "1", "timeframe_start": "2022-01-25T12:00:00+00:00", "timeframe_end": "2022-01-26T12:00:00+00:00"},
        {"subscription_id": "11", "timeframe_start": "2022-01-25T12:00:00+00:00", "timeframe_end": "2022-01-26T12:00:00+00:00"},
    ]
    assert list(stream.stream_slices(**inputs)) == expected_stream_slice


def test_subscription_usage_stream_slices_with_grouping_key(mocker):
    mocker.patch.object(
        Subscriptions,
        "read_records",
        return_value=iter(
            [
                {"id": "1", "plan_id": "2"},
                {"id": "11", "plan_id": "2"},
                {"id": "111", "plan_id": "3"},  # should be ignored because plan_id set to 2
            ]
        ),
    )

    mocker.patch.object(
        Plans,
        "read_records",
        return_value=iter(
            [
                {"id": "2", "prices": [{"billable_metric": {"id": "billableMetricIdA"}}, {"billable_metric": {"id": "billableMetricIdB"}}]},
                {"id": "3", "prices": [{"billable_metric": {"id": "billableMetricIdC"}}]},  # should be ignored because plan_id is set to 2
            ]
        ),
    )

    # when a grouping_key is present, one slice per billable_metric is created because the Orb API
    # requires one API call per billable metric if the group_by param is in use.
    stream = SubscriptionUsage(
        plan_id="2",
        subscription_usage_grouping_key="groupKey",
        start_date="2022-01-25T12:00:00+00:00",
        end_date="2022-01-26T12:00:00+00:00",
    )
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}

    # one slice per billable metric per subscription that matches the input plan
    expected_stream_slice = [
        {
            "subscription_id": "1",
            "billable_metric_id": "billableMetricIdA",
            "timeframe_start": "2022-01-25T12:00:00+00:00",
            "timeframe_end": "2022-01-26T12:00:00+00:00",
        },
        {
            "subscription_id": "1",
            "billable_metric_id": "billableMetricIdB",
            "timeframe_start": "2022-01-25T12:00:00+00:00",
            "timeframe_end": "2022-01-26T12:00:00+00:00",
        },
        {
            "subscription_id": "11",
            "billable_metric_id": "billableMetricIdA",
            "timeframe_start": "2022-01-25T12:00:00+00:00",
            "timeframe_end": "2022-01-26T12:00:00+00:00",
        },
        {
            "subscription_id": "11",
            "billable_metric_id": "billableMetricIdB",
            "timeframe_start": "2022-01-25T12:00:00+00:00",
            "timeframe_end": "2022-01-26T12:00:00+00:00",
        },
    ]
    assert list(stream.stream_slices(**inputs)) == expected_stream_slice


@pytest.mark.parametrize(
    ("current_stream_state", "current_stream_slice", "grouping_key"),
    [
        # Slice matches subscription in state, no grouping
        (
            dict(subscription_id_foo=dict(timeframe_start="2022-01-25T12:00:00+00:00")),
            dict(
                subscription_id="subscription_id_foo",
                timeframe_start="2022-01-25T12:00:00+00:00",
                timeframe_end="2022-01-26T12:00:00+00:00",
            ),
            None,
        ),
        # Slice does not match subscription in state, no grouping
        (
            dict(subscription_id_foo=dict(timeframe_start="2022-01-25T12:00:00+00:00")),
            dict(
                subscription_id="subscription_id_bar",
                timeframe_start="2022-01-25T12:00:00+00:00",
                timeframe_end="2022-01-26T12:00:00+00:00",
            ),
            None,
        ),
        # No existing state, no grouping
        (
            {},
            dict(
                subscription_id="subscription_id_baz",
                timeframe_start="2022-01-25T12:00:00+00:00",
                timeframe_end="2022-01-26T12:00:00+00:00",
            ),
            None,
        ),
        # Slice matches subscription in state, with grouping
        (
            dict(subscription_id_foo=dict(timeframe_start="2022-01-25T12:00:00+00:00")),
            dict(
                subscription_id="subscription_id_foo",
                billable_metric_id="billableMetricA",
                timeframe_start="2022-01-25T12:00:00+00:00",
                timeframe_end="2022-01-26T12:00:00+00:00",
            ),
            "group_key_foo",
        ),
        # Slice does not match subscription in state, with grouping
        (
            dict(subscription_id_foo=dict(timeframe_start="2022-01-25T12:00:00+00:00")),
            dict(
                subscription_id="subscription_id_bar",
                billable_metric_id="billableMetricA",
                timeframe_start="2022-01-25T12:00:00+00:00",
                timeframe_end="2022-01-26T12:00:00+00:00",
            ),
            "group_key_foo",
        ),
        # No existing state, with grouping
        (
            {},
            dict(
                subscription_id="subscription_id_baz",
                billable_metric_id="billableMetricA",
                timeframe_start="2022-01-25T12:00:00+00:00",
                timeframe_end="2022-01-26T12:00:00+00:00",
            ),
            "group_key_foo",
        ),
    ],
)
def test_subscription_usage_request_params(mocker, current_stream_state, current_stream_slice, grouping_key):
    if grouping_key:
        stream = SubscriptionUsage(
            start_date="2022-01-25T12:00:00+00:00", end_date="2022-01-26T12:00:00+00:00", subscription_usage_grouping_key=grouping_key
        )
    else:
        stream = SubscriptionUsage(start_date="2022-01-25T12:00:00+00:00", end_date="2022-01-26T12:00:00+00:00")

    inputs = {"stream_state": current_stream_state, "stream_slice": current_stream_slice}
    expected_params = dict(granularity="day")

    # always pull the timeframe_start and timeframe_end from the stream slice
    expected_params["timeframe_start"] = current_stream_slice["timeframe_start"]
    expected_params["timeframe_end"] = current_stream_slice["timeframe_end"]

    # if a grouping_key is present, add the group_by and billable_metric_id to params
    if grouping_key:
        expected_params["group_by"] = grouping_key
        expected_params["billable_metric_id"] = current_stream_slice["billable_metric_id"]

    assert stream.request_params(**inputs) == expected_params


def test_subscription_usage_yield_transformed_subrecords(mocker):
    stream = SubscriptionUsage(start_date="2022-01-25T12:00:00+00:00", end_date="2022-01-26T12:00:00+00:00")

    subscription_usage_response = {
        "billable_metric": {"name": "Metric A", "id": "billableMetricA"},
        "usage": [
            {"quantity": 0, "timeframe_start": "2022-01-25T12:00:00+00:00", "timeframe_end": "2022-01-26T12:00:00+00:00"},
            {"quantity": 1, "timeframe_start": "2022-01-25T12:00:00+00:00", "timeframe_end": "2022-01-26T12:00:00+00:00"},
            {"quantity": 2, "timeframe_start": "2022-01-26T12:00:00+00:00", "timeframe_end": "2022-01-27T12:00:00+00:00"},
        ],
        "otherTopLevelField": {"shouldBeIncluded": "true"},
    }

    subscription_id = "subscriptionIdA"

    # Validate that one record is yielded per non-zero usage subrecord
    expected = [
        {
            "quantity": 1,
            "timeframe_start": "2022-01-25T12:00:00+00:00",
            "timeframe_end": "2022-01-26T12:00:00+00:00",
            "billable_metric_name": "Metric A",
            "billable_metric_id": "billableMetricA",
            "otherTopLevelField": {"shouldBeIncluded": "true"},
            "subscription_id": subscription_id,
        },
        {
            "quantity": 2,
            "timeframe_start": "2022-01-26T12:00:00+00:00",
            "timeframe_end": "2022-01-27T12:00:00+00:00",
            "billable_metric_name": "Metric A",
            "billable_metric_id": "billableMetricA",
            "otherTopLevelField": {"shouldBeIncluded": "true"},
            "subscription_id": subscription_id,
        },
    ]

    actual_output = list(stream.yield_transformed_subrecords(subscription_usage_response, subscription_id))

    assert actual_output == expected


def test_subscription_usage_yield_transformed_subrecords_with_grouping(mocker):
    stream = SubscriptionUsage(
        start_date="2022-01-25T12:00:00+00:00", end_date="2022-01-26T12:00:00+00:00", subscription_usage_grouping_key="grouping_key"
    )

    subscription_usage_response = {
        "billable_metric": {"name": "Metric A", "id": "billableMetricA"},
        "metric_group": {"property_key": "grouping_key", "property_value": "grouping_value"},
        "usage": [
            {"quantity": 0, "timeframe_start": "2022-01-25T12:00:00+00:00", "timeframe_end": "2022-01-26T12:00:00+00:00"},
            {"quantity": 1, "timeframe_start": "2022-01-25T12:00:00+00:00", "timeframe_end": "2022-01-26T12:00:00+00:00"},
            {"quantity": 2, "timeframe_start": "2022-01-26T12:00:00+00:00", "timeframe_end": "2022-01-27T12:00:00+00:00"},
        ],
        "otherTopLevelField": {"shouldBeIncluded": "true"},
    }

    subscription_id = "subscriptionIdA"

    # Validate that one record is yielded per non-zero usage subrecord
    expected = [
        {
            "quantity": 1,
            "timeframe_start": "2022-01-25T12:00:00+00:00",
            "timeframe_end": "2022-01-26T12:00:00+00:00",
            "billable_metric_name": "Metric A",
            "billable_metric_id": "billableMetricA",
            "otherTopLevelField": {"shouldBeIncluded": "true"},
            "subscription_id": subscription_id,
            "grouping_key": "grouping_value",
        },
        {
            "quantity": 2,
            "timeframe_start": "2022-01-26T12:00:00+00:00",
            "timeframe_end": "2022-01-27T12:00:00+00:00",
            "billable_metric_name": "Metric A",
            "billable_metric_id": "billableMetricA",
            "otherTopLevelField": {"shouldBeIncluded": "true"},
            "subscription_id": subscription_id,
            "grouping_key": "grouping_value",
        },
    ]

    actual_output = list(stream.yield_transformed_subrecords(subscription_usage_response, subscription_id))

    assert actual_output == expected


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
