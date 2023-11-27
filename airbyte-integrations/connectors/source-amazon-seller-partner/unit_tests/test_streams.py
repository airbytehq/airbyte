#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict
from unittest.mock import patch

import pendulum
import pytest
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.utils import AirbyteTracedException
from source_amazon_seller_partner.streams import IncrementalReportsAmazonSPStream, ReportsAmazonSPStream, VendorDirectFulfillmentShipping


class SomeReportStream(ReportsAmazonSPStream):
    name = "GET_TEST_REPORT"


class SomeIncrementalReportStream(IncrementalReportsAmazonSPStream):
    name = "GET_TEST_INCREMENTAL_REPORT"
    cursor_field = "dataEndTime"


class TestReportsAmazonSPStream:
    @staticmethod
    def report_init_kwargs() -> Dict[str, Any]:
        return {
            "url_base": "https://test.url",
            "replication_start_date": "2022-09-01T00:00:00Z",
            "marketplace_id": "market",
            "period_in_days": 90,
            "report_options": None,
            "replication_end_date": None,
        }

    def test_next_page_token(self, mocker):
        stream = SomeReportStream(**self.report_init_kwargs())
        assert stream.next_page_token(mocker.Mock(spec=requests.Response)) is None

    def test_request_params(self):
        kwargs = self.report_init_kwargs()
        stream = SomeReportStream(**kwargs)
        assert stream.request_params() == {"MarketplaceIds": kwargs["marketplace_id"]}

    def test_report_data(self):
        kwargs = self.report_init_kwargs()
        kwargs["report_options"] = [
            {"option_name": "some_name_1", "option_value": "some_value_1"},
            {"option_name": "some_name_2", "option_value": "some_value_2"},
        ]
        stream = SomeReportStream(**kwargs)
        expected_data = {
            "reportType": stream.name,
            "marketplaceIds": [kwargs["marketplace_id"]],
            "reportOptions": {"some_name_1": "some_value_1", "some_name_2": "some_value_2"},
        }

        assert stream._report_data(sync_mode=SyncMode.full_refresh) == expected_data

    @pytest.mark.parametrize(
        ("start_date", "end_date", "expected_slices"),
        (
            (
                "2022-09-01T00:00:00Z",
                "2022-10-01T00:00:00Z",
                [{"dataStartTime": "2022-09-01T00:00:00Z", "dataEndTime": "2022-10-01T00:00:00Z"}],
            ),
            (
                "2022-09-01T00:00:00Z",
                "2023-01-01T00:00:00Z",
                [
                    {"dataStartTime": "2022-09-01T00:00:00Z", "dataEndTime": "2022-11-29T23:59:59Z"},
                    {"dataStartTime": "2022-11-30T00:00:00Z", "dataEndTime": "2023-01-01T00:00:00Z"},
                ],
            ),
            (
                "2022-10-01T00:00:00Z",
                None,
                [{"dataStartTime": "2022-10-03T00:00:00Z", "dataEndTime": "2022-12-31T23:59:59Z"}],
            ),
            (
                "2022-11-01T00:00:00Z",
                None,
                [{"dataStartTime": "2022-11-01T00:00:00Z", "dataEndTime": "2023-01-01T00:00:00Z"}],
            ),
        ),
    )
    def test_stream_slices(self, start_date, end_date, expected_slices):
        kwargs = self.report_init_kwargs()
        kwargs["replication_start_date"] = start_date
        kwargs["replication_end_date"] = end_date

        stream = SomeReportStream(**kwargs)
        with patch("pendulum.now", return_value=pendulum.parse("2023-01-01T00:00:00Z")):
            assert list(stream.stream_slices(sync_mode=SyncMode.full_refresh)) == expected_slices

    @pytest.mark.parametrize(
        ("current_stream_state", "latest_record", "expected_date"),
        (
            ({"dataEndTime": "2022-10-03"}, {"dataEndTime": "2022-10-04"}, "2022-10-04"),
            ({"dataEndTime": "2022-10-04"}, {"dataEndTime": "2022-10-03"}, "2022-10-04"),
            ({}, {"dataEndTime": "2022-10-03"}, "2022-10-03"),
        ),
    )
    def test_get_updated_state(self, current_stream_state, latest_record, expected_date):
        stream = SomeIncrementalReportStream(**self.report_init_kwargs())
        expected_state = {stream.cursor_field: expected_date}
        assert stream.get_updated_state(current_stream_state, latest_record) == expected_state

    def test_read_records_retrieve_fatal(self, mocker, requests_mock):
        mocker.patch("time.sleep", lambda x: None)
        requests_mock.register_uri(
            "POST",
            "https://api.amazon.com/auth/o2/token",
            status_code=200,
            json={"access_token": "access_token", "expires_in": "3600"},
        )

        report_id = "some_report_id"
        requests_mock.register_uri(
            "POST",
            "https://test.url/reports/2021-06-30/reports",
            status_code=201,
            json={"reportId": report_id},
        )
        requests_mock.register_uri(
            "GET",
            f"https://test.url/reports/2021-06-30/reports/{report_id}",
            status_code=200,
            json={"processingStatus": "FATAL", "dataEndTime": "2022-10-03T00:00:00Z"},
        )

        stream = SomeReportStream(**self.report_init_kwargs())
        with pytest.raises(AirbyteTracedException) as e:
            list(stream.read_records(sync_mode=SyncMode.full_refresh))
        assert e.value.message == "The report for stream 'GET_TEST_REPORT' was not created - skip reading"

    def test_read_records_retrieve_cancelled(self, mocker, requests_mock, caplog):
        mocker.patch("time.sleep", lambda x: None)
        requests_mock.register_uri(
            "POST",
            "https://api.amazon.com/auth/o2/token",
            status_code=200,
            json={"access_token": "access_token", "expires_in": "3600"},
        )

        report_id = "some_report_id"
        requests_mock.register_uri(
            "POST",
            "https://test.url/reports/2021-06-30/reports",
            status_code=201,
            json={"reportId": report_id},
        )
        requests_mock.register_uri(
            "GET",
            f"https://test.url/reports/2021-06-30/reports/{report_id}",
            status_code=200,
            json={"processingStatus": "CANCELLED", "dataEndTime": "2022-10-03T00:00:00Z"},
        )

        stream = SomeReportStream(**self.report_init_kwargs())
        list(stream.read_records(sync_mode=SyncMode.full_refresh))
        assert "The report for stream 'GET_TEST_REPORT' was cancelled or there is no data to return" in caplog.messages[-1]

    def test_read_records_retrieve_done(self, mocker, requests_mock):
        mocker.patch("time.sleep", lambda x: None)
        requests_mock.register_uri(
            "POST",
            "https://api.amazon.com/auth/o2/token",
            status_code=200,
            json={"access_token": "access_token", "expires_in": "3600"},
        )

        report_id = "some_report_id"
        document_id = "some_document_id"
        requests_mock.register_uri(
            "POST",
            "https://test.url/reports/2021-06-30/reports",
            status_code=201,
            json={"reportId": report_id},
        )
        requests_mock.register_uri(
            "GET",
            f"https://test.url/reports/2021-06-30/reports/{report_id}",
            status_code=200,
            json={"processingStatus": "DONE", "dataEndTime": "2022-10-03T00:00:00Z", "reportDocumentId": document_id},
        )
        requests_mock.register_uri(
            "GET",
            f"https://test.url/reports/2021-06-30/documents/{document_id}",
            status_code=200,
            json={"reportDocumentId": document_id},
        )

        stream = SomeReportStream(**self.report_init_kwargs())
        with patch.object(stream, "parse_response", return_value=[{"some_key": "some_value"}]):
            records = list(stream.read_records(sync_mode=SyncMode.full_refresh))
        assert records[0] == {"some_key": "some_value", "dataEndTime": "2022-10-03"}


