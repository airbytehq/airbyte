#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
import logging

import pytest
from click.testing import CliRunner
from octavia_cli import api_http_headers, entrypoint

logging.basicConfig()  # you need to initialize logging, otherwise you will not see anything from vcrpy
vcr_log = logging.getLogger("vcr")
vcr_log.setLevel(logging.WARN)

AIRBYTE_URL = "http://localhost:8000"
AIRBYTE_USERNAME = "airbyte"
AIRBYTE_PASSWORD = "password"


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "record_mode": "rewrite",
        "match_on": ["method", "scheme", "host", "port", "path", "query", "headers"],
    }


@pytest.fixture
def file_based_headers(tmp_path):
    yaml_document = """
    headers:
      Custom-Header: Foo
    """
    custom_api_http_headers_yaml_file_path = tmp_path / "custom_api_http_headers.yaml"
    custom_api_http_headers_yaml_file_path.write_text(yaml_document)
    expected_headers = [api_http_headers.ApiHttpHeader("Custom-Header", "Foo")]
    return custom_api_http_headers_yaml_file_path, expected_headers


@pytest.fixture
def option_based_headers():
    return ["Another-Custom-Header", "Bar"], [api_http_headers.ApiHttpHeader("Another-Custom-Header", "Bar")]


@pytest.mark.vcr
def test_api_http_headers(vcr, file_based_headers, option_based_headers):
    raw_option_based_headers, expected_option_based_headers = option_based_headers
    custom_api_http_headers_yaml_file_path, expected_file_based_headers = file_based_headers
    basic_auth_header_value = f"Basic {base64.b64encode(f'{AIRBYTE_USERNAME}:{AIRBYTE_PASSWORD}'.encode()).decode()}"
    expected_headers = (
        expected_option_based_headers
        + expected_file_based_headers
        + [api_http_headers.ApiHttpHeader("Authorization", basic_auth_header_value)]
    )
    runner = CliRunner()
    command_options = (
        [
            "--airbyte-url",
            AIRBYTE_URL,
            "--airbyte-username",
            AIRBYTE_USERNAME,
            "--airbyte-password",
            AIRBYTE_PASSWORD,
            "--api-http-headers-file-path",
            custom_api_http_headers_yaml_file_path,
            "--api-http-header",
        ]
        + raw_option_based_headers
        + ["list", "connectors", "sources"]
    )

    result = runner.invoke(entrypoint.octavia, command_options, obj={})
    for request in vcr.requests:
        for expected_header in expected_headers:
            assert request.headers[expected_header.name] == expected_header.value
    assert result.exit_code == 0
