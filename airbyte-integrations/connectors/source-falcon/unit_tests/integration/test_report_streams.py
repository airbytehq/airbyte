# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
import pathlib
from unittest import TestCase

import jsonschema
from config_builder import ConfigBuilder
from source_falcon.source import SourceFalcon

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


class TestReports(TestCase):
    def catalog(self, report_id: str, sync_mode: SyncMode = SyncMode.full_refresh):
        return CatalogBuilder().with_stream(name=f"test/{report_id}", sync_mode=sync_mode).build()

    def config(self, report_id: str):
        return ConfigBuilder().with_report_id(f"test/{report_id}").raas_build()

    def xml_schema_content(self, report: str):
        with open(
            str(pathlib.Path(__file__).parent.parent / "resource/http/response/xml" / f"{report}.xml"),
            "r",
        ) as f:
            return f.read()

    def mock_schema_request(self, http_mocker: HttpMocker, report: str):
        http_mocker.get(
            HttpRequest(url=f"https://test_host/ccx/service/customreport2/test_tenant/test/{report}?xsd"),
            HttpResponse(body=self.xml_schema_content(report), status_code=200),
        )

    def mock_read_request(self, http_mocker: HttpMocker, report: str):
        http_mocker.get(
            HttpRequest(url=f"https://test_host/ccx/service/customreport2/test_tenant/test/{report}?format=json"),
            HttpResponse(
                body=json.dumps(find_template(f"json/{report}", __file__)),
                status_code=200,
            ),
        )

    def mock_requests(self, http_mocker: HttpMocker, report: str):
        self.mock_schema_request(http_mocker, report)
        self.mock_read_request(http_mocker, report)

    def get_expected_json_schema(self, report: str):
        with open(
            str(pathlib.Path(__file__).parent.parent / "resource/json_schema" / f"{report}.json"),
            "r",
        ) as f:
            return json.load(f)

    @HttpMocker()
    def test_read_reports(self, http_mocker: HttpMocker):
        for report in ["report_1", "report_2"]:
            self.mock_requests(http_mocker, report)
            output = read(SourceFalcon(), self.config(report), self.catalog(report))
            assert len(output.records) == 3

    @HttpMocker()
    def test_read_than_transform_record_fields(self, http_mocker: HttpMocker):
        for report, field_to_transform in [
            ("report_1", "Eligibility_Rules"),
            ("report_2", "Job_Family_Group_for_Job_Family"),
        ]:
            self.mock_requests(http_mocker, report)
            output = read(SourceFalcon(), self.config(report), self.catalog(report))

            assert len(output.records) == 3

            for record in output.records:
                transformed_field = record.record.data[field_to_transform]
                assert isinstance(transformed_field, list)
                assert transformed_field[0]["ID"]

    @HttpMocker()
    def test_discover(self, http_mocker: HttpMocker):
        for report in ["report_1", "report_2"]:
            self.mock_schema_request(http_mocker, report)

            output = discover(SourceFalcon(), self.config(report))
            assert output.catalog.catalog

            stream_names = [stream.name for stream in output.catalog.catalog.streams]
            assert f"test/{report}" in stream_names

            for stream in output.catalog.catalog.streams:
                if stream.name == f"test/{report}":
                    assert stream.json_schema == self.get_expected_json_schema(report)

    @HttpMocker()
    def test_read_record_follows_json_schema(self, http_mocker: HttpMocker):
        for report in ["report_1", "report_2"]:
            self.mock_requests(http_mocker, report)
            stream_schema = self.get_expected_json_schema(report)

            output = read(SourceFalcon(), self.config(report), self.catalog(report))

            assert len(output.records) == 3

            for record in output.records:
                jsonschema.validate(record.record.data, schema=stream_schema)
