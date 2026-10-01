# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Iterable
from unittest.mock import Mock, patch

import pytest
from source_dropbox.client import DropboxClient, DropboxCursorResetError, DropboxPage
from source_dropbox.source import SourceDropbox
from source_dropbox.streams.entries import Entries

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
    Type,
)
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


CONFIG = {
    "credentials": {
        "auth_type": "access_token",
        "access_token": "test-token",
    }
}
ENTRIES_SCHEMA = {
    "type": "object",
    "additionalProperties": True,
    "properties": {"entry_key": {"type": "string"}},
}


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="entries",
                    json_schema=ENTRIES_SCHEMA,
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=sync_mode,
                destination_sync_mode=DestinationSyncMode.append,
                cursor_field=[],
            )
        ]
    )


def _state(cursor: str) -> list[AirbyteStateMessage]:
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="entries"),
                stream_state=AirbyteStateBlob(cursor=cursor),
            ),
        )
    ]


def _run_source(
    pages: Iterable[DropboxPage],
    sync_mode: SyncMode,
    normalize_side_effect: object,
    state: list[AirbyteStateMessage] | None = None,
) -> tuple[list[object], Mock]:
    client = Mock()
    client.iter_entries.return_value = pages

    with (
        patch("source_dropbox.source.DropboxClient", return_value=client),
        patch("source_dropbox.streams.entries.normalize_entry", side_effect=normalize_side_effect),
    ):
        messages = list(
            SourceDropbox().read(
                logger=Mock(),
                config=CONFIG,
                catalog=_catalog(sync_mode),
                state=state,
            )
        )
    return messages, client


def _records(messages: Iterable[object]) -> list[dict[str, object]]:
    return [message.record.data for message in messages if message.type == Type.RECORD]  # type: ignore[union-attr]


def _stream_states(messages: Iterable[object]) -> list[dict[str, object]]:
    return [
        vars(message.state.stream.stream_state)  # type: ignore[union-attr]
        for message in messages
        if message.type == Type.STATE and message.state.stream
    ]


def test_full_refresh_protocol_emits_page_state_without_cursor_records() -> None:
    page = DropboxPage(entries=[Mock()], cursor="full-page", has_more=False)

    messages, client = _run_source([page], SyncMode.full_refresh, [{"entry_key": "file:1"}])

    assert _records(messages) == [{"entry_key": "file:1"}]
    assert _stream_states(messages) == [{"cursor": "full-page"}]
    client.iter_entries.assert_called_once_with(path="", recursive=True, include_deleted=True, cursor=None)


def test_full_refresh_ignores_a_saved_cursor_and_starts_from_root() -> None:
    page = DropboxPage(entries=[Mock()], cursor="full-page", has_more=False)
    client = DropboxClient.__new__(DropboxClient)
    client.list_folder = Mock(return_value=page)
    client.list_folder_continue = Mock()

    with (
        patch("source_dropbox.source.DropboxClient", return_value=client),
        patch(
            "source_dropbox.streams.entries.normalize_entry",
            return_value={"entry_key": "file:1"},
        ),
    ):
        messages = list(
            SourceDropbox().read(
                logger=Mock(),
                config=CONFIG,
                catalog=_catalog(SyncMode.full_refresh),
                state=_state("saved-page"),
            )
        )

    assert _records(messages) == [{"entry_key": "file:1"}]
    assert _stream_states(messages) == [{"cursor": "full-page"}]
    client.list_folder.assert_called_once_with("", True, True)
    client.list_folder_continue.assert_not_called()


def test_next_full_refresh_ignores_a_prior_full_refresh_checkpoint() -> None:
    first_page = DropboxPage(entries=[Mock()], cursor="first-full-page", has_more=False)
    first_messages, _ = _run_source([first_page], SyncMode.full_refresh, [{"entry_key": "file:1"}])
    prior_state = [message.state for message in first_messages if message.type == Type.STATE]
    second_page = DropboxPage(entries=[Mock()], cursor="second-full-page", has_more=False)

    _, second_client = _run_source([second_page], SyncMode.full_refresh, [{"entry_key": "file:2"}], prior_state)

    second_client.iter_entries.assert_called_once_with(path="", recursive=True, include_deleted=True, cursor=None)


def test_incremental_protocol_uses_saved_state_and_emits_page_state() -> None:
    page = DropboxPage(entries=[Mock()], cursor="next-page", has_more=False)

    messages, client = _run_source([page], SyncMode.incremental, [{"entry_key": "file:1"}], _state("saved-page"))

    assert _records(messages) == [{"entry_key": "file:1"}]
    assert _stream_states(messages) == [{"cursor": "next-page"}]
    client.iter_entries.assert_called_once_with(path="", recursive=True, include_deleted=True, cursor="saved-page")


