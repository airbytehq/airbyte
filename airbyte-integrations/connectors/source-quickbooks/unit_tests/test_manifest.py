# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for source-quickbooks manifest.yaml.

Covers the two places where a misconfiguration is silent rather than loud: an
error filter that can never match Intuit's payload shape, and refresh-token
rejections that reach the user as a generic authentication failure.
"""

from pathlib import Path

import jinja2
import pytest
import yaml


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"

TOKEN_REFRESH_ENDPOINT = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


@pytest.fixture(scope="module")
def response_filters(manifest):
    return manifest["definitions"]["error_handler"]["response_filters"]


def _eval_predicate(predicate, response):
    rendered = jinja2.Environment().from_string(predicate).render(response=response)
    return rendered.strip() == "True"


def _iter_authenticators(node):
    if isinstance(node, dict):
        if node.get("type") == "OAuthAuthenticator":
            yield node
        for value in node.values():
            yield from _iter_authenticators(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_authenticators(value)


def _fault_predicates(response_filters):
    return [f["predicate"] for f in response_filters if "predicate" in f]


def test_every_stream_shares_the_error_handler(manifest):
    stream_names = {stream["name"] for stream in manifest["streams"]}
    assert len(stream_names) == 28
    for stream in manifest["streams"]:
        error_handler = stream["retriever"]["requester"]["error_handler"]
        assert error_handler["$ref"] == "#/definitions/error_handler", stream["name"]


def test_fault_code_filters_do_not_use_error_message_contains(response_filters):
    """`error_message_contains` is matched against JsonErrorMessageParser output, which
    never sees Intuit's `Fault.Error[0].code`, so a substring match silently never fires."""
    assert not any("error_message_contains" in f for f in response_filters)


def test_two_fault_code_predicates_precede_the_status_filters(response_filters):
    predicate_indexes = [i for i, f in enumerate(response_filters) if "predicate" in f]
    status_indexes = [i for i, f in enumerate(response_filters) if "http_codes" in f]
    assert predicate_indexes == [0, 1]
    assert min(status_indexes) > max(predicate_indexes)


@pytest.mark.parametrize(
    "response,expected",
    [
        ({"Fault": {"Error": [{"Message": "message", "code": "3200"}], "type": "AUTHENTICATION"}}, [True, False]),
        ({"Fault": {"Error": [{"code": "003200"}]}}, [True, False]),
        ({"Fault": {"Error": [{"code": "3201"}]}}, [False, True]),
        ({"fault": {"error": [{"code": "003201"}]}}, [False, True]),
        ({"Fault": {"Error": [{"code": "5010"}]}}, [False, False]),
        ({"Fault": {"Error": []}}, [False, False]),
        ({"QueryResponse": {"Account": [{"Id": "3200"}], "maxResults": 3200}}, [False, False]),
        ({}, [False, False]),
        ([{"Id": "1"}], [False, False]),
    ],
)
def test_fault_code_predicates(response_filters, response, expected):
    predicates = _fault_predicates(response_filters)
    assert [_eval_predicate(p, response) for p in predicates] == expected


def test_fault_code_filters_fail_as_config_error(response_filters):
    for response_filter in response_filters[:2]:
        assert response_filter["action"] == "FAIL"
        assert response_filter["failure_type"] == "config_error"
        assert response_filter["error_message"]


def test_terminal_and_retryable_status_codes(response_filters):
    terminal = {
        code
        for f in response_filters
        if f.get("action") == "FAIL" and f.get("failure_type") == "config_error"
        for code in f.get("http_codes", [])
    }
    retryable = {code for f in response_filters if f.get("action") == "RETRY" for code in f.get("http_codes", [])}
    assert terminal == {401, 403, 404}
    assert retryable == {429, 500, 502, 503, 504}


def test_no_catch_all_filter(response_filters):
    """A catch-all would match HTTP 200s, which predicates are also evaluated against."""
    for response_filter in response_filters:
        assert response_filter.get("http_codes") or response_filter.get("predicate")


def test_every_authenticator_classifies_refresh_token_rejection(manifest):
    authenticators = list(_iter_authenticators(manifest))
    assert len(authenticators) == 57
    for authenticator in authenticators:
        assert authenticator["token_refresh_endpoint"] == TOKEN_REFRESH_ENDPOINT
        assert authenticator["refresh_token_error_status_codes"] == [400, 401]
        assert authenticator["refresh_token_error_key"] == "error"
        assert authenticator["refresh_token_error_values"] == ["invalid_grant", "invalid_client"]
