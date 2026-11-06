# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from dropbox.exceptions import ApiError
from dropbox.files import ListFolderContinueError
from source_dropbox.client import (
    DropboxClient,
    DropboxNamespaceError,
    NamespaceInfo,
)
from source_dropbox.streams.entries import Entries

from airbyte_cdk.models import SyncMode


CONFIG = {
    "credentials": {"auth_type": "access_token", "access_token": "test-token"},
    "path": "/Reports",
    "recursive": True,
}


def _namespace(namespace_id: str, *, name: str | None = None) -> NamespaceInfo:
    return NamespaceInfo(
        namespace_id=namespace_id,
        name=name,
        namespace_type="team_folder",
    )


def _constructed_namespace_client(
    config: dict[str, object],
    *rooted_clients: Mock,
) -> tuple[DropboxClient, Mock]:
    default = Mock()
    default.with_path_root.side_effect = list(rooted_clients)
    with patch(
        "source_dropbox.dropbox_context.dropbox.Dropbox",
        return_value=default,
    ):
        client = DropboxClient(config)
    return client, default


def test_selected_namespace_ids_are_validated_and_sorted() -> None:
    client = DropboxClient.__new__(DropboxClient)
    namespaces = client._resolve_namespaces(
        {
            **CONFIG,
            "namespace_selection": {
                "mode": "selected",
                "namespace_ids": ["456", "123"],
            },
        }
    )

    assert [namespace.namespace_id for namespace in namespaces] == ["123", "456"]

    with pytest.raises(DropboxNamespaceError, match="duplicates"):
        client._resolve_namespaces(
            {
                **CONFIG,
                "namespace_selection": {
                    "mode": "selected",
                    "namespace_ids": ["123", "123"],
                },
            }
        )


def test_all_accessible_discovers_and_normalizes_namespaces() -> None:
    sdk = Mock()
    namespace_type = SimpleNamespace(_tag="team_folder")
    sdk.team_namespaces_list.return_value = SimpleNamespace(
        namespaces=[SimpleNamespace(namespace_id="456", name="B", namespace_type=namespace_type)],
        cursor="next",
        has_more=True,
    )
    sdk.team_namespaces_list_continue.return_value = SimpleNamespace(
        namespaces=[SimpleNamespace(namespace_id="123", name="A", namespace_type=namespace_type)],
        cursor=None,
        has_more=False,
    )
    client = DropboxClient.__new__(DropboxClient)
    client._common_kwargs = {}

    with patch("source_dropbox.client.build_dropbox_team_client", return_value=sdk):
        namespaces = client._list_accessible_namespaces(CONFIG)

    assert [namespace.provenance() for namespace in namespaces] == [
        {"namespace_id": "123", "namespace_name": "A", "namespace_type": "team_folder"},
        {"namespace_id": "456", "namespace_name": "B", "namespace_type": "team_folder"},
    ]


def test_selected_namespaces_traverse_each_rooted_client_once() -> None:
    first = Mock()
    second = Mock()
    first.files_list_folder.return_value = SimpleNamespace(entries=["a"], cursor="cursor-a", has_more=False)
    second.files_list_folder.return_value = SimpleNamespace(entries=["b"], cursor="cursor-b", has_more=False)
    client = DropboxClient.__new__(DropboxClient)
    client._config = {
        **CONFIG,
        "namespace_selection": {"mode": "selected", "namespace_ids": ["456", "123"]},
    }
    client._namespaces = [_namespace("123"), _namespace("456")]
    client._namespace_clients = {"123": first, "456": second}

    pages = list(client.iter_entries(path="/Reports", recursive=True, include_deleted=False))

    assert [(page.namespace.namespace_id, page.entries) for page in pages if page.namespace] == [
        ("123", ["a"]),
        ("456", ["b"]),
    ]
    first.files_list_folder.assert_called_once_with(path="/Reports", recursive=True, include_deleted=False)
    second.files_list_folder.assert_called_once_with(path="/Reports", recursive=True, include_deleted=False)


def test_current_namespace_mode_does_not_discover_business_namespaces() -> None:
    with (
        patch("source_dropbox.dropbox_context.dropbox.Dropbox") as dropbox_client,
        patch("source_dropbox.dropbox_context.dropbox.DropboxTeam") as team_client,
    ):
        client = DropboxClient({**CONFIG, "namespace_selection": {"mode": "current"}})

    assert client.namespaces == []
    assert client.is_multi_namespace is False
    dropbox_client.assert_called_once()
    team_client.assert_not_called()