def test_protocol_does_not_advance_cursor_after_mid_page_failure() -> None:
    page = DropboxPage(entries=[Mock(), Mock()], cursor="page-one", has_more=False)
    client = Mock()
    client.iter_entries.return_value = [page]
    messages: list[object] = []

    with (
        patch("source_dropbox.source.DropboxClient", return_value=client),
        patch(
            "source_dropbox.streams.entries.normalize_entry",
            side_effect=[{"entry_key": "file:1"}, RuntimeError("normalization failed")],
        ),
        pytest.raises(AirbyteTracedException),
    ):
        for message in SourceDropbox().read(
            logger=Mock(),
            config=CONFIG,
            catalog=_catalog(SyncMode.incremental),
            state=_state("saved-page"),
        ):
            messages.append(message)

    assert _records(messages) == [{"entry_key": "file:1"}]
    assert _stream_states(messages) == []


def test_protocol_keeps_first_page_checkpoint_when_second_page_fails() -> None:
    first_page = DropboxPage(entries=[Mock()], cursor="page-one", has_more=True)
    second_page = DropboxPage(entries=[Mock()], cursor="page-two", has_more=False)
    client = Mock()
    client.iter_entries.return_value = [first_page, second_page]
    messages: list[object] = []

    with (
        patch("source_dropbox.source.DropboxClient", return_value=client),
        patch(
            "source_dropbox.streams.entries.normalize_entry",
            side_effect=[{"entry_key": "file:1"}, RuntimeError("normalization failed")],
        ),
        pytest.raises(AirbyteTracedException),
    ):
        for message in SourceDropbox().read(
            logger=Mock(),
            config=CONFIG,
            catalog=_catalog(SyncMode.incremental),
            state=_state("saved-page"),
        ):
            messages.append(message)

    assert _records(messages) == [{"entry_key": "file:1"}]
    assert _stream_states(messages) == [{"cursor": "page-one"}]


def test_empty_page_emits_a_state_message() -> None:
    page = DropboxPage(entries=[], cursor="empty-page", has_more=False)

    messages, _ = _run_source([page], SyncMode.incremental, [], _state("saved-page"))

    assert _records(messages) == []
    assert _stream_states(messages) == [{"cursor": "empty-page"}]


def test_normalization_failure_releases_page_cache() -> None:
    stream = Entries(Mock(), CONFIG)
    stream._pages["page-one"] = [Mock()]

    with (
        patch(
            "source_dropbox.streams.entries.normalize_entry",
            side_effect=RuntimeError("normalization failed"),
        ),
        pytest.raises(RuntimeError, match="normalization failed"),
    ):
        list(stream.read_records(SyncMode.incremental, stream_slice={"cursor": "page-one"}))

    assert stream._pages == {}
    assert stream.state == {}


def test_entries_state_rejects_changed_resolved_root_namespace() -> None:
    client = Mock()
    client.context_scope.return_value = {
        "team_mode": "user",
        "selected_member_id": "dbmid:member",
        "path_root_mode": "root",
        "namespace_id": "222",
    }
    stream = Entries(client, CONFIG)

    with pytest.raises(ValueError, match="context does not match"):
        stream.state = {
            "cursor": "saved",
            "context": {
                "team_mode": "user",
                "selected_member_id": "dbmid:member",
                "path_root_mode": "root",
                "namespace_id": "111",
            },
        }


def test_cursor_reset_restart_is_reflected_in_airbyte_messages() -> None:
    page = DropboxPage(entries=[Mock()], cursor="fresh-page", has_more=False)
    client = DropboxClient.__new__(DropboxClient)
    client.list_folder_continue = Mock(side_effect=DropboxCursorResetError("reset"))
    client.list_folder = Mock(return_value=page)

    with (
        patch("source_dropbox.source.DropboxClient", return_value=client),
        patch(
            "source_dropbox.streams.entries.normalize_entry",
            return_value={"entry_key": "file:1"},
        ),
    ):
        messages = list(
            SourceDropbox().read(
                logger=Mock(),
                config=CONFIG,
                catalog=_catalog(SyncMode.incremental),
                state=_state("invalidated-page"),
            )
        )

    assert _records(messages) == [{"entry_key": "file:1"}]
    assert _stream_states(messages) == [{"cursor": "fresh-page"}]
    client.list_folder_continue.assert_called_once_with("invalidated-page")
    client.list_folder.assert_called_once_with("", True, True)
