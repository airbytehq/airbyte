#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from copy import deepcopy
from unittest.mock import DEFAULT, MagicMock, Mock, call

import pendulum
import pytest
from source_google_ads.google_ads import GoogleAds
from source_google_ads.streams import CampaignCriterion, ChangeStatus

from airbyte_cdk.models import SyncMode
from airbyte_cdk.utils import AirbyteTracedException


def mock_response_parent():
    yield [
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:01.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "ADDED",
            "change_status.campaign_criterion": "1",
        },
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:02.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "ADDED",
            "change_status.campaign_criterion": "2",
        },
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:03.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "3",
        },
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:04.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "4",
        },
    ]


def mock_response_child():
    yield [
        {"customer.id": 123, "campaign.id": 1, "campaign_criterion.resource_name": "1"},
        {"customer.id": 123, "campaign.id": 1, "campaign_criterion.resource_name": "2"},
    ]


class MockGoogleAds(GoogleAds):
    def parse_single_result(self, schema, result):
        return result

    def send_request(self, query: str, customer_id: str, login_customer_id: str = "default"):
        if query == "query_parent":
            return mock_response_parent()
        else:
            return mock_response_child()


def test_change_status_stream(config, customers):
    """ """
    customer_id = next(iter(customers)).id
    stream_slice = {"customer_id": customer_id, "login_customer_id": "default"}

    google_api = MockGoogleAds(credentials=config["credentials"])

    stream = ChangeStatus(api=google_api, customers=customers)

    stream.get_query = Mock()
    stream.get_query.return_value = "query_parent"

    result = list(
        stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["change_status.last_change_date_time"], stream_slice=stream_slice)
    )
    assert len(result) == 4
    assert stream.get_query.call_count == 1
    stream.get_query.assert_called_with({"customer_id": customer_id, "login_customer_id": "default"})


def test_change_status_stream_slices(config, additional_customers):
    """Change status stream slices should return correct empty slices for the new customers"""
    google_api = MockGoogleAds(credentials=config["credentials"])

    stream = ChangeStatus(api=google_api, customers=additional_customers)

    now = pendulum.datetime(2023, 11, 2, 12, 53, 7)
    pendulum.set_test_now(now)

    stream_state = {"123": {"change_status.last_change_date_time": "2023-11-01 12:36:04.772447"}}

    result_slices = list(stream.stream_slices(stream_state=stream_state))
    assert len(result_slices) == 2
    assert result_slices == [
        {
            "start_date": "2023-11-01 12:36:04.772447",
            "end_date": "2023-11-02 00:00:00.000000",
            "customer_id": "123",
            "login_customer_id": None,
        },
        {"customer_id": "789", "login_customer_id": None},
    ]


def test_incremental_events_stream_slices(config, additional_customers):
    """Test if the empty slice will be produced for the new customers"""
    stream_state = {"change_status": {"123": {"change_status.last_change_date_time": "2023-06-12 13:20:01.003295"}}}

    google_api = MockGoogleAds(credentials=config["credentials"])

    stream = CampaignCriterion(api=google_api, customers=additional_customers)
    parent_stream = stream.parent_stream

    parent_stream.get_query = Mock()
    parent_stream.get_query.return_value = "query_parent"

    parent_stream.state = stream_state["change_status"]

    stream.get_query = Mock()
    stream.get_query.return_value = "query_child"

    now = pendulum.datetime(2023, 6, 15, 12, 53, 7)
    pendulum.set_test_now(now)

    stream_slices = list(stream.stream_slices(stream_state=stream_state))

    assert len(stream_slices) == 2
    assert stream_slices == [
        {
            "customer_id": "123",
            "updated_ids": {"2", "1"},
            "deleted_ids": {"3", "4"},
            "record_changed_time_map": {
                "1": "2023-06-13 12:36:01.772447",
                "2": "2023-06-13 12:36:02.772447",
                "3": "2023-06-13 12:36:03.772447",
                "4": "2023-06-13 12:36:04.772447",
            },
            "login_customer_id": None,
        },
        {"customer_id": "789", "updated_ids": set(), "deleted_ids": set(), "record_changed_time_map": {}, "login_customer_id": None},
    ]


