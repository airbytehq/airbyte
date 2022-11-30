#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os

import pytest
from octavia_cli import api_http_headers


class TestApiHttpHeader:
    @pytest.mark.parametrize(
        "header_name, header_value, expected_error, expected_name, expected_value",
        [
            ("foo", "bar", None, "foo", "bar"),
            (" foo ", " bar ", None, "foo", "bar"),
            ("", "bar", AttributeError, None, None),
            ("foo", "", AttributeError, None, None),
        ],
    )
    def test_init(self, header_name, header_value, expected_error, expected_name, expected_value):
        if expected_error is None:
            api_http_header = api_http_headers.ApiHttpHeader(header_name, header_value)
            assert api_http_header.name == expected_name and api_http_header.value == expected_value
        else:
            with pytest.raises(expected_error):
                api_http_headers.ApiHttpHeader(header_name, header_value)


@pytest.fixture
def api_http_header_env_var():
    os.environ["API_HTTP_HEADER_IN_ENV_VAR"] = "bar"
    yield "bar"
    del os.environ["API_HTTP_HEADER_IN_ENV_VAR"]


@pytest.mark.parametrize(
    "yaml_document, expected_api_http_headers, expected_error",
    [
        (
            """
    headers:
      Content-Type: ${API_HTTP_HEADER_IN_ENV_VAR}
    """,
            [api_http_headers.ApiHttpHeader("Content-Type", "bar")],
            None,
        ),
        (
            """
    headers:
      Content-Type: application/json
    """,
            [api_http_headers.ApiHttpHeader("Content-Type", "application/json")],
            None,
        ),
        (
            """
    headers:
      Content-Type: application/csv
      Content-Type: application/json
    """,
            [api_http_headers.ApiHttpHeader("Content-Type", "application/json")],
            None,
        ),
        (
            """
    headers:
      Content-Type: application/json
      Authorization: Bearer XXX
    """,
            [
                api_http_headers.ApiHttpHeader("Content-Type", "application/json"),
                api_http_headers.ApiHttpHeader("Authorization", "Bearer XXX"),
            ],
            None,
        ),
        ("no_headers: foo", None, api_http_headers.InvalidApiHttpHeadersFileError),
        ("", None, api_http_headers.InvalidApiHttpHeadersFileError),
        (
            """
     some random words
     - some dashes:
      - and_next
     """.strip(),
            None,
            api_http_headers.InvalidApiHttpHeadersFileError,
        ),
    ],
)
def test_deserialize_file_based_headers(api_http_header_env_var, tmp_path, yaml_document, expected_api_http_headers, expected_error):
    yaml_file_path = tmp_path / "api_http_headers.yaml"
    yaml_file_path.write_text(yaml_document)
    if expected_error is None:
        file_based_headers = api_http_headers.deserialize_file_based_headers(yaml_file_path)
        assert file_based_headers == expected_api_http_headers
    else:
        with pytest.raises(expected_error):
            api_http_headers.deserialize_file_based_headers(yaml_file_path)


@pytest.mark.parametrize(
    "option_based_headers, expected_option_based_headers",
    [
        ([("Content-Type", "application/json")], [api_http_headers.ApiHttpHeader("Content-Type", "application/json")]),
        (
            [("Content-Type", "application/yaml"), ("Content-Type", "application/json")],
            [api_http_headers.ApiHttpHeader("Content-Type", "application/json")],
        ),
        (
            [("Content-Type", "application/json"), ("Authorization", "Bearer XXX")],
            [
                api_http_headers.ApiHttpHeader("Content-Type", "application/json"),
                api_http_headers.ApiHttpHeader("Authorization", "Bearer XXX"),
            ],
        ),
        ([], []),
    ],
)
def test_deserialize_option_based_headers(option_based_headers, expected_option_based_headers):
    assert api_http_headers.deserialize_option_based_headers(option_based_headers) == expected_option_based_headers


@pytest.mark.parametrize(
    "yaml_document, option_based_raw_headers, expected_merged_headers",
    [
        (
            """
    headers:
      Content-Type: application/csv
    """,
            [("Content-Type", "application/json")],
            [api_http_headers.ApiHttpHeader("Content-Type", "application/json")],
        ),
        (
            None,
            [("Content-Type", "application/json")],
            [api_http_headers.ApiHttpHeader("Content-Type", "application/json")],
        ),
        (
            """
    headers:
      Content-Type: application/json
    """,
            [],
            [api_http_headers.ApiHttpHeader("Content-Type", "application/json")],
        ),
        (
            """
    headers:
      Content-Type: application/json
    """,
            None,
            [api_http_headers.ApiHttpHeader("Content-Type", "application/json")],
        ),
        (
            """
    headers:
      Content-Type: application/json
    """,
            [("Authorization", "Bearer XXX")],
            [
                api_http_headers.ApiHttpHeader("Content-Type", "application/json"),
                api_http_headers.ApiHttpHeader("Authorization", "Bearer XXX"),
            ],
        ),
        (
            """
    headers:
      Content-Type: application/json
      Foo: Bar
    """,
            [("Authorization", "Bearer XXX")],
            [
                api_http_headers.ApiHttpHeader("Content-Type", "application/json"),
                api_http_headers.ApiHttpHeader("Foo", "Bar"),
                api_http_headers.ApiHttpHeader("Authorization", "Bearer XXX"),
            ],
        ),
    ],
)
def test_merge_api_headers(tmp_path, mocker, yaml_document, option_based_raw_headers, expected_merged_headers):
    mocker.patch.object(api_http_headers.click, "echo")
    if yaml_document is not None:
        yaml_file_path = tmp_path / "api_http_headers.yaml"
        yaml_file_path.write_text(yaml_document)
    else:
        yaml_file_path = None
    assert api_http_headers.merge_api_headers(option_based_raw_headers, yaml_file_path) == expected_merged_headers
    if option_based_raw_headers and yaml_file_path:
        api_http_headers.click.echo.assert_called_with(
            "ℹ️  - You passed API HTTP headers in a file and in options at the same time. Option based headers will override file based headers."
        )


def test_set_api_headers_on_api_client(mocker, mock_api_client):
    headers = [api_http_headers.ApiHttpHeader("foo", "bar"), api_http_headers.ApiHttpHeader("bar", "foo")]
    api_http_headers.set_api_headers_on_api_client(mock_api_client, headers)
    mock_api_client.set_default_header.assert_has_calls(
        [
            mocker.call(headers[0].name, headers[0].value),
            mocker.call(headers[1].name, headers[1].value),
        ]
    )
