# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read

# Ancre le chemin du manifest au fichier de test lui-même, au lieu d'un
# chemin relatif "manifest.yaml" qui casse si pytest est lancé depuis un
# autre répertoire de travail (c'était le bug n°3 relevé par le bot).
MANIFEST_PATH = str(Path(__file__).parent.parent / "manifest.yaml")

TEST_CONFIG = {"api_key": "fake-key", "start_date": "2025-01-01"}


def _source() -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=TEST_CONFIG, catalog=None)


def _catalog(stream_name: str):
    return CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()


def test_rcs_messages_stream_extracts_records(requests_mock):
    requests_mock.get(
        "https://rest.smsmode.com/rcs/v1/messages",
        json={"items": [{"messageId": "abc123", "from": "TestSender"}]},
    )
    output = read(_source(), TEST_CONFIG, _catalog("rcs_messages"))
    records = output.records
    assert len(records) == 1
    assert records[0].record.data["messageId"] == "abc123"


def test_consumptions_rcs_stream_extracts_records(requests_mock):
    requests_mock.get(
        "https://rest.smsmode.com/commons/v1/consumptions",
        json={"items": [{"consumptionId": "cons-1", "quantity": 42}]},
    )
    output = read(_source(), TEST_CONFIG, _catalog("consumptions_rcs"))
    records = output.records
    assert len(records) == 1
    assert records[0].record.data["consumptionId"] == "cons-1"


def test_api_key_sent_as_header_on_rcs_messages(requests_mock):
    mock = requests_mock.get("https://rest.smsmode.com/rcs/v1/messages", json={"items": []})
    read(_source(), TEST_CONFIG, _catalog("rcs_messages"))
    assert mock.last_request.headers["X-Api-Key"] == "fake-key"
