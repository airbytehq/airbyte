import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path

from source_microsoft_onedrive import SourceMicrosoftOneDrive
from source_microsoft_onedrive.spec import SourceMicrosoftOneDriveSpec
from source_microsoft_onedrive.stream_reader import SourceMicrosoftOneDriveStreamReader


def _without_none(value):
    if isinstance(value, dict):
        return {key: _without_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [_without_none(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    return value


def test_spec_matches_expected_spec_json():
    expected_spec = json.loads((Path(__file__).parents[1] / "integration_tests" / "spec.json").read_text())
    actual_spec = SourceMicrosoftOneDrive(catalog=None, config=None, state=None).spec()

    assert actual_spec.connectionSpecification == expected_spec["connectionSpecification"]
    if "advanced_auth" in expected_spec:
        assert _without_none(asdict(actual_spec.advanced_auth)) == expected_spec["advanced_auth"]


def test_unstructured_format_only_has_local_processing_option():
    connection_specification = SourceMicrosoftOneDrive(catalog=None, config=None, state=None).spec().connectionSpecification
    unstructured_format = connection_specification["properties"]["streams"]["items"]["properties"]["format"]["oneOf"][4]

    assert (
        unstructured_format.get("title") == "Unstructured Document Format"
        or unstructured_format.get("properties", {}).get("filetype", {}).get("const") == "unstructured"
    )
    processing_options = unstructured_format["properties"]["processing"]["oneOf"]
    assert len(processing_options) == 1
    assert processing_options[0]["title"] == "Local"


def test_stream_reader_accepts_source_spec_config():
    config = SourceMicrosoftOneDriveSpec(
        credentials={
            "auth_type": "Client",
            "tenant_id": "tenant_id",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "refresh_token": "refresh_token",
        },
        drive_name="OneDrive",
        streams=[{"name": "csv_stream", "format": {"filetype": "csv"}}],
    )
    stream_reader = SourceMicrosoftOneDriveStreamReader()

    stream_reader.config = config

    assert stream_reader.config is config
