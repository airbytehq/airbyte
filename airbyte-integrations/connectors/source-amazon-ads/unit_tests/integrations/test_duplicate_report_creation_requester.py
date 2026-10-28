# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Mapping, Optional
from unittest.mock import patch

import pytest
import requests_mock
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomRequester as CustomRequesterModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


_MANIFEST_PATH = Path(__file__).parent.parent.parent / "manifest.yaml"
_STREAM_NAME = "sponsored_brands_v3_report_stream"
_CONFIG = {
    "client_id": "amzn.app-oa2-client.test",
    "client_secret": "test-secret",
    "refresh_token": "test-refresh-token",
    "region": "NA",
}
_STREAM_SLICE = StreamSlice(partition={"profileId": 1}, cursor_slice={"start_time": "2026-10-01", "end_time": "2026-10-05"})


def _creation_requester(factory: ModelToComponentFactory, requester_changes: Optional[Mapping[str, Any]] = None) -> Any:
    """Build a report stream's `creation_requester` from the manifest the way the CDK does."""
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_MANIFEST_PATH.read_text()))
    definition = manifest["definitions"]["streams"][_STREAM_NAME]["retriever"]["creation_requester"]
    definition["requester"] = {**definition["requester"], **(requester_changes or {})}
    definition = ManifestComponentTransformer().propagate_types_and_parameters("", definition, {})
    return factory.create_component(CustomRequesterModel, definition, _CONFIG, name=f"job creation - {_STREAM_NAME}")


def test_nested_requesters_keep_the_factory_settings_for_test_reads() -> None:
    """Connector Builder test reads build components with retries disabled and with the message repository
    that carries the request and response log. Both must reach the requests this component sends."""
    message_repository = InMemoryMessageRepository()
    requester = _creation_requester(ModelToComponentFactory(disable_retries=True, message_repository=message_repository))

    for nested_requester in (requester.requester, requester.report_requester):
        assert isinstance(nested_requester, HttpRequester)
        assert nested_requester.disable_retries is True
        assert nested_requester.message_repository is message_repository


def test_every_kind_of_request_option_reaches_the_report_creation_request() -> None:
    """Any request option HttpRequester supports must reach the report creation POST, not only the headers
    and JSON body the stream definitions use today."""
    requester = _creation_requester(ModelToComponentFactory(), {"request_parameters": {"profile": "{{ stream_partition['profileId'] }}"}})

    assert requester.get_request_params(stream_slice=_STREAM_SLICE) == {"profile": "1"}
    assert str(requester.get_request_headers(stream_slice=_STREAM_SLICE)["Amazon-Advertising-API-Scope"]) == "1"
    request_body = requester.get_request_body_json(stream_slice=_STREAM_SLICE)
    assert request_body["startDate"] == "2026-10-01"
    assert request_body["configuration"]["reportTypeId"] == "sbPurchasedProduct"


def test_given_retries_disabled_when_425_names_no_report_then_fails_without_waiting(requests_mock: requests_mock.Mocker) -> None:
    """Test reads disable retries so they fail fast. Waiting to request a duplicate report again would
    undo that."""
    requests_mock.post("https://api.amazon.com/auth/o2/token", json={"access_token": "test-access-token", "expires_in": 3600})
    requests_mock.post(
        "https://advertising-api.amazon.com/reporting/reports",
        status_code=425,
        json={"code": "425", "detail": "Too early"},
    )
    requester = _creation_requester(ModelToComponentFactory(disable_retries=True))

    with patch("time.sleep") as sleep, pytest.raises(AirbyteTracedException) as raised:
        requester.send_request(stream_slice=_STREAM_SLICE)

    assert raised.value.failure_type == FailureType.transient_error
    sleep.assert_not_called()
    creation_calls = [r for r in requests_mock.request_history if r.method == "POST" and r.url.endswith("/reporting/reports")]
    assert len(creation_calls) == 1
