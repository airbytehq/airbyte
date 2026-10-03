# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from unittest.mock import Mock, patch

from source_dropbox.client import DropboxPage
from source_dropbox.source import SourceDropbox

from airbyte_cdk.models import SyncMode


CONFIG = {
    "credentials": {
        "auth_type": "access_token",
        "access_token": "test-token",
    }
}


def test_check_connection_success() -> None:
    with patch("source_dropbox.source.DropboxClient") as client_cls:
        client_cls.return_value.current_account.return_value = Mock()
        ok, error = SourceDropbox().check_connection(Mock(), CONFIG)

    assert ok is True
    assert error is None


def test_check_connection_failure() -> None:
    with patch("source_dropbox.source.DropboxClient") as client_cls:
        client_cls.return_value.current_account.side_effect = RuntimeError("bad token")
        ok, error = SourceDropbox().check_connection(Mock(), CONFIG)

    assert ok is False
    assert "bad token" in error


def test_streams_expose_entries_and_snapshots() -> None:
    with patch("source_dropbox.source.DropboxClient"):
        streams = SourceDropbox().streams(CONFIG)

    assert [stream.name for stream in streams] == [
        "entries",
        "files",
        "folders",
        "file_properties",
        "shared_links",
        "shared_folders",
        "sharing_acl",
    ]
    assert streams[0].supports_incremental is True
    assert "cursor" not in streams[0].get_json_schema()["properties"]


def test_entries_checkpoints_only_after_complete_pages() -> None:
    first_entry = Mock()
    second_entry = Mock()
    first_page = DropboxPage(entries=[first_entry], cursor="first-cursor", has_more=True)
    second_page = DropboxPage(entries=[second_entry], cursor="second-cursor", has_more=False)
    client = Mock()
    client.iter_entries.return_value = [first_page, second_page]

    with (
        patch("source_dropbox.source.DropboxClient", return_value=client),
        patch(
            "source_dropbox.streams.entries.normalize_entry",
            side_effect=[{"entry_key": "file:1"}, {"entry_key": "file:2"}],
        ),
    ):
        stream = SourceDropbox().streams(CONFIG)[0]
        stream.state = {"cursor": "saved"}
        configured_stream = Mock(sync_mode=SyncMode.incremental, cursor_field=[])
        configured_stream.stream.json_schema = stream.get_json_schema()
        slice_logger = Mock()
        slice_logger.should_log_slice_message.return_value = False
        internal_config = Mock()
        internal_config.is_limit_reached.return_value = False
        with patch.object(
            stream,
            "_checkpoint_state",
            side_effect=lambda state, **_: {"checkpoint": state},
        ):
            events = list(
                stream.read(
                    configured_stream=configured_stream,
                    logger=Mock(),
                    slice_logger=slice_logger,
                    stream_state={"cursor": "saved"},
                    state_manager=Mock(),
                    internal_config=internal_config,
                )
            )

    assert events == [
        {"entry_key": "file:1"},
        {"checkpoint": {"cursor": "first-cursor"}},
        {"entry_key": "file:2"},
        {"checkpoint": {"cursor": "second-cursor"}},
    ]
    client.iter_entries.assert_called_once_with(path="", recursive=True, include_deleted=True, cursor="saved")


def test_entries_checkpoints_an_empty_page() -> None:
    client = Mock()
    client.iter_entries.return_value = [DropboxPage(entries=[], cursor="empty-cursor", has_more=False)]

    with patch("source_dropbox.source.DropboxClient", return_value=client):
        stream = SourceDropbox().streams(CONFIG)[0]
        configured_stream = Mock(sync_mode=SyncMode.full_refresh, cursor_field=[])
        configured_stream.stream.json_schema = stream.get_json_schema()
        slice_logger = Mock()
        slice_logger.should_log_slice_message.return_value = False
        internal_config = Mock()
        internal_config.is_limit_reached.return_value = False
        with patch.object(stream, "_checkpoint_state", return_value={"checkpoint": "empty-cursor"}):
            events = list(
                stream.read(
                    configured_stream=configured_stream,
                    logger=Mock(),
                    slice_logger=slice_logger,
                    stream_state={},
                    state_manager=Mock(),
                    internal_config=internal_config,
                )
            )

    assert events == [{"checkpoint": "empty-cursor"}]


def test_entries_does_not_advance_state_when_the_cdk_stops_mid_page() -> None:
    first_entry = Mock()
    second_entry = Mock()
    page = DropboxPage(entries=[first_entry, second_entry], cursor="page-cursor", has_more=False)
    client = Mock()
    client.iter_entries.return_value = [page]

    with (
        patch("source_dropbox.source.DropboxClient", return_value=client),
        patch(
            "source_dropbox.streams.entries.normalize_entry",
            side_effect=[{"entry_key": "file:1"}, {"entry_key": "file:2"}],
        ),
    ):
        stream = SourceDropbox().streams(CONFIG)[0]
        stream.state = {"cursor": "saved"}
        configured_stream = Mock(sync_mode=SyncMode.incremental, cursor_field=[])
        configured_stream.stream.json_schema = stream.get_json_schema()
        slice_logger = Mock()
        slice_logger.should_log_slice_message.return_value = False
        internal_config = Mock()
        internal_config.is_limit_reached.return_value = True
        with patch.object(
            stream,
            "_checkpoint_state",
            side_effect=lambda state, **_: {"checkpoint": state},
        ):
            events = list(
                stream.read(
                    configured_stream=configured_stream,
                    logger=Mock(),
                    slice_logger=slice_logger,
                    stream_state={"cursor": "saved"},
                    state_manager=Mock(),
                    internal_config=internal_config,
                )
            )

    assert events == [{"entry_key": "file:1"}, {"checkpoint": {"cursor": "saved"}}]
    assert stream.state == {"cursor": "saved"}


def test_spec_declares_supported_authentication_shapes() -> None:
    spec_path = Path(__file__).parents[1] / "source_dropbox" / "spec.json"
    spec = json.loads(spec_path.read_text())
    credentials = spec["connectionSpecification"]["properties"]["credentials"]

    assert spec["connectionSpecification"]["required"] == ["credentials"]
    assert {item["properties"]["auth_type"]["const"] for item in credentials["oneOf"]} == {
        "oauth2_pkce",
        "access_token",
    }
    oauth = next(item for item in credentials["oneOf"] if item["properties"]["auth_type"]["const"] == "oauth2_pkce")
    access_token = next(item for item in credentials["oneOf"] if item["properties"]["auth_type"]["const"] == "access_token")
    assert oauth["properties"]["refresh_token"]["airbyte_secret"] is True
    assert access_token["properties"]["access_token"]["airbyte_secret"] is True
