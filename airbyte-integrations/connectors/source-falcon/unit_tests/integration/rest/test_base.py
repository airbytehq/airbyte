# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from copy import deepcopy
from typing import Any, Dict, List
from unittest import TestCase

from source_falcon.source import SourceFalcon
from unit_tests.integration.config_builder import ConfigBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


class TestBase(TestCase):
    stream_name: str = None
    path: str = None
    space: str = None
    output_records_count: int = 3

    def setUp(self):
        if not self.stream_name:
            self.skipTest(f"Skipping TestBase")

    def get_path(self):
        if not self.path:
            return self.stream_name
        return self.path

    def catalog(self, sync_mode: SyncMode = SyncMode.full_refresh):
        return CatalogBuilder().with_stream(name=self.stream_name, sync_mode=sync_mode).build()

    def config(self):
        return ConfigBuilder().with_access_token("test access token").rest_build()

    @HttpMocker()
    def test_read(self, http_mocker):
        http_mocker.get(
            HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.get_path()}?limit=100"),
            HttpResponse(
                body=json.dumps(find_template(f"json/{self.stream_name}", __file__)),
                status_code=200,
            ),
        )
        output = read(SourceFalcon(), self.config(), self.catalog())
        assert len(output.records) == self.output_records_count
        # verify auth method
        assert http_mocker._mocker._adapter._matchers[0].last_request.headers["Authorization"] == "Bearer test access token"

    def create_range_of_records(self, start: int, end: int) -> List[Dict[str, Any]]:
        record = find_template(f"json/{self.stream_name}", __file__)["data"][0]
        records = []
        for id in range(start, end + 1):
            rec = deepcopy(record)
            rec["id"] = id
            records.append(rec)
        return records

    @HttpMocker()
    def test_pagination(self, http_mocker):
        records_page_1 = self.create_range_of_records(1, 100)
        records_page_2 = self.create_range_of_records(101, 200)
        records_page_3 = self.create_range_of_records(201, 250)
        total = 250
        http_mocker.get(
            HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.get_path()}?limit=100"),
            HttpResponse(
                body=json.dumps(
                    {"data": records_page_1, "total": total},
                ),
                status_code=200,
            ),
        )
        http_mocker.get(
            HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.get_path()}?limit=100&offset=100"),
            HttpResponse(
                body=json.dumps(
                    {"data": records_page_2, "total": total},
                ),
                status_code=200,
            ),
        )
        http_mocker.get(
            HttpRequest(url=f"https://test_host/api/{self.space}/v1/test_tenant/{self.get_path()}?limit=100&offset=200"),
            HttpResponse(
                body=json.dumps(
                    {"data": records_page_3, "total": total},
                ),
                status_code=200,
            ),
        )

        output = read(SourceFalcon(), self.config(), self.catalog())
        assert len(output.records) == total
