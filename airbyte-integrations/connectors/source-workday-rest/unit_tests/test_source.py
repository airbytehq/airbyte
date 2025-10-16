# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import json
import pathlib
import unittest
from unittest.mock import MagicMock

from conftest import get_source

from airbyte_cdk.models import Status
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


class TestSourceWorkday(unittest.TestCase):
    rest_config = {
        "tenant_id": "test_tenant",
        "host": "test_host",
        "start_date": "2024-05-01T00:00:00.000Z",
        "credentials": {
            "access_token": "test_access_token",
            "auth_type": "REST",
        },
    }

    def test_rest_streams(self):
        source = get_source(self.rest_config)
        streams = source.streams(self.rest_config)
        assert len(streams) == 11

    @HttpMocker()
    def test_rest_check(self, http_mocker: HttpMocker):
        source = get_source(self.rest_config)

        http_mocker.get(
            HttpRequest(
                url="https://test_host/api/common/v1/test_tenant/workers?limit=100",
            ),
            HttpResponse(
                body=json.dumps(json.dumps(find_template("json/workers", __file__))),
                status_code=200,
            ),
        )

        assert source.check(MagicMock(), self.rest_config).status == Status.SUCCEEDED
