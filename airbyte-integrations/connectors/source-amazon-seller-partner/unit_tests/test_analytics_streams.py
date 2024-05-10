#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import patch

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from source_amazon_seller_partner.streams import AnalyticsStream, IncrementalAnalyticsStream


class SomeAnalyticsStream(AnalyticsStream):
    name = "GET_ANALYTICS_STREAM"
    result_key = "result_key"
    availability_sla_days = 3


class SomeIncrementalAnalyticsStream(IncrementalAnalyticsStream):
    name = "GET_INCREMENTAL_ANALYTICS_STREAM"
    result_key = "result_key"
    availability_sla_days = 3
    cursor_field = "endDate"


class TestAnalyticsStream:
    @pytest.mark.parametrize(
        ("input_document", "expected_value"),
        (
            ('{"result_key": [{"some_key": "some_value"}]}', [{"some_key": "some_value"}]),
            ('{"wrong_result_key": {"some_key": "some_value"}}', []),
        ),
    )
    def test_parse_document(self, report_init_kwargs, input_document, expected_value):
        stream = SomeAnalyticsStream(**report_init_kwargs)
        assert stream.parse_document(input_document) == expected_value

    @pytest.mark.parametrize(
        ("report_options", "expected_result"),
        (
            ({"reportPeriod": "DAY"}, {"dataStartTime": "2023-09-06T00:00:00Z", "dataEndTime": "2023-09-06T23:59:59Z"}),
            ({"reportPeriod": "WEEK"}, {"dataStartTime": "2023-08-27T00:00:00Z", "dataEndTime": "2023-09-02T23:59:59Z"}),
            ({"reportPeriod": "MONTH"}, {"dataStartTime": "2023-08-01T00:00:00Z", "dataEndTime": "2023-08-31T23:59:59Z"}),
        ),
    )
    def test_augmented_data(self, report_init_kwargs, report_options, expected_result):
        stream = SomeAnalyticsStream(**report_init_kwargs)
        expected_result["reportOptions"] = report_options
        with patch("pendulum.now", return_value=pendulum.parse("2023-09-09T00:00:00Z")):
            assert stream._augmented_data(report_options) == expected_result

    def test_augmented_data_incorrect_period(self, report_init_kwargs):
        stream = SomeAnalyticsStream(**report_init_kwargs)
        report_options = {"reportPeriod": "DAYS123"}
        with pytest.raises(Exception) as e:
            stream._augmented_data(report_options)
        assert e.value.args[0] == [{"message": "This reportPeriod is not implemented."}]

    @pytest.mark.parametrize(
        ("report_options", "report_option_dates"),
        (
            (
                [{"option_name": "reportPeriod", "option_value": "DAY"}],
                {"dataStartTime": "2023-09-06T00:00:00Z", "dataEndTime": "2023-09-06T23:59:59Z", "reportOptions": {"reportPeriod": "DAY"}},
            ),
            ([], {}),
        ),
    )
    def test_report_data(self, report_init_kwargs, report_options, report_option_dates):
        report_init_kwargs["report_options"] = report_options
        stream = SomeAnalyticsStream(**report_init_kwargs)
        expected_data = {"reportType": stream.name, "marketplaceIds": [report_init_kwargs["marketplace_id"]]}
        expected_data.update(report_option_dates)
        with patch("pendulum.now", return_value=pendulum.parse("2023-09-09T00:00:00Z")):
            assert stream._report_data(sync_mode=SyncMode.full_refresh) == expected_data


class TestIncrementalAnalyticsStream:
    @pytest.mark.parametrize(
        "stream_slice",
        (
            ({"dataStartTime": "2022-09-01T00:00:00Z", "dataEndTime": "2022-09-02T00:00:00Z"}),
            ({"dataEndTime": "2022-09-02T00:00:00Z"}),
            ({"dataStartTime": "2022-09-01T00:00:00Z"}),
            ({}),
        ),
    )
    def test_report_data(self, report_init_kwargs, stream_slice):
        stream = SomeIncrementalAnalyticsStream(**report_init_kwargs)
        expected_data = {"reportType": stream.name, "marketplaceIds": [report_init_kwargs["marketplace_id"]]}
        expected_data.update(stream_slice)
        assert (
            stream._report_data(sync_mode=SyncMode.incremental, cursor_field=[stream.cursor_field], stream_slice=stream_slice)
            == expected_data
        )

    @pytest.mark.parametrize(
        ("current_stream_state", "latest_record", "expected_date"),
        (
            ({"endDate": "2022-10-03T00:00:00Z"}, {"endDate": "2022-10-04T00:00:00Z"}, "2022-10-04T00:00:00Z"),
            ({"endDate": "2022-10-04T00:00:00Z"}, {"endDate": "2022-10-03T00:00:00Z"}, "2022-10-04T00:00:00Z"),
            ({}, {"endDate": "2022-10-03T00:00:00Z"}, "2022-10-03T00:00:00Z"),
        ),
    )
    def test_get_updated_state(self, report_init_kwargs, current_stream_state, latest_record, expected_date):
        stream = SomeIncrementalAnalyticsStream(**report_init_kwargs)
        expected_state = {stream.cursor_field: expected_date}
        assert stream.get_updated_state(current_stream_state, latest_record) == expected_state

    @pytest.mark.parametrize(
        ("start_date", "end_date", "stream_state", "fixed_period_in_days", "expected_slices"),
        (
            ("2023-09-05T00:00:00Z", None, None, 1, [{"dataStartTime": "2023-09-05T00:00:00Z", "dataEndTime": "2023-09-05T23:59:59Z"}]),
            (
                "2023-09-05T00:00:00Z",
                "2023-09-06T00:00:00Z",
                None,
                1,
                [{"dataStartTime": "2023-09-05T00:00:00Z", "dataEndTime": "2023-09-05T23:59:59Z"}],
            ),
            (
                "2023-09-05T00:00:00Z",
                "2023-09-07T00:00:00Z",
                {"endDate": "2023-09-06T00:00:00Z"},
                1,
                [{"dataStartTime": "2023-09-06T00:00:00Z", "dataEndTime": "2023-09-06T23:59:59Z"}],
            ),
            (
                "2022-05-01T00:00:00Z",
                "2023-09-05T00:00:00Z",
                None,
                0,
                [
                    {"dataStartTime": "2022-05-01T00:00:00Z", "dataEndTime": "2023-04-30T23:59:59Z"},
                    {"dataStartTime": "2023-05-01T00:00:00Z", "dataEndTime": "2023-09-05T00:00:00Z"},
                ],
            ),
        ),
    )
    def test_stream_slices(self, report_init_kwargs, start_date, end_date, stream_state, fixed_period_in_days, expected_slices):
        report_init_kwargs["replication_start_date"] = start_date
        report_init_kwargs["replication_end_date"] = end_date
        stream = SomeIncrementalAnalyticsStream(**report_init_kwargs)
        stream.fixed_period_in_days = fixed_period_in_days
        with patch("pendulum.now", return_value=pendulum.parse("2023-09-09T00:00:00Z")):
            assert (
                list(stream.stream_slices(sync_mode=SyncMode.incremental, cursor_field=[stream.cursor_field], stream_state=stream_state))
                == expected_slices
            )
