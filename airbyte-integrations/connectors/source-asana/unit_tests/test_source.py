#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_asana.source import SourceAsana


def test_oauth_connector_input_specification_includes_default_scope():
    source = SourceAsana(catalog=None, config=None, state=None)

    spec = source.spec(None)
    oauth_spec = spec.advanced_auth.oauth_config_specification.oauth_connector_input_specification

    assert oauth_spec.scopes == [{"scope": "default"}]


@pytest.mark.parametrize(
    "filter_index, expected_filter",
    [
        pytest.param(
            0,
            {
                "action": "REFRESH_TOKEN_THEN_RETRY",
                "predicate": "{{ config.get('credentials', {}).get('option_title') == 'OAuth Credentials' }}",
                "failure_type": "transient_error",
                "error_message": "Asana access token is expired.",
            },
            id="oauth_401_refreshes_token",
        ),
        pytest.param(
            1,
            {
                "action": "FAIL",
                "failure_type": "config_error",
                "error_message": "Asana credentials are invalid. Verify the credentials in your source configuration.",
            },
            id="pat_401_fails",
        ),
    ],
)
def test_401_error_handler_by_auth_type(filter_index, expected_filter):
    source = SourceAsana(catalog=None, config=None, state=None)
    manifest = source._read_and_parse_yaml_file(source._path_to_yaml)

    response_filters = manifest["definitions"]["requester"]["error_handler"]["response_filters"]
    auth_filters = [response_filter for response_filter in response_filters if 401 in response_filter.get("http_codes", [])]

    assert len(auth_filters) == 2
    assert auth_filters[filter_index] == {
        "type": "HttpResponseFilter",
        "http_codes": [401],
        **expected_filter,
    }
