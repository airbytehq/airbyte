import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

from packaging.specifiers import SpecifierSet
from source_couchbase.source import SourceCouchbase


try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from airbyte_cdk.entrypoint import launch
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode, Type


def test_pyproject_python_constraint_supports_base_image_python():
    pyproject = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
    python_constraint = pyproject["tool"]["poetry"]["dependencies"]["python"]

    assert "3.13" in SpecifierSet(python_constraint)


def test_spec_via_cdk_entrypoint(capsys):
    launch(SourceCouchbase(), ["spec"])

    spec = json.loads(capsys.readouterr().out)

    assert spec["type"] == "SPEC"
    assert {"connection_string", "username", "password", "bucket"} <= set(spec["spec"]["connectionSpecification"]["properties"])


def test_incremental_read_through_abstract_source_emits_state():
    config = {"connection_string": "couchbase://localhost", "username": "user", "password": "password", "bucket": "travel-sample"}
    cluster = MagicMock()
    scope = MagicMock()
    scope.name = "inventory"
    collection = MagicMock()
    collection.name = "hotel"
    cluster.bucket.return_value.collections.return_value.get_all_scopes.return_value = [scope]
    scope.collections = [collection]
    cluster.query.return_value = [
        {"_id": "a", "_ab_cdc_updated_at": 100, "hotel": {"name": "first"}},
        {"_id": "b", "_ab_cdc_updated_at": 200, "hotel": {"name": "second"}},
    ]
    source = SourceCouchbase()

    with patch.object(SourceCouchbase, "_get_cluster", return_value=cluster), patch.object(SourceCouchbase, "_ensure_primary_index"):
        stream = source.streams(config)[0]
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(
                        name=stream.name,
                        json_schema=stream.get_json_schema(),
                        supported_sync_modes=[SyncMode.incremental],
                        source_defined_cursor=True,
                        default_cursor_field=[stream.cursor_field],
                    ),
                    sync_mode=SyncMode.incremental,
                    destination_sync_mode=DestinationSyncMode.append,
                    cursor_field=[stream.cursor_field],
                )
            ]
        )
        messages = list(source.read(logging.getLogger("test"), config, catalog, state=[]))

    records = [message for message in messages if message.type == Type.RECORD]
    states = [message for message in messages if message.type == Type.STATE]

    assert len(records) == 2
    assert states
    assert states[-1].state.stream.stream_state._ab_cdc_updated_at == 200
