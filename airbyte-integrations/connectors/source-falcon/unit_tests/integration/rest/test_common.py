# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from source_falcon.source import SourceFalcon
from unit_tests.integration.config_builder import ConfigBuilder
from airbyte_cdk.test.state_builder import StateBuilder


class TestCommon(TestCase):
    stream_name: str = None
    output_records_count: int = 3

    def setUp(self):
        if not self.stream_name:
            self.skipTest("Skipping TestCommon")

    def catalog(self, sync_mode: SyncMode = SyncMode.full_refresh):
        return CatalogBuilder().with_stream(name=self.stream_name, sync_mode=sync_mode).build()

    def config(self):
        return ConfigBuilder().with_access_token("test access token").rest_build()

    @HttpMocker()
    def test_read(self, http_mocker):
        http_mocker.get(
            HttpRequest(
                url=f"https://test_host/api/common/v1/test_tenant/{self.stream_name}?limit=100"
            ),
            HttpResponse(body=json.dumps(find_template(f"json/{self.stream_name}", __file__)), status_code=200)

        )
        output = read(SourceFalcon(), self.config(), self.catalog())
        assert len(output.records) == self.output_records_count


class TestOrganizations(TestCommon):
    stream_name = "organizations"


class TestWorkers(TestCommon):
    stream_name = "workers"


class TestWorkersRelatedStreams(TestCommon):
    path: str
    workers: str = "workers"
    output_records_count: int = 9

    @HttpMocker()
    def test_read(self, http_mocker):
        http_mocker.get(
            HttpRequest(
                url=f"https://test_host/api/common/v1/test_tenant/{self.workers}?limit=100"
            ),
            HttpResponse(body=json.dumps(find_template(f"json/{self.workers}", __file__)), status_code=200)

        )
        for id in ["1", "2", "3"]:
            http_mocker.get(
                HttpRequest(
                    url=f"https://test_host/api/common/v1/test_tenant/{self.workers}/{id}/{self.path}?limit=100"
                ),
                HttpResponse(body=json.dumps(find_template(f"json/{self.stream_name}", __file__)), status_code=200)

            )
        output = read(SourceFalcon(), self.config(), self.catalog())
        assert len(output.records) == self.output_records_count


class TestWorkersDirectReports(TestWorkersRelatedStreams):
    stream_name = "workers_direct_reports"
    path = "directReports"

class TestWorkersHistory(TestWorkersRelatedStreams):
    stream_name = "workers_history"
    path = "history"

class TestWorkersPayslips(TestWorkersRelatedStreams):
    stream_name = "workers_payslips"
    path = "paySlips"

    @HttpMocker()
    def test_read_incremental(self, http_mocker):
        http_mocker.get(
            HttpRequest(
                url=f"https://test_host/api/common/v1/test_tenant/{self.workers}?limit=100"
            ),
            HttpResponse(body=json.dumps(find_template(f"json/{self.workers}", __file__)), status_code=200)

        )
        for id in ["1", "2", "3"]:
            http_mocker.get(
                HttpRequest(
                    url=f"https://test_host/api/common/v1/test_tenant/{self.workers}/{id}/{self.path}?limit=100"
                ),
                HttpResponse(body=json.dumps(find_template(f"json/{self.stream_name}", __file__)), status_code=200)

            )

        output = read(
            SourceFalcon(), 
            self.config(),
            self.catalog(SyncMode.incremental), 
            StateBuilder().with_stream_state(
                self.stream_name,
                {
                    "states": [
                        {"partition": {"parent_slice": {}, "worker_id": "1"}, "cursor": {"date": "2024-10-27"}},
                        {"partition": {"parent_slice": {}, "worker_id": "2"}, "cursor": {"date": "2024-10-27"}},
                        {"partition": {"parent_slice": {}, "worker_id": "3"}, "cursor": {"date": "2024-10-27"}},
                    ]
                }
            ).build()
        )
        assert len(output.records) == 0

class TestWorkersTimeOffEntries(TestWorkersRelatedStreams):
    stream_name = "workers_time_off_entries"
    path = "timeOffEntries"

    @HttpMocker()
    def test_read_incremental(self, http_mocker):
        http_mocker.get(
            HttpRequest(
                url=f"https://test_host/api/common/v1/test_tenant/{self.workers}?limit=100"
            ),
            HttpResponse(body=json.dumps(find_template(f"json/{self.workers}", __file__)), status_code=200)

        )
        for id in ["1", "2", "3"]:
            http_mocker.get(
                HttpRequest(
                    url=f"https://test_host/api/common/v1/test_tenant/{self.workers}/{id}/{self.path}?limit=100"
                ),
                HttpResponse(body=json.dumps(find_template(f"json/{self.stream_name}", __file__)), status_code=200)

            )

        output = read(
            SourceFalcon(),
            self.config(),
            self.catalog(SyncMode.incremental),
            StateBuilder().with_stream_state(
                self.stream_name,
                {
                    "states": [
                        {"partition": {"parent_slice": {}, "worker_id": "1"}, "cursor": {"date": "2024-10-27T07:00:00.000Z"}},
                        {"partition": {"parent_slice": {}, "worker_id": "2"}, "cursor": {"date": "2024-10-27T07:00:00.000Z"}},
                        {"partition": {"parent_slice": {}, "worker_id": "3"}, "cursor": {"date": "2024-10-27T07:00:00.000Z"}},
                    ]
                }
            ).build()
        )
        assert len(output.records) == 0
