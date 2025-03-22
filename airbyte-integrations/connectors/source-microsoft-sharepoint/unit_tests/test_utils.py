# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from datetime import datetime, timedelta
from http import HTTPStatus
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from office365.onedrive.sites.site import Site
from source_microsoft_sharepoint.utils import PlaceholderUrlBuilder, execute_query_with_retry, filter_http_urls, get_site, get_site_prefix

from airbyte_cdk import AirbyteTracedException


class MockResponse:
    def __init__(self, status_code, headers=None):
        self.status_code = status_code
        self.headers = headers or {}


class MockException(Exception):
    def __init__(self, status_code, headers=None):
        self.response = MockResponse(status_code, headers)


@pytest.mark.parametrize(
    "status_code, retry_after_header, expected_retries, error_message",
    [
        (
            HTTPStatus.TOO_MANY_REQUESTS,
            None,
            4,
            "Maximum total wait time of 10 seconds exceeded for execute_query. The latest response status code is 429.",
        ),  # No 'Retry-After' header, should retry max times
        (
            HTTPStatus.SERVICE_UNAVAILABLE,
            "4",
            4,
            "Maximum total wait time of 10 seconds exceeded for execute_query. The latest response status code is 503. Retry-After header: 4",
        ),  # With 'Retry-After' header, limited retries due to time constraint
        (
            HTTPStatus.SERVICE_UNAVAILABLE,
            "1",
            5,
            "Maximum number of retries of 5 exceeded for execute_query.",
        ),  # With 'Retry-After' header, max number of retries
        (HTTPStatus.FORBIDDEN, "1", 1, "Caught unexpected exception"),  # unexpected exception
    ],
)
def test_execute_query_with_retry(status_code, retry_after_header, expected_retries, error_message):
    obj = Mock()
    obj.execute_query = Mock(side_effect=MockException(status_code, {"Retry-After": retry_after_header}))

    with (
        patch("source_microsoft_sharepoint.utils.time.sleep") as mock_sleep,
        patch("source_microsoft_sharepoint.utils.datetime") as mock_datetime,
    ):
        start_time = datetime(2021, 1, 1, 0, 0, 0)
        if retry_after_header:
            mock_datetime.now.side_effect = [start_time] * 2 + [
                start_time + timedelta(seconds=int(retry_after_header) * i) for i in range(5)
            ]
        else:
            mock_datetime.now.side_effect = [start_time] * 2 + [start_time + timedelta(seconds=2**i) for i in range(5)]

        with pytest.raises(AirbyteTracedException) as exception:
            execute_query_with_retry(obj, max_retries=5, initial_retry_after=1, max_retry_after=10, max_total_wait_time=10)
        assert exception.value.message == error_message
        assert obj.execute_query.call_count == expected_retries


def test_execute_query_success_before_max_retries():
    obj = Mock()
    obj.execute_query = Mock(side_effect=[MockException(HTTPStatus.TOO_MANY_REQUESTS), "success"])

    result = execute_query_with_retry(obj, max_retries=5, initial_retry_after=1, max_retry_after=10, max_total_wait_time=10)

    assert obj.execute_query.call_count == 2
    assert result == "success"


def test_filter_http_urls():
    files = [
        Mock(download_url="https://example.com/file1.txt"),
        Mock(download_url="https://example.com/file2.txt"),
        Mock(uri="file3.txt", download_url="http://example.com/file3.txt"),
    ]

    mock_logger = Mock()
    filtered_files = filter_http_urls(files, mock_logger)
    filtered_files = list(filtered_files)

    assert len(filtered_files) == 2
    mock_logger.error.assert_called_once_with("Cannot open file file3.txt. The URL returned by SharePoint is not secure.")


