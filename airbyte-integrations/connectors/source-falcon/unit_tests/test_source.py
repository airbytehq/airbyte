# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import json
import pathlib
import unittest
from unittest.mock import MagicMock

from source_falcon import SourceFalcon

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


def mock_schema_request(http_mocker: HttpMocker, report: str):
    with open(
        str(pathlib.Path(__file__).parent / "resource/http/response/xml" / f"{report}.xml"),
        "r",
    ) as f:
        xml_schema_content = f.read()

    http_mocker.get(
        HttpRequest(url=f"https://test_host/ccx/service/customreport2/test_tenant/test/{report}?xsd"),
        HttpResponse(body=xml_schema_content, status_code=200),
    )


class TestSourceFalcon(unittest.TestCase):
    raas_config = {
        "tenant_id": "test_tenant",
        "host": "test_host",
        "credentials": {
            "username": "test_user",
            "password": "test_password",
            "report_ids": ["test/report_1"],
            "auth_type": "RAAS",
        },
    }

    rest_config = {
        "tenant_id": "test_tenant",
        "host": "test_host",
        "credentials": {
            "access_token": "test_access_token",
            "start_date": "2024-05-01T00:00:00.000Z",
            "auth_type": "REST",
        },
    }

    @HttpMocker()
    def test_raas_streams(self, http_mocker: HttpMocker):
        source = SourceFalcon()
        mock_schema_request(http_mocker=http_mocker, report="report_1")
        streams = source.streams(self.raas_config)
        assert len(streams) == 1
        assert streams[0].name == self.raas_config["credentials"]["report_ids"][0]

    def test_rest_streams(self):
        source = SourceFalcon()
        streams = source.streams(self.rest_config)
        assert len(streams) == 11

    @HttpMocker()
    def test_raas_check(self, http_mocker: HttpMocker):
        source = SourceFalcon()
        mock_schema_request(http_mocker=http_mocker, report="report_1")

        http_mocker.get(
            HttpRequest(
                url="https://test_host/ccx/service/customreport2/test_tenant/test/report_1?format=json",
            ),
            HttpResponse(
                body=json.dumps(json.dumps(find_template("json/report_1", __file__))),
                status_code=200,
            ),
        )

        assert source.check_connection(MagicMock(), self.raas_config) == (True, None)

    @HttpMocker()
    def test_rest_check(self, http_mocker: HttpMocker):
        source = SourceFalcon()

        http_mocker.get(
            HttpRequest(
                url="https://test_host/api/common/v1/test_tenant/workers?limit=100",
            ),
            HttpResponse(
                body=json.dumps(json.dumps(find_template("json/workers", __file__))),
                status_code=200,
            ),
        )

        assert source.check_connection(MagicMock(), self.rest_config) == (True, None)