def test_child_incremental_events_read(config, customers):
    """
    Page token expired while reading records on date 2021-01-03
    The latest read record is {"segments.date": "2021-01-03", "click_view.gclid": "4"}
    It should retry reading starting from 2021-01-03, already read records will be reread again from that date.
    It shouldn't read records on 2021-01-01, 2021-01-02
    """
    customer_id = next(iter(customers)).id
    parent_stream_slice = {"customer_id": customer_id, "resource_type": "CAMPAIGN_CRITERION", "login_customer_id": "default"}
    stream_state = {"change_status": {customer_id: {"change_status.last_change_date_time": "2023-08-16 13:20:01.003295"}}}

    google_api = MockGoogleAds(credentials=config["credentials"])

    stream = CampaignCriterion(api=google_api, customers=customers)
    parent_stream = stream.parent_stream

    parent_stream.get_query = Mock()
    parent_stream.get_query.return_value = "query_parent"

    parent_stream.stream_slices = Mock()
    parent_stream.stream_slices.return_value = [parent_stream_slice]

    parent_stream.state = {customer_id: {"change_status.last_change_date_time": "2023-05-16 13:20:01.003295"}}

    stream.get_query = Mock()
    stream.get_query.return_value = "query_child"

    stream_slices = list(stream.stream_slices(stream_state=stream_state))

    assert stream_slices == [
        {
            "customer_id": "123",
            "updated_ids": {"2", "1"},
            "deleted_ids": {"3", "4"},
            "record_changed_time_map": {
                "1": "2023-06-13 12:36:01.772447",
                "2": "2023-06-13 12:36:02.772447",
                "3": "2023-06-13 12:36:03.772447",
                "4": "2023-06-13 12:36:04.772447",
            },
            "login_customer_id": "default",
        }
    ]

    result = list(
        stream.read_records(
            sync_mode=SyncMode.incremental, cursor_field=["change_status.last_change_date_time"], stream_slice=stream_slices[0]
        )
    )
    expected_result = [
        {
            "campaign.id": 1,
            "campaign_criterion.resource_name": "1",
            "change_status.last_change_date_time": "2023-06-13 12:36:01.772447",
            "customer.id": 123,
        },
        {
            "campaign.id": 1,
            "campaign_criterion.resource_name": "2",
            "change_status.last_change_date_time": "2023-06-13 12:36:02.772447",
            "customer.id": 123,
        },
        {"campaign_criterion.resource_name": "3", "deleted_at": "2023-06-13 12:36:03.772447"},
        {"campaign_criterion.resource_name": "4", "deleted_at": "2023-06-13 12:36:04.772447"},
    ]

    assert all([expected_row in result for expected_row in expected_result])

    assert stream.state == {"change_status": {"123": {"change_status.last_change_date_time": "2023-06-13 12:36:04.772447"}}}

    assert stream.get_query.call_count == 1


def mock_response_1():
    yield [
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:01.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "ADDED",
            "change_status.campaign_criterion": "1",
        },
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:02.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "ADDED",
            "change_status.campaign_criterion": "2",
        },
    ]


def mock_response_2():
    yield [
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:03.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "3",
        },
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:04.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "4",
        },
    ]


def mock_response_3():
    yield [
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:04.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "6",
        },
    ]


def mock_response_4():
    yield [
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:04.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "6",
        },
        {
            "change_status.last_change_date_time": "2023-06-13 12:36:04.772447",
            "change_status.resource_type": "CAMPAIGN_CRITERION",
            "change_status.resource_status": "REMOVED",
            "change_status.campaign_criterion": "7",
        },
    ]


class MockGoogleAdsLimit(GoogleAds):
    count = 0

    def parse_single_result(self, schema, result):
        return result

    def send_request(self, query: str, customer_id: str, login_customer_id: str = "default"):
        self.count += 1
        if self.count == 1:
            return mock_response_1()
        elif self.count == 2:
            return mock_response_2()
        else:
            return mock_response_3()


def mock_query_limit(self) -> int:
    return 2  # or whatever value you want for testing


def copy_call_args(mock):
    new_mock = Mock()

    def side_effect(*args, **kwargs):
        args = deepcopy(args)
        kwargs = deepcopy(kwargs)
        new_mock(*args, **kwargs)
        return DEFAULT

    mock.side_effect = side_effect
    return new_mock


