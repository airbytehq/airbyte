import base64
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Mapping, Optional

import yaml

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
_RESOURCE_PATH = Path(__file__).parent.parent / "resource"
_BASE_URL = "https://api.qualaroo.com/api/v1/"
_START_DATE = "2021-03-01T00:00:00.000Z"
_AUTHORIZATION = "Basic " + base64.b64encode(b"test_key:test_token").decode("ascii")


def _config(survey_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "key": "test_key",
        "token": "test_token",
        "start_date": _START_DATE,
        "survey_ids": survey_ids or [],
    }


def _catalog(stream_name: str) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()


def _read(stream_name: str, config: Optional[Mapping[str, Any]] = None) -> EntrypointOutput:
    stream_catalog = _catalog(stream_name)
    stream_config = config or _config()
    state = StateBuilder().build()
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text(encoding="utf-8"))
    manifest["concurrency_level"] = {"type": "ConcurrencyLevel", "default_concurrency": 1}
    with TemporaryDirectory() as temporary_directory:
        test_manifest_path = Path(temporary_directory) / "manifest.yaml"
        test_manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        source = YamlDeclarativeSource(
            path_to_yaml=str(test_manifest_path),
            catalog=stream_catalog,
            config=stream_config,
            state=state,
        )
        output = entrypoint_read(source, stream_config, stream_catalog, state)
    output.raise_if_errors()
    return output


def _records(output: EntrypointOutput) -> List[Dict[str, Any]]:
    return [message.record.data for message in output.records]


def _request(path: str) -> HttpRequest:
    return HttpRequest(
        f"{_BASE_URL}{path}?limit=500&start_date={_START_DATE}",
        headers={"Authorization": _AUTHORIZATION},
    )


def _response(filename: str) -> HttpResponse:
    return HttpResponse((_RESOURCE_PATH / "http" / "response" / filename).read_text(encoding="utf-8"))


def _mock_survey_request(http_mocker: HttpMocker, filename: str = "surveys.json") -> HttpRequest:
    request = _request("nudges")
    http_mocker.get(request, _response(filename))
    return request


def _mock_response_requests(
    http_mocker: HttpMocker,
    responses_101: str = "responses_101.json",
    responses_102: str = "responses_102.json",
) -> List[HttpRequest]:
    requests = []
    for survey_id, filename in (("101", responses_101), ("102", responses_102)):
        request = _request(f"nudges/{survey_id}/responses.json")
        http_mocker.get(request, _response(filename))
        requests.append(request)
    return requests


def test_survey_and_response_records_match_legacy_fixtures() -> None:
    for stream_name in ("surveys", "responses"):
        with HttpMocker() as http_mocker:
            survey_request = _mock_survey_request(http_mocker)
            response_requests = _mock_response_requests(http_mocker)
            actual = _records(_read(stream_name))
            expected_path = _RESOURCE_PATH / "expected" / f"{stream_name}.json"
            assert actual == json.loads(expected_path.read_text(encoding="utf-8"))
            http_mocker.assert_number_of_calls(survey_request, 1)
            for request in response_requests:
                http_mocker.assert_number_of_calls(request, 1 if stream_name == "responses" else 0)


def test_authentication_matches_basic_auth_and_legacy_header() -> None:
    legacy_authorization = (_RESOURCE_PATH / "expected" / "legacy_authorization.txt").read_text(encoding="utf-8").strip()
    assert _AUTHORIZATION == "Basic " + base64.b64encode(b"test_key:test_token").decode("ascii")
    assert _AUTHORIZATION == legacy_authorization

    with HttpMocker() as http_mocker:
        request = _mock_survey_request(http_mocker)
        output = _read("surveys")
        assert len(output.records) == 2
        http_mocker.assert_number_of_calls(request, 1)


def test_answered_questions_mappings_preserve_legacy_order_and_missing_fields() -> None:
    with HttpMocker() as http_mocker:
        survey_request = _mock_survey_request(http_mocker)
        response_requests = _mock_response_requests(http_mocker)
        records = _records(_read("responses"))

    first_record = next(record for record in records if record["id"] == 201)
    assert [item["question_id"] for item in first_record["answered_questions"]] == [
        1001,
        1002,
        1003,
        1004,
        1005,
        1006,
    ]
    assert next(record for record in records if record["id"] == 202)["answered_questions"] == []
    assert "answered_questions" not in next(record for record in records if record["id"] == 203)
    assert len(records) == 4
    assert survey_request is not None
    assert len(response_requests) == 2


def test_null_answered_questions_is_preserved_without_failing() -> None:
    with HttpMocker() as http_mocker:
        survey_request = _mock_survey_request(http_mocker)
        response_101_request = _request("nudges/101/responses.json")
        http_mocker.get(response_101_request, _response("responses_null.json"))
        response_102_request = _request("nudges/102/responses.json")
        http_mocker.get(response_102_request, _response("responses_102.json"))

        output = _read("responses")
        records = _records(output)

    null_record = next(record for record in records if record["id"] == 205)
    assert not output.errors
    assert null_record.get("answered_questions") is None
    http_mocker.assert_number_of_calls(survey_request, 1)
    http_mocker.assert_number_of_calls(response_101_request, 1)
    http_mocker.assert_number_of_calls(response_102_request, 1)


def test_survey_ids_filter_requests_only_selected_survey() -> None:
    with HttpMocker() as http_mocker:
        survey_request = _mock_survey_request(http_mocker, "surveys_string_ids.json")
        response_request = _request("nudges/101/responses.json")
        http_mocker.get(response_request, _response("responses_101.json"))

        records = _records(_read("responses", _config(["101"])))

    assert records
    assert {record["nudge_id"] for record in records} == {101}
    http_mocker.assert_number_of_calls(survey_request, 1)
    http_mocker.assert_number_of_calls(response_request, 1)


def test_manifest_and_connector_have_no_custom_components() -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text(encoding="utf-8"))
    component_types = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            component_type = value.get("type")
            if isinstance(component_type, str):
                component_types.append(component_type)
            assert "class_name" not in value
            for nested_value in value.values():
                visit(nested_value)
        elif isinstance(value, list):
            for nested_value in value:
                visit(nested_value)

    visit(manifest)
    assert not any(component_type.startswith("Custom") for component_type in component_types)
    assert not (_SOURCE_FOLDER_PATH / "components.py").exists()