def test_selected_namespaces_route_operations_to_rooted_clients_without_discovery() -> None:
    rooted_a = Mock()
    rooted_b = Mock()
    rooted_a.files_list_folder.return_value = SimpleNamespace(entries=["a"], cursor="cursor-a", has_more=False)
    rooted_b.files_list_folder.return_value = SimpleNamespace(entries=["b"], cursor="cursor-b", has_more=False)
    with (
        patch("source_dropbox.dropbox_context.dropbox.DropboxTeam") as team_client,
    ):
        client, default = _constructed_namespace_client(
            {
                **CONFIG,
                "namespace_selection": {
                    "mode": "selected",
                    "namespace_ids": ["456", "123"],
                },
            },
            rooted_a,
            rooted_b,
        )

    pages = list(client.iter_entries(path="/Reports", recursive=True, include_deleted=False))

    assert [(page.namespace.namespace_id, page.entries) for page in pages if page.namespace] == [
        ("123", ["a"]),
        ("456", ["b"]),
    ]
    default.files_list_folder.assert_not_called()
    rooted_a.files_list_folder.assert_called_once_with(path="/Reports", recursive=True, include_deleted=False)
    rooted_b.files_list_folder.assert_called_once_with(path="/Reports", recursive=True, include_deleted=False)
    team_client.assert_not_called()


def test_all_accessible_fails_on_namespace_without_stable_id() -> None:
    sdk = Mock()
    sdk.team_namespaces_list.return_value = SimpleNamespace(
        namespaces=[SimpleNamespace(namespace_id=None, name="Broken", namespace_type=None)],
        cursor=None,
        has_more=False,
    )
    client = DropboxClient.__new__(DropboxClient)
    client._common_kwargs = {}

    with patch("source_dropbox.client.build_dropbox_team_client", return_value=sdk):
        with pytest.raises(DropboxNamespaceError, match="stable ID"):
            client._list_accessible_namespaces(CONFIG)


def test_selected_namespace_access_check_fails_for_inaccessible_root() -> None:
    inaccessible = Mock()
    inaccessible.files_list_folder.side_effect = ApiError("request-id", object(), None, None)
    client, default = _constructed_namespace_client(
        {
            **CONFIG,
            "namespace_selection": {
                "mode": "selected",
                "namespace_ids": ["123"],
            },
        },
        inaccessible,
    )

    default.users_get_current_account.return_value = object()
    with pytest.raises(DropboxNamespaceError, match="namespace selection"):
        client.current_account()


def test_multi_namespace_pagination_keeps_cursors_on_each_rooted_client() -> None:
    first = Mock()
    second = Mock()
    first.files_list_folder_continue.return_value = SimpleNamespace(entries=["a1"], cursor="a-next", has_more=True)
    first.files_list_folder_continue.side_effect = [
        first.files_list_folder_continue.return_value,
        SimpleNamespace(entries=["a2"], cursor="a-final", has_more=False),
    ]
    second.files_list_folder_continue.return_value = SimpleNamespace(entries=["b1"], cursor="b-final", has_more=False)
    client, default = _constructed_namespace_client(
        {
            **CONFIG,
            "namespace_selection": {"mode": "selected", "namespace_ids": ["123", "456"]},
        },
        first,
        second,
    )

    pages = list(
        client.iter_entries(
            path="/Reports",
            recursive=True,
            include_deleted=True,
            cursor={"123": "a-saved", "456": "b-saved"},
        )
    )

    assert [(page.namespace.namespace_id if page.namespace else None, page.entries, page.cursor) for page in pages] == [
        ("123", ["a1"], "a-next"),
        ("123", ["a2"], "a-final"),
        ("456", ["b1"], "b-final"),
    ]
    assert first.files_list_folder_continue.call_args_list[0].args == ("a-saved",)
    assert first.files_list_folder_continue.call_args_list[1].args == ("a-next",)
    second.files_list_folder_continue.assert_called_once_with("b-saved")
    default.files_list_folder_continue.assert_not_called()
    first.files_list_folder.assert_not_called()
    second.files_list_folder.assert_not_called()


def test_multi_namespace_cursor_reset_restarts_only_the_reset_namespace() -> None:
    first = Mock()
    second = Mock()
    first.files_list_folder_continue.side_effect = ApiError("request-id", ListFolderContinueError.reset, None, None)
    first.files_list_folder.return_value = SimpleNamespace(entries=["a-replayed"], cursor="a-new", has_more=False)
    second.files_list_folder_continue.return_value = SimpleNamespace(entries=["b-resumed"], cursor="b-next", has_more=False)
    client, default = _constructed_namespace_client(
        {
            **CONFIG,
            "namespace_selection": {"mode": "selected", "namespace_ids": ["123", "456"]},
        },
        first,
        second,
    )

    pages = list(
        client.iter_entries(
            path="/Reports",
            recursive=True,
            include_deleted=True,
            cursor={"123": "a-old", "456": "b-old"},
        )
    )

    assert [(page.namespace.namespace_id if page.namespace else None, page.entries) for page in pages] == [
        ("123", ["a-replayed"]),
        ("456", ["b-resumed"]),
    ]
    first.files_list_folder.assert_called_once_with(path="/Reports", recursive=True, include_deleted=True)
    default.files_list_folder.assert_not_called()
    second.files_list_folder.assert_not_called()