def test_query_limit_hit(config, customers):
    """
    Test the behavior of the `read_records` method in the `ChangeStatus` stream when the query limit is hit.

    This test simulates a scenario where the limit is hit and slice start_date is updated with latest record cursor
    """
    customer_id = next(iter(customers)).id
    stream_slice = {
        "customer_id": customer_id,
        "start_date": "2023-06-13 11:35:04.772447",
        "end_date": "2023-06-13 13:36:04.772447",
        "login_customer_id": "default",
    }

    google_api = MockGoogleAdsLimit(credentials=config["credentials"])
    stream_config = dict(
        api=google_api,
        customers=customers,
    )
    stream = ChangeStatus(**stream_config)
    ChangeStatus.query_limit = property(mock_query_limit)
    stream.get_query = Mock(return_value="query")
    get_query_mock = copy_call_args(stream.get_query)

    result = list(
        stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["change_status.last_change_date_time"], stream_slice=stream_slice)
    )

    assert len(result) == 5
    assert stream.get_query.call_count == 3

    get_query_calls = [
        call(
            {
                "customer_id": "123",
                "start_date": "2023-06-13 11:35:04.772447",
                "end_date": "2023-06-13 13:36:04.772447",
                "login_customer_id": "default",
            }
        ),
        call(
            {
                "customer_id": "123",
                "start_date": "2023-06-13 12:36:02.772447",
                "end_date": "2023-06-13 13:36:04.772447",
                "login_customer_id": "default",
            }
        ),
        call(
            {
                "customer_id": "123",
                "start_date": "2023-06-13 12:36:04.772447",
                "end_date": "2023-06-13 13:36:04.772447",
                "login_customer_id": "default",
            }
        ),
    ]

    get_query_mock.assert_has_calls(get_query_calls)


class MockGoogleAdsLimitException(MockGoogleAdsLimit):
    def send_request(self, query: str, customer_id: str, login_customer_id: str = "default"):
        self.count += 1
        if self.count == 1:
            return mock_response_1()
        elif self.count == 2:
            return mock_response_2()
        elif self.count == 3:
            return mock_response_4()


def test_query_limit_hit_exception(config, customers):
    """
    Test the behavior of the `read_records` method in the `ChangeStatus` stream when the query limit is hit.

    This test simulates a scenario where the limit is hit and there are more than query_limit number of records with same cursor,
    then error will be raised
    """
    customer_id = next(iter(customers)).id
    stream_slice = {
        "customer_id": customer_id,
        "start_date": "2023-06-13 11:35:04.772447",
        "end_date": "2023-06-13 13:36:04.772447",
        "login_customer_id": "default",
    }

    google_api = MockGoogleAdsLimitException(credentials=config["credentials"])
    stream_config = dict(
        api=google_api,
        customers=customers,
    )
    stream = ChangeStatus(**stream_config)
    ChangeStatus.query_limit = property(mock_query_limit)
    stream.get_query = Mock(return_value="query")

    with pytest.raises(AirbyteTracedException) as e:
        list(
            stream.read_records(
                sync_mode=SyncMode.incremental, cursor_field=["change_status.last_change_date_time"], stream_slice=stream_slice
            )
        )

    expected_message = "More than limit 2 records with same cursor field. Incremental sync is not possible for this stream."
    assert e.value.message == expected_message


def test_change_status_get_query(mocker, config, customers):
    """
    Test the get_query method of ChangeStatus stream.

    Given a sample stream_slice, it verifies that the returned query is as expected.
    """
    # Setup an instance of the ChangeStatus stream
    google_api = MockGoogleAds(credentials=config["credentials"])
    stream = ChangeStatus(api=google_api, customers=customers)

    # Mock get_json_schema method of the stream to return a predefined schema
    mocker.patch.object(stream, "get_json_schema", return_value={"properties": {"change_status.resource_type": {"type": "str"}}})

    # Define a sample stream_slice for the test
    stream_slice = {
        "start_date": "2023-01-01 00:00:00.000000",
        "end_date": "2023-09-19 00:00:00.000000",
        "resource_type": "SOME_RESOURCE_TYPE",
        "login_customer_id": "default",
    }

    # Call the get_query method with the stream_slice
    query = stream.get_query(stream_slice=stream_slice)

    # Expected result based on the provided sample
    expected_query = """SELECT change_status.resource_type FROM change_status WHERE change_status.last_change_date_time >= '2023-01-01 00:00:00.000000' AND change_status.last_change_date_time <= '2023-09-19 00:00:00.000000' AND change_status.resource_type = 'SOME_RESOURCE_TYPE' ORDER BY change_status.last_change_date_time ASC LIMIT 2"""

    # Check that the result from the get_query method matches the expected query
    assert query == expected_query


