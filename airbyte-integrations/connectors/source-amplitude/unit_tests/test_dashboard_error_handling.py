# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONNECTOR_DIR = Path(__file__).parent.parent
sys.path.append(str(_CONNECTOR_DIR))

_MANIFEST_PATH = _CONNECTOR_DIR / "manifest.yaml"
_ANNOTATIONS_REQUEST = HttpRequest(url="https://amplitude.com/api/2/annotations")
_CONFIG = {
    "api_key": "an-api-key",
    "secret_key": "a-secret-key",
    "start_date": "2024-01-01T00:00:00Z",
}


def _read_annotations(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("annotations", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(config=_CONFIG, catalog=catalog, state=None, path_to_yaml=str(_MANIFEST_PATH))
    return read(source, _CONFIG, catalog, None, expecting_exception)


class DashboardErrorHandlingTest(TestCase):
    @HttpMocker()
    def test_given_400_when_read_then_config_error_with_amplitude_message(self, http_mocker: HttpMocker) -> None:
        # The body Amplitude returned in airbytehq/airbyte#46712.
        body = {
            "error": {
                "http_code": 400,
                "type": "invalid",
                "message": "Invalid chart definition",
                "metadata": {"details": "Invalid user property country"},
            }
        }
        http_mocker.get(_ANNOTATIONS_REQUEST, HttpResponse(json.dumps(body), status_code=400))

        output = _read_annotations(expecting_exception=True)

        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert output.errors[0].trace.error.message == (
            "Amplitude rejected the request (HTTP 400): Invalid chart definition (Invalid user property country)"
        )

    @HttpMocker()
    def test_given_504_when_read_then_retried(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _ANNOTATIONS_REQUEST,
            [HttpResponse("Gateway Timeout", status_code=504), HttpResponse(json.dumps({"data": [{"id": 1, "label": "release"}]}))],
        )

        with patch("time.sleep"):  # skip the retry backoff
            output = _read_annotations()

        assert not output.errors
        assert [message.record.data["id"] for message in output.records] == [1]
