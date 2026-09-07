# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Behavioral tests for Apple Ads error handling."""

import json
from pathlib import Path

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CompositeErrorHandler as CompositeErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DefaultErrorHandler as DefaultErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
STREAM_NAMES = [
    "campaigns",
    "adgroups",
    "keywords",
    "campaigns_report_daily",
    "adgroups_report_daily",
    "keywords_report_daily",
    "ads",
    "ads_report_daily",
]
REPORT_STREAM_NAMES = [
    "campaigns_report_daily",
    "adgroups_report_daily",
    "keywords_report_daily",
    "ads_report_daily",
]
OBJECT_STREAM_NAMES = ["campaigns", "adgroups", "keywords", "ads"]
AUTHENTICATION_ERROR_MESSAGE = (
    "Apple Ads API authentication failed. Verify the Client ID, Client Secret, and Organization ID in the source configuration."
)
ACCESS_ERROR_MESSAGE = (
    "Apple Ads API denied access to the requested resource. Verify the API user role and Organization ID in the source configuration."
)


@pytest.fixture(scope="module")
def manifest():
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(MANIFEST_PATH.read_text()))


def _response(status_code, body):
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(body).encode()
    response.headers["Content-Type"] = "application/json"
    return response


def _error_handler(manifest, stream_name):
    definition = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]
    propagated = ManifestComponentTransformer().propagate_types_and_parameters("", definition, {})
    model_cls = CompositeErrorHandlerModel if propagated["type"] == "CompositeErrorHandler" else DefaultErrorHandlerModel
    return ModelToComponentFactory().create_component(model_cls, propagated, config={})


def _apple_error(message):
    return {
        "data": None,
        "pagination": None,
        "error": {
            "errors": [
                {
                    "messageCode": "UNAUTHORIZED",
                    "message": message,
                    "field": "",
                }
            ]
        },
    }


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_expired_token_401_refreshes_token(manifest, stream_name):
    """Expired-token responses refresh the OAuth token."""
    resolution = _error_handler(manifest, stream_name).interpret_response(
        _response(401, _apple_error("Expired Token: 5594b1f4-0000-0000-0000-000000000000"))
    )

    assert resolution.response_action is ResponseAction.REFRESH_TOKEN_THEN_RETRY


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_invalid_token_401_fails_with_configuration_error(manifest, stream_name):
    """Invalid-token responses fail with a configuration error."""
    resolution = _error_handler(manifest, stream_name).interpret_response(
        _response(401, _apple_error("Invalid token: 5594b1f4-0000-0000-0000-000000000000"))
    )

    assert resolution.response_action is ResponseAction.FAIL
    assert resolution.failure_type is FailureType.config_error
    assert resolution.error_message == AUTHENTICATION_ERROR_MESSAGE


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_forbidden_response_fails_with_configuration_error(manifest, stream_name):
    """Forbidden responses fail with a configuration error."""
    resolution = _error_handler(manifest, stream_name).interpret_response(_response(403, _apple_error("Unauthorized resource")))

    assert resolution.response_action is ResponseAction.FAIL
    assert resolution.failure_type is FailureType.config_error
    assert resolution.error_message == ACCESS_ERROR_MESSAGE


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_rate_limit_response_is_rate_limited(manifest, stream_name):
    """Rate-limit responses use the CDK rate-limited action."""
    resolution = _error_handler(manifest, stream_name).interpret_response(_response(429, _apple_error("Too many requests")))

    assert resolution.response_action is ResponseAction.RATE_LIMITED


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
def test_server_errors_are_retried(manifest, stream_name, status_code):
    """Server responses use retry handling."""
    resolution = _error_handler(manifest, stream_name).interpret_response(_response(status_code, _apple_error("Server error")))

    assert resolution.response_action is ResponseAction.RETRY


@pytest.mark.parametrize("status_code", [400, 500])
def test_keywords_report_ignores_missing_keyword_response(manifest, status_code):
    """Missing-keyword responses are ignored for keyword reports."""
    resolution = _error_handler(manifest, "keywords_report_daily").interpret_response(
        _response(status_code, _apple_error("CAMPAIGN DOES NOT CONTAIN KEYWORD"))
    )

    assert resolution.response_action is ResponseAction.IGNORE


@pytest.mark.parametrize("stream_name", REPORT_STREAM_NAMES)
def test_report_streams_have_ten_retries(manifest, stream_name):
    """Report streams retain the higher retry budget."""
    assert _error_handler(manifest, stream_name).max_retries == 10


@pytest.mark.parametrize("stream_name", OBJECT_STREAM_NAMES)
def test_object_streams_use_default_retry_budget(manifest, stream_name):
    """Object streams retain the default retry budget."""
    assert _error_handler(manifest, stream_name).max_retries in (None, 5)


def test_source_builds_and_exposes_eight_streams(manifest):
    """The source accepts the manifest and exposes all streams."""
    config = {
        "org_id": 1,
        "client_id": "client-id",
        "client_secret": "client-secret",
        "start_date": "2025-01-01",
        "timezone": "UTC",
        "token_refresh_endpoint": "https://example.com/token",
        "lookback_window": 30,
        "backoff_factor": 5,
        "num_workers": 2,
    }
    source = ConcurrentDeclarativeSource(source_config=manifest, config=config, catalog=None, state=None)

    assert len(source.streams(config)) == 8


def test_oauth_authenticator_has_token_error_classification(manifest):
    """The OAuth authenticator classifies token endpoint errors."""
    authenticator = manifest["definitions"]["base_requester"]["authenticator"]

    assert authenticator["refresh_token_error_key"] == "error"
    assert 400 in authenticator["refresh_token_error_status_codes"]
    assert "invalid_client" in authenticator["refresh_token_error_values"]