def are_queries_equivalent(query1, query2):
    # Split the queries to extract the list of criteria
    criteria1 = query1.split("IN (")[1].rstrip(")").split(", ")
    criteria2 = query2.split("IN (")[1].rstrip(")").split(", ")

    # Sort the criteria for comparison
    criteria1_sorted = sorted(criteria1)
    criteria2_sorted = sorted(criteria2)

    # Replace the original criteria with the sorted version in the queries
    query1_sorted = query1.replace(", ".join(criteria1), ", ".join(criteria1_sorted))
    query2_sorted = query2.replace(", ".join(criteria2), ", ".join(criteria2_sorted))

    return query1_sorted == query2_sorted


def test_incremental_events_stream_get_query(mocker, config, customers):
    """
    Test the get_query method of the IncrementalEventsStream class.

    Given a sample stream_slice, this test will verify that the returned query string is as expected.
    """
    # Setup an instance of the CampaignCriterion stream
    google_api = MockGoogleAds(credentials=config["credentials"])
    stream = CampaignCriterion(api=google_api, customers=customers)

    # Mock get_json_schema method of the stream to return a predefined schema
    mocker.patch.object(stream, "get_json_schema", return_value={"properties": {"campaign_criterion.resource_name": {"type": "str"}}})

    # Define a sample stream_slice for the test
    stream_slice = {
        "customer_id": "1234567890",
        "updated_ids": {
            "customers/1234567890/adGroupCriteria/111111111111~1",
            "customers/1234567890/adGroupCriteria/111111111111~2",
            "customers/1234567890/adGroupCriteria/111111111111~3",
        },
        "deleted_ids": {
            "customers/1234567890/adGroupCriteria/111111111111~4",
            "customers/1234567890/adGroupCriteria/111111111111~5",
        },
        "record_changed_time_map": {
            "customers/1234567890/adGroupCriteria/111111111111~1": "2023-09-18 08:56:53.413023",
            "customers/1234567890/adGroupCriteria/111111111111~2": "2023-09-18 08:56:59.165599",
            "customers/1234567890/adGroupCriteria/111111111111~3": "2023-09-18 08:56:59.165599",
            "customers/1234567890/adGroupCriteria/111111111111~4": "2023-09-18 08:56:59.165599",
            "customers/1234567890/adGroupCriteria/111111111111~5": "2023-09-18 08:56:59.165599",
        },
        "login_customer_id": "default",
    }

    # Call the get_query method with the stream_slice
    query = stream.get_query(stream_slice=stream_slice)

    # Assuming the generated query should look like:
    expected_query = (
        "SELECT campaign_criterion.resource_name "
        "FROM campaign_criterion "
        "WHERE campaign_criterion.resource_name IN ("
        "'customers/1234567890/adGroupCriteria/111111111111~1', "
        "'customers/1234567890/adGroupCriteria/111111111111~2', "
        "'customers/1234567890/adGroupCriteria/111111111111~3')"
    )

    # Check if the query generated by the get_query method matches the expected query
    assert are_queries_equivalent(query, expected_query)


def test_read_records_with_slice_splitting(mocker, config):
    """
    Test the read_records method to ensure it correctly splits the stream_slice and calls the parent's read_records.
    """
    # Define a stream_slice with 15,000 ids to ensure it gets split during processing
    stream_slice = {
        "updated_ids": set(range(15000)),
        "record_changed_time_map": {i: f"time_{i}" for i in range(15000)},
        "customer_id": "sample_customer_id",
        "deleted_ids": set(),
        "login_customer_id": "default",
    }

    # Create a mock instance of the CampaignCriterion stream
    google_api = MockGoogleAds(credentials=config["credentials"])
    stream = CampaignCriterion(api=google_api, customers=[])

    # Mock methods that are expected to be called during the test
    super_read_records_mock = MagicMock()
    mocker.patch("source_google_ads.streams.GoogleAdsStream.read_records", super_read_records_mock)
    read_deleted_records_mock = mocker.patch.object(stream, "_read_deleted_records", return_value=[])
    update_state_mock = mocker.patch.object(stream, "_update_state")

    # Execute the method under test
    list(stream.read_records(SyncMode.incremental, stream_slice=stream_slice))

    # Verify that the parent's read_records method was called twice due to splitting
    assert super_read_records_mock.call_count == 2

    # Define the expected slices after the stream_slice is split
    expected_first_slice = {
        "updated_ids": set(range(10000)),
        "record_changed_time_map": {i: f"time_{i}" for i in range(10000)},
        "customer_id": "sample_customer_id",
        "deleted_ids": set(),
        "login_customer_id": "default",
    }
    expected_second_slice = {
        "updated_ids": set(range(10000, 15000)),
        "record_changed_time_map": {i: f"time_{i}" for i in range(10000, 15000)},
        "customer_id": "sample_customer_id",
        "deleted_ids": set(),
        "login_customer_id": "default",
    }

    # Verify the arguments passed to the parent's read_records method for both calls
    first_call_args, first_call_kwargs = super_read_records_mock.call_args_list[0]
    assert first_call_args[0] == SyncMode.incremental
    assert first_call_kwargs["stream_slice"] == expected_first_slice
    second_call_args, second_call_kwargs = super_read_records_mock.call_args_list[1]
    assert second_call_args[0] == SyncMode.incremental
    assert second_call_kwargs["stream_slice"] == expected_second_slice

    # Ensure that the mocked methods were called as expected
    read_deleted_records_mock.assert_called_once_with(stream_slice)
    update_state_mock.assert_called_once_with(stream_slice)