class TestVendorDirectFulfillmentShipping:
    @staticmethod
    def report_init_kwargs() -> Dict[str, Any]:
        return {
            "url_base": "https://test.url",
            "replication_start_date": "2022-09-01T00:00:00Z",
            "marketplace_id": "market",
            "period_in_days": 90,
            "report_options": None,
            "replication_end_date": None,
        }

    @pytest.mark.parametrize(
        ("start_date", "end_date", "expected_params"),
        (
            ("2022-09-01T00:00:00Z", None, {"createdAfter": "2022-09-01T00:00:00Z", "createdBefore": "2022-09-05T00:00:00Z"}),
            ("2022-08-01T00:00:00Z", None, {"createdAfter": "2022-08-28T23:00:00Z", "createdBefore": "2022-09-05T00:00:00Z"}),
            (
                "2022-09-01T00:00:00Z",
                "2022-09-05T00:00:00Z",
                {"createdAfter": "2022-09-01T00:00:00Z", "createdBefore": "2022-09-05T00:00:00Z"},
            ),
        ),
    )
    def test_request_params(self, start_date, end_date, expected_params):
        kwargs = self.report_init_kwargs()
        kwargs["replication_start_date"] = start_date
        kwargs["replication_end_date"] = end_date

        stream = VendorDirectFulfillmentShipping(**kwargs)
        with patch("pendulum.now", return_value=pendulum.parse("2022-09-05T00:00:00Z")):
            assert stream.request_params(stream_state={}) == expected_params