@pytest.mark.parametrize(
    "steps, expected_url",
    [
        (
            # steps is a list of (method_name, argument)
            [
                ("set_scheme", "https"),
                ("set_host", "accounts.google.com"),
                ("set_path", "/o/oauth2/v2/auth"),
                ("add_key_value_placeholder_param", "client_id"),
                ("add_key_value_placeholder_param", "redirect_uri"),
                ("add_literal_param", "response_type=code"),
                ("add_key_value_placeholder_param", "scope"),
                ("add_literal_param", "access_type=offline"),
                ("add_key_value_placeholder_param", "state"),
                ("add_literal_param", "include_granted_scopes=true"),
                ("add_literal_param", "prompt=consent"),
            ],
            # And this is the expected URL for these steps
            "https://accounts.google.com/o/oauth2/v2/auth?{{client_id_param}}&{{redirect_uri_param}}&response_type=code&{{scope_param}}&access_type=offline&{{state_param}}&include_granted_scopes=true&prompt=consent",
        ),
        (
            # steps is a list of (method_name, argument)
            [
                ("set_scheme", "https"),
                ("set_host", "login.microsoftonline.com"),
                ("set_path", "/TENANT_ID/oauth2/v2.0/authorize"),
                ("add_key_value_placeholder_param", "client_id"),
                ("add_key_value_placeholder_param", "redirect_uri"),
                ("add_key_value_placeholder_param", "state"),
                ("add_key_value_placeholder_param", "scope"),
                ("add_literal_param", "response_type=code"),
            ],
            # And this is the expected URL for these steps
            "https://login.microsoftonline.com/TENANT_ID/oauth2/v2.0/authorize?{{client_id_param}}&{{redirect_uri_param}}&{{state_param}}&{{scope_param}}&response_type=code",
        ),
        (
            [
                ("set_scheme", "https"),
                ("set_host", "oauth2.googleapis.com"),
                ("set_path", "/token"),
                ("add_key_value_placeholder_param", "client_id"),
                ("add_key_value_placeholder_param", "client_secret"),
                ("add_key_value_placeholder_param", "auth_code"),
                ("add_key_value_placeholder_param", "redirect_uri"),
                ("add_literal_param", "grant_type=authorization_code"),
            ],
            "https://oauth2.googleapis.com/token?{{client_id_param}}&{{client_secret_param}}&{{auth_code_param}}&{{redirect_uri_param}}&grant_type=authorization_code",
        ),
        (
            [
                ("set_scheme", "https"),
                ("set_host", "login.microsoftonline.com"),
                ("set_path", "/TENANT_ID/oauth2/v2.0/token"),
                ("add_key_value_placeholder_param", "client_id"),
                ("add_key_value_placeholder_param", "auth_code"),
                ("add_key_value_placeholder_param", "redirect_uri"),
                ("add_key_value_placeholder_param", "client_secret"),
                ("add_literal_param", "grant_type=authorization_code"),
            ],
            "https://login.microsoftonline.com/TENANT_ID/oauth2/v2.0/token?{{client_id_param}}&{{auth_code_param}}&{{redirect_uri_param}}&{{client_secret_param}}&grant_type=authorization_code",
        ),
    ],
)
def test_url_builder_for_key_pair_value_pair(steps, expected_url):
    """
    Demonstrates building a URL in a specified order,
    using a list of (method_name, argument) tuples.
    """

    builder = PlaceholderUrlBuilder()

    # We'll call each builder method in the order given by steps
    for method_name, arg in steps:
        if method_name == "set_scheme":
            builder.set_scheme(arg)
        elif method_name == "set_host":
            builder.set_host(arg)
        elif method_name == "set_path":
            builder.set_path(arg)
        elif method_name == "add_key_value_placeholder_param":
            builder.add_key_value_placeholder_param(arg)
        elif method_name == "add_literal_param":
            builder.add_literal_param(arg)
        else:
            raise ValueError(f"Unknown method_name: {method_name}")

    # Finally, build the URL and compare to expected
    url = builder.build()
    assert url == expected_url, f"Expected {expected_url}, but got {url}"


@pytest.mark.parametrize(
    "site_url, expected_method_call",
    [
        ("https://example.sharepoint.com/sites/test", "get_by_url"),
        (None, "root.get"),
    ],
)
@patch("source_microsoft_sharepoint.utils.execute_query_with_retry")
def test_get_site(mock_execute_query_with_retry, site_url, expected_method_call):
    mock_graph_client = Mock()

    mock_site = Mock(spec=Site)
    mock_site.web_url = "https://example.sharepoint.com/sites/test" if site_url else "https://example.sharepoint.com"

    mock_site.site_collection = Mock()
    mock_site.site_collection.hostname = "example.sharepoint.com"

    mock_site.name = "Test Site"
    mock_site.id = "test-site-id"
    mock_site.root = Mock()

    mock_execute_query_with_retry.return_value = mock_site

    result = get_site(mock_graph_client, site_url)

    if expected_method_call == "get_by_url":
        mock_graph_client.sites.get_by_url.assert_called_once_with(site_url)
    else:
        mock_graph_client.sites.root.get.assert_called_once()

    mock_execute_query_with_retry.assert_called_once()
    assert result

    # Additional assertions to verify the site object's structure is maintained
    assert result.web_url == "https://example.sharepoint.com/sites/test" if site_url else "https://example.sharepoint.com"
    assert result.site_collection.hostname == "example.sharepoint.com"
    assert result.name == "Test Site"


@pytest.mark.parametrize(
    "web_url, hostname, expected_site_url, expected_prefix",
    [
        (
            "https://contoso.sharepoint.com/sites/marketing",
            "contoso.sharepoint.com",
            "https://contoso.sharepoint.com/sites/marketing",
            "contoso",
        ),
        ("https://fabrikam.sharepoint.com", "fabrikam.sharepoint.com", "https://fabrikam.sharepoint.com", "fabrikam"),
        (
            "https://tailwind.sharepoint.com/sites/engineering/dev",
            "tailwind.sharepoint.com",
            "https://tailwind.sharepoint.com/sites/engineering/dev",
            "tailwind",
        ),
    ],
)
def test_get_site_prefix(web_url, hostname, expected_site_url, expected_prefix):
    # Create a mock Site object with the correct spec
    mock_site = Mock(spec=Site)
    mock_site.web_url = web_url
    mock_site.site_collection = Mock()
    mock_site.site_collection.hostname = hostname

    site_url, prefix = get_site_prefix(mock_site)

    assert site_url == expected_site_url
    assert prefix == expected_prefix


def test_get_site_prefix_invalid_hostname():
    # Create a mock Site object with the correct spec
    mock_site = Mock(spec=Site)
    mock_site.web_url = "https://invalid"
    mock_site.site_collection = Mock()
    mock_site.site_collection.hostname = "invalid"

    # Call the function and expect a ValueError
    with pytest.raises(ValueError, match="Invalid host name: invalid"):
        get_site_prefix(mock_site)