def test_update_state_with_parent_state(mocker):
    """
    Test the _update_state method when the parent_stream has a state.
    """
    # Mock instance setup
    stream = CampaignCriterion(api=MagicMock(), customers=[])

    # Mock parent_stream with initial state
    stream.parent_stream.state = {"customer_id_1": {"change_status.last_change_date_time": "2023-10-20 00:00:00.000000"}}

    # Call the _update_state method with the first stream_slice
    stream_slice_first = {"customer_id": "customer_id_1"}
    stream._update_state(stream_slice_first)

    # Assert the state after the first call
    expected_state_first_call = {"change_status": {"customer_id_1": {"change_status.last_change_date_time": "2023-10-20 00:00:00.000000"}}}
    assert stream._state == expected_state_first_call

    # Update the parent_stream state for the second call
    stream.parent_stream.state = {"customer_id_2": {"change_status.last_change_date_time": "2023-10-21 00:00:00.000000"}}

    # Call the _update_state method with the second stream_slice
    stream_slice_second = {"customer_id": "customer_id_2"}
    stream._update_state(stream_slice_second)

    # Assert the state after the second call
    expected_state_second_call = {
        "change_status": {
            "customer_id_1": {"change_status.last_change_date_time": "2023-10-20 00:00:00.000000"},
            "customer_id_2": {"change_status.last_change_date_time": "2023-10-21 00:00:00.000000"},
        }
    }
    assert stream._state == expected_state_second_call

    # Set pendulum to return a consistent value
    now = pendulum.datetime(2023, 11, 2, 12, 53, 7)
    pendulum.set_test_now(now)

    # Call the _update_state method with the third stream_slice
    stream_slice_third = {"customer_id": "customer_id_3"}
    stream._update_state(stream_slice_third)

    # Assert the state after the third call
    expected_state_third_call = {
        "change_status": {
            "customer_id_1": {"change_status.last_change_date_time": "2023-10-20 00:00:00.000000"},
            "customer_id_2": {"change_status.last_change_date_time": "2023-10-21 00:00:00.000000"},
            "customer_id_3": {"change_status.last_change_date_time": "2023-11-02 00:00:00.000000"},
        }
    }
    assert stream._state == expected_state_third_call

    # Reset the pendulum mock to its original state
    pendulum.set_test_now()


def test_update_state_without_parent_state(mocker):
    """
    Test the _update_state method when the parent_stream does not have a state.
    """
    # Reset any previous mock state for pendulum
    pendulum.set_test_now()

    # Mock instance setup
    stream = CampaignCriterion(api=MagicMock(), customers=[])

    # Mock pendulum call to return a consistent value
    now = pendulum.datetime(2023, 11, 2, 12, 53, 7)
    pendulum.set_test_now(now)

    # Call the _update_state method with the first stream_slice
    stream_slice_first = {"customer_id": "customer_id_1"}
    stream._update_state(stream_slice_first)

    # Assert the state after the first call
    expected_state_first_call = {"change_status": {"customer_id_1": {"change_status.last_change_date_time": "2023-11-02 00:00:00.000000"}}}
    assert stream._state == expected_state_first_call

    # Call the _update_state method with the second stream_slice
    stream_slice_second = {"customer_id": "customer_id_2"}
    stream._update_state(stream_slice_second)

    # Assert the state after the second call
    expected_state_second_call = {
        "change_status": {
            "customer_id_1": {"change_status.last_change_date_time": "2023-11-02 00:00:00.000000"},
            "customer_id_2": {"change_status.last_change_date_time": "2023-11-02 00:00:00.000000"},
        }
    }
    assert stream._state == expected_state_second_call

    # Reset the pendulum mock to its original state
    pendulum.set_test_now()
