# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict

from source_falcon.source import SourceFalcon
from unit_tests.integration.rest.test_base import TestBase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.test.state_builder import StateBuilder


class TestCommon(TestBase):
    space = "common"


class TestWorkersRelatedStreams(TestCommon):
    path: str
    workers: str = "workers"
    output_records_count: int = 9

    @HttpMocker()
    def test_read(self, http_mocker):
        http_mocker.get(
            HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.workers}?limit=100"),
            HttpResponse(
                body=json.dumps(find_template(f"json/{self.workers}", __file__)),
                status_code=200,
            ),
        )
        for id in ["1", "2", "3"]:
            http_mocker.get(
                HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.workers}/{id}/{self.path}?limit=100"),
                HttpResponse(
                    body=json.dumps(find_template(f"json/{self.stream_name}", __file__)),
                    status_code=200,
                ),
            )
        output = read(SourceFalcon(), self.config(), self.catalog())
        assert len(output.records) == self.output_records_count

    @HttpMocker()
    def test_pagination(self, http_mocker):
        records_page_1 = self.create_range_of_records(1, 100)
        records_page_2 = self.create_range_of_records(101, 200)
        records_page_3 = self.create_range_of_records(201, 250)
        total = 250

        http_mocker.get(
            HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.workers}?limit=100"),
            HttpResponse(
                body=json.dumps(find_template(f"json/{self.workers}", __file__)),
                status_code=200,
            ),
        )

        for id in ["1", "2", "3"]:
            http_mocker.get(
                HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.workers}/{id}/{self.path}?limit=100"),
                HttpResponse(
                    body=json.dumps(
                        {"data": records_page_1, "total": total},
                    ),
                    status_code=200,
                ),
            )
            http_mocker.get(
                HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.workers}/{id}/{self.path}?limit=100&offset=100"),
                HttpResponse(
                    body=json.dumps(
                        {"data": records_page_2, "total": total},
                    ),
                    status_code=200,
                ),
            )
            http_mocker.get(
                HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.workers}/{id}/{self.path}?limit=100&offset=200"),
                HttpResponse(
                    body=json.dumps(
                        {"data": records_page_3, "total": total},
                    ),
                    status_code=200,
                ),
            )

        output = read(SourceFalcon(), self.config(), self.catalog())
        assert len(output.records) == total * 3  # 250 records per worker, workers count is 3


class TestWorkersRelatedStreamsIncremental(TestWorkersRelatedStreams):
    state: Dict[str, Any] = None

    @HttpMocker()
    def test_read_incremental(self, http_mocker):
        http_mocker.get(
            HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.workers}?limit=100"),
            HttpResponse(
                body=json.dumps(find_template(f"json/{self.workers}", __file__)),
                status_code=200,
            ),
        )
        for id in ["1", "2", "3"]:
            http_mocker.get(
                HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.workers}/{id}/{self.path}?limit=100"),
                HttpResponse(
                    body=json.dumps(find_template(f"json/{self.stream_name}", __file__)),
                    status_code=200,
                ),
            )

        output = read(
            SourceFalcon(),
            self.config(),
            self.catalog(SyncMode.incremental),
            StateBuilder().with_stream_state(self.stream_name, self.state).build(),
        )
        assert len(output.records) == 0


class TestOrganizations(TestCommon):
    stream_name = "organizations"


class TestWorkers(TestCommon):
    stream_name = "workers"


class TestWorkersDirectReports(TestWorkersRelatedStreams):
    stream_name = "workers_direct_reports"
    path = "directReports"


class TestWorkersHistory(TestWorkersRelatedStreams):
    stream_name = "workers_history"
    path = "history"


class TestWorkersPayslips(TestWorkersRelatedStreamsIncremental):
    stream_name = "workers_payslips"
    path = "paySlips"
    state = {
        "states": [
            {
                "partition": {"parent_slice": {}, "worker_id": "1"},
                "cursor": {"date": "2024-10-27"},
            },
            {
                "partition": {"parent_slice": {}, "worker_id": "2"},
                "cursor": {"date": "2024-10-27"},
            },
            {
                "partition": {"parent_slice": {}, "worker_id": "3"},
                "cursor": {"date": "2024-10-27"},
            },
        ]
    }


class TestWorkersTimeOffEntries(TestWorkersRelatedStreamsIncremental):
    stream_name = "workers_time_off_entries"
    path = "timeOffEntries"
    state = {
        "states": [
            {
                "partition": {"parent_slice": {}, "worker_id": "1"},
                "cursor": {"date": "2024-10-27T07:00:00.000Z"},
            },
            {
                "partition": {"parent_slice": {}, "worker_id": "2"},
                "cursor": {"date": "2024-10-27T07:00:00.000Z"},
            },
            {
                "partition": {"parent_slice": {}, "worker_id": "3"},
                "cursor": {"date": "2024-10-27T07:00:00.000Z"},
            },
        ]
    }