def test_file_property_listing_continues_on_each_namespace_rooted_client() -> None:
    first = Mock()
    second = Mock()
    first.files_list_folder.return_value = SimpleNamespace(entries=["a1"], cursor="a-next", has_more=True)
    first.files_list_folder_continue.return_value = SimpleNamespace(entries=["a2"], cursor="a-final", has_more=False)
    second.files_list_folder.return_value = SimpleNamespace(entries=["b1"], cursor="b-final", has_more=False)
    client, default = _constructed_namespace_client(
        {
            **CONFIG,
            "namespace_selection": {"mode": "selected", "namespace_ids": ["123", "456"]},
        },
        first,
        second,
    )
    default.file_properties_templates_list_for_user.return_value = SimpleNamespace(template_ids=["ptid:contract"])

    pages = list(client.iter_entries_with_property_groups(path="/Reports", recursive=True))

    assert [(page.namespace.namespace_id if page.namespace else None, page.entries) for page in pages] == [
        ("123", ["a1"]),
        ("123", ["a2"]),
        ("456", ["b1"]),
    ]
    default.file_properties_templates_list_for_user.assert_called_once_with()
    default.files_list_folder.assert_not_called()
    assert first.files_list_folder.call_args.kwargs["include_property_groups"].is_filter_some()
    assert second.files_list_folder.call_args.kwargs["include_property_groups"].is_filter_some()
    first.files_list_folder_continue.assert_called_once_with("a-next")
    second.files_list_folder_continue.assert_not_called()


def test_shared_links_paginate_on_each_namespace_rooted_client() -> None:
    first = Mock()
    second = Mock()
    first.sharing_list_shared_links.side_effect = [
        SimpleNamespace(links=["a1"], cursor="a-next", has_more=True),
        SimpleNamespace(links=["a2"], cursor=None, has_more=False),
    ]
    second.sharing_list_shared_links.return_value = SimpleNamespace(links=["b1"], cursor=None, has_more=False)
    client, default = _constructed_namespace_client(
        {
            **CONFIG,
            "namespace_selection": {"mode": "selected", "namespace_ids": ["123", "456"]},
        },
        first,
        second,
    )

    pages = list(client.iter_shared_links())

    assert [(page.namespace.namespace_id if page.namespace else None, page.links) for page in pages] == [
        ("123", ["a1"]),
        ("123", ["a2"]),
        ("456", ["b1"]),
    ]
    assert first.sharing_list_shared_links.call_args_list[0].kwargs == {"cursor": None}
    assert first.sharing_list_shared_links.call_args_list[1].kwargs == {"cursor": "a-next"}
    second.sharing_list_shared_links.assert_called_once_with(cursor=None)
    default.sharing_list_shared_links.assert_not_called()


def test_shared_folder_members_use_the_client_that_discovered_the_folder() -> None:
    first = Mock()
    second = Mock()
    first.sharing_list_folders.return_value = SimpleNamespace(
        entries=[SimpleNamespace(shared_folder_id="sf:a")],
        cursor=None,
    )
    second.sharing_list_folders.return_value = SimpleNamespace(
        entries=[SimpleNamespace(shared_folder_id="sf:b")],
        cursor=None,
    )
    second.sharing_list_folder_members.return_value = SimpleNamespace(
        users=["member"],
        groups=[],
        invitees=[],
        cursor=None,
    )
    client, default = _constructed_namespace_client(
        {
            **CONFIG,
            "namespace_selection": {"mode": "selected", "namespace_ids": ["123", "456"]},
        },
        first,
        second,
    )

    list(client.iter_shared_folders())
    members = list(client.iter_shared_folder_members("sf:b"))

    assert members[0].users == ["member"]
    second.sharing_list_folder_members.assert_called_once_with("sf:b")
    first.sharing_list_folder_members.assert_not_called()
    default.sharing_list_folder_members.assert_not_called()


def test_entries_checkpoint_cursors_are_isolated_by_namespace() -> None:
    client = Mock()
    client.is_multi_namespace = True
    client.context_scope.return_value = {
        "team_mode": "user",
        "selected_member_id": "dbmid:member",
        "path_root_mode": "default",
    }
    stream = Entries(client, CONFIG)
    stream._pages["123:cursor-a"] = (["a"], _namespace("123", name="A"), "cursor-a")
    stream._pages["456:cursor-b"] = (["b"], _namespace("456", name="B"), "cursor-b")

    with patch(
        "source_dropbox.streams.entries.normalize_entry",
        side_effect=[{"entry_key": "a"}, {"entry_key": "b"}],
    ):
        first_records = list(stream.read_records(SyncMode.incremental, stream_slice={"cursor": "123:cursor-a"}))
        assert first_records == [
            {
                "entry_key": "123:a",
                "namespace_id": "123",
                "namespace_name": "A",
                "namespace_type": "team_folder",
            }
        ]
        second_records = list(stream.read_records(SyncMode.incremental, stream_slice={"cursor": "456:cursor-b"}))
        assert second_records == [
            {
                "entry_key": "456:b",
                "namespace_id": "456",
                "namespace_name": "B",
                "namespace_type": "team_folder",
            }
        ]

    assert stream.state["namespaces"] == {
        "123": {"cursor": "cursor-a"},
        "456": {"cursor": "cursor-b"},
    }
