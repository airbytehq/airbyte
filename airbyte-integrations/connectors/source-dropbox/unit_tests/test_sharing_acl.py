# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from dropbox.exceptions import ApiError, AuthError, BadInputError, RateLimitError
from dropbox.sharing import (
    AccessLevel,
    GroupInfo,
    GroupMembershipInfo,
    InviteeInfo,
    InviteeMembershipInfo,
    ListFolderMembersContinueError,
    SharedFolderMembers,
    SharedFolderMetadata,
    UserInfo,
    UserMembershipInfo,
)
from jsonschema import Draft7Validator
from source_dropbox.client import (
    DropboxAuthenticationError,
    DropboxClient,
    DropboxRateLimitError,
    DropboxSharingAclError,
    DropboxSharingPermissionError,
    SharedFolderMembersPage,
    SharedFoldersPage,
)
from source_dropbox.source import SourceDropbox
from source_dropbox.streams.sharing_acl import SharingAcl

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)


CONFIG = {"credentials": {"auth_type": "access_token", "access_token": "test-token"}}
SCOPED_CONFIG = {**CONFIG, "path": "/Reports"}
ACCOUNT_ID = "dbid:" + "a" * 35
OTHER_ACCOUNT_ID = "dbid:" + "b" * 35


def _schema() -> dict[str, object]:
    path = Path(__file__).parents[1] / "source_dropbox" / "schemas" / "sharing_acl.json"
    return json.loads(path.read_text())


def _folder(
    *,
    shared_folder_id: str = "sf:reports",
    path_lower: str | None = "/reports",
    path_display: str | None = "/Reports",
) -> SharedFolderMetadata:
    return SharedFolderMetadata(
        shared_folder_id=shared_folder_id,
        name="Reports",
        path_lower=path_lower,
        path_display=path_display,
    )


def _user_member(
    *,
    account_id: str = ACCOUNT_ID,
    email: str = "user@example.com",
    same_team: bool | None = True,
    access_type: AccessLevel = AccessLevel.editor,
    inherited: bool | None = False,
) -> UserMembershipInfo:
    return UserMembershipInfo(
        access_type=access_type,
        user=UserInfo(
            account_id=account_id,
            email=email,
            display_name="Example User",
            same_team=same_team,
        ),
        is_inherited=inherited,
    )


def _user_member_without_identity() -> UserMembershipInfo:
    return UserMembershipInfo(
        access_type=AccessLevel.viewer,
        user=UserInfo(display_name="No Identity"),
        is_inherited=False,
    )


def _group_member() -> GroupMembershipInfo:
    return GroupMembershipInfo(
        access_type=AccessLevel.viewer,
        group=GroupInfo(group_id="g:engineering", group_name="Engineering", same_team=False),
        is_inherited=True,
    )


def _group_member_without_identity() -> GroupMembershipInfo:
    return GroupMembershipInfo(
        access_type=AccessLevel.viewer,
        group=GroupInfo(group_name="No Identity Group"),
        is_inherited=False,
    )


def _invitee_member() -> InviteeMembershipInfo:
    return InviteeMembershipInfo(
        access_type=AccessLevel.viewer_no_comment,
        invitee=InviteeInfo.email("invitee@example.com"),
        is_inherited=None,
    )


def _invitee_member_without_identity() -> InviteeMembershipInfo:
    return InviteeMembershipInfo(
        access_type=AccessLevel.viewer,
        invitee=InviteeInfo.other,
        is_inherited=False,
    )


def test_sharing_acl_normalizes_user_membership_and_schema() -> None:
    client = Mock()
    client.iter_shared_folders.return_value = [SharedFoldersPage(entries=[_folder()], cursor=None)]
    client.iter_shared_folder_members.return_value = [SharedFolderMembersPage(users=[_user_member()], groups=[], invitees=[], cursor=None)]

    records = list(SharingAcl(client, SCOPED_CONFIG).read_records(SyncMode.full_refresh))

    assert records == [
        {
            "acl_key": f"sf:reports|user|{ACCOUNT_ID}",
            "resource_id": "sf:reports",
            "resource_type": "shared_folder",
            "path_lower": "/reports",
            "path_display": "/Reports",
            "principal_type": "user",
            "principal_id": ACCOUNT_ID,
            "principal_email": "user@example.com",
            "principal_display_name": "Example User",
            "access_level": "editor",
            "is_inherited": False,
            "is_external": False,
        }
    ]
    client.iter_shared_folder_members.assert_called_once_with("sf:reports")
    assert list(Draft7Validator(_schema()).iter_errors(records[0])) == []


def test_sharing_acl_supports_group_invitee_and_nullable_fields() -> None:
    client = Mock()
    client.iter_shared_folders.return_value = [SharedFoldersPage(entries=[_folder()], cursor=None)]
    client.iter_shared_folder_members.return_value = [
        SharedFolderMembersPage(
            users=[
                _user_member(
                    account_id=OTHER_ACCOUNT_ID,
                    email="external@example.com",
                    same_team=False,
                    access_type=AccessLevel.owner,
                    inherited=None,
                )
            ],
            groups=[_group_member()],
            invitees=[_invitee_member()],
            cursor=None,
        )
    ]

    records = list(SharingAcl(client, SCOPED_CONFIG).read_records(SyncMode.full_refresh))

    assert [(record["principal_type"], record["access_level"]) for record in records] == [
        ("user", "owner"),
        ("group", "viewer"),
        ("invitee", "viewer_no_comment"),
    ]
    assert records[0]["is_external"] is True
    assert records[0]["is_inherited"] is False
    assert records[1]["principal_id"] == "g:engineering"
    assert records[1]["principal_display_name"] == "Engineering"
    assert records[1]["is_external"] is True
    assert records[2]["principal_id"] is None
    assert records[2]["principal_email"] == "invitee@example.com"
    assert records[2]["is_external"] is None
    assert all(list(Draft7Validator(_schema()).iter_errors(record)) == [] for record in records)


def test_sharing_acl_distinguishes_resources_and_keeps_key_stable_across_rename() -> None:
    client = Mock()
    client.iter_shared_folders.return_value = [
        SharedFoldersPage(
            entries=[
                _folder(shared_folder_id="sf:one", path_lower="/reports/old"),
                _folder(shared_folder_id="sf:two", path_lower="/reports/two"),
            ],
            cursor=None,
        )
    ]
    client.iter_shared_folder_members.return_value = [SharedFolderMembersPage(users=[_user_member()], groups=[], invitees=[], cursor=None)]

    records = list(SharingAcl(client, SCOPED_CONFIG).read_records(SyncMode.full_refresh))

    assert [record["acl_key"] for record in records] == [
        f"sf:one|user|{ACCOUNT_ID}",
        f"sf:two|user|{ACCOUNT_ID}",
    ]

    renamed_client = Mock()
    renamed_client.iter_shared_folders.return_value = [
        SharedFoldersPage(
            entries=[_folder(shared_folder_id="sf:one", path_lower="/reports/new")],
            cursor=None,
        )
    ]
    renamed_client.iter_shared_folder_members.return_value = [
        SharedFolderMembersPage(users=[_user_member()], groups=[], invitees=[], cursor=None)
    ]
    renamed_record = list(SharingAcl(renamed_client, SCOPED_CONFIG).read_records(SyncMode.full_refresh))[0]
    assert renamed_record["acl_key"] == f"sf:one|user|{ACCOUNT_ID}"


def test_sharing_acl_access_level_change_keeps_same_identity_key() -> None:
    viewer_client = Mock()
    viewer_client.iter_shared_folders.return_value = [SharedFoldersPage(entries=[_folder()], cursor=None)]
    viewer_client.iter_shared_folder_members.return_value = [
        SharedFolderMembersPage(
            users=[_user_member(access_type=AccessLevel.viewer)],
            groups=[],
            invitees=[],
            cursor=None,
        )
    ]
    editor_client = Mock()
    editor_client.iter_shared_folders.return_value = [SharedFoldersPage(entries=[_folder()], cursor=None)]
    editor_client.iter_shared_folder_members.return_value = [
        SharedFolderMembersPage(
            users=[_user_member(access_type=AccessLevel.editor)],
            groups=[],
            invitees=[],
            cursor=None,
        )
    ]

    viewer = list(SharingAcl(viewer_client, SCOPED_CONFIG).read_records(SyncMode.full_refresh))[0]
    editor = list(SharingAcl(editor_client, SCOPED_CONFIG).read_records(SyncMode.full_refresh))[0]

    assert viewer["acl_key"] == editor["acl_key"] == f"sf:reports|user|{ACCOUNT_ID}"
    assert viewer["access_level"] == "viewer"
    assert editor["access_level"] == "editor"


def test_sharing_acl_root_confinement_and_empty_membership() -> None:
    client = Mock()
    client.iter_shared_folders.return_value = [
        SharedFoldersPage(
            entries=[
                _folder(path_lower="/reports"),
                _folder(shared_folder_id="sf:child", path_lower="/reports/2026"),
                _folder(shared_folder_id="sf:prefix", path_lower="/reports-old"),
                _folder(shared_folder_id="sf:other", path_lower="/other"),
                _folder(shared_folder_id="sf:unknown", path_lower=None),
            ],
            cursor=None,
        )
    ]
    client.iter_shared_folder_members.side_effect = [
        [SharedFolderMembersPage(users=[_user_member()], groups=[], invitees=[], cursor=None)],
        [SharedFolderMembersPage(users=[], groups=[], invitees=[], cursor=None)],
    ]

    records = list(SharingAcl(client, SCOPED_CONFIG).read_records(SyncMode.full_refresh))

    assert [record["resource_id"] for record in records] == ["sf:reports"]
    assert client.iter_shared_folder_members.call_args_list[0].args == ("sf:reports",)
    assert client.iter_shared_folder_members.call_args_list[1].args == ("sf:child",)
    assert client.iter_shared_folder_members.call_count == 2


def test_sharing_acl_member_pagination_and_protocol_read() -> None:
    client = Mock()
    client.iter_shared_folders.return_value = [SharedFoldersPage(entries=[_folder()], cursor=None)]
    client.iter_shared_folder_members.return_value = [
        SharedFolderMembersPage(users=[_user_member()], groups=[], invitees=[], cursor="next"),
        SharedFolderMembersPage(
            users=[
                _user_member(
                    account_id=OTHER_ACCOUNT_ID,
                    email="other@example.com",
                    access_type=AccessLevel.viewer,
                )
            ],
            groups=[],
            invitees=[],
            cursor=None,
        ),
    ]
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="sharing_acl",
                    json_schema=_schema(),
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
                primary_key=[["acl_key"]],
            )
        ]
    )

    with patch("source_dropbox.source.DropboxClient", return_value=client):
        messages = list(SourceDropbox().read(Mock(), SCOPED_CONFIG, catalog))

    records = [message.record for message in messages if message.type == Type.RECORD]
    assert [(record.stream, record.data["principal_email"]) for record in records] == [
        ("sharing_acl", "user@example.com"),
        ("sharing_acl", "other@example.com"),
    ]
    assert not hasattr(client, "files_download") or not client.files_download.called
    assert not hasattr(client, "sharing_add_folder_member") or not client.sharing_add_folder_member.called


def test_sharing_acl_deduplicates_identical_records_and_fails_conflicts_safely() -> None:
    client = Mock()
    client.iter_shared_folders.return_value = [SharedFoldersPage(entries=[_folder()], cursor=None)]
    client.iter_shared_folder_members.return_value = [
        SharedFolderMembersPage(
            users=[_user_member(), _user_member()],
            groups=[],
            invitees=[],
            cursor=None,
        )
    ]

    assert len(list(SharingAcl(client, SCOPED_CONFIG).read_records(SyncMode.full_refresh))) == 1

    conflict_client = Mock()
    conflict_client.iter_shared_folders.return_value = [SharedFoldersPage(entries=[_folder()], cursor=None)]
    conflict_client.iter_shared_folder_members.return_value = [
        SharedFolderMembersPage(
            users=[
                _user_member(email="secret-one@example.com"),
                _user_member(email="secret-two@example.com"),
            ],
            groups=[],
            invitees=[],
            cursor=None,
        )
    ]
    with pytest.raises(DropboxSharingAclError) as exc_info:
        list(SharingAcl(conflict_client, SCOPED_CONFIG).read_records(SyncMode.full_refresh))
    assert "secret-one@example.com" not in str(exc_info.value)
    assert "secret-two@example.com" not in str(exc_info.value)
    assert "sf:reports" in str(exc_info.value)


@pytest.mark.parametrize(
    ("users", "groups", "invitees"),
    [
        ([_user_member_without_identity()], [], []),
        ([], [_group_member_without_identity()], []),
        ([], [], [_invitee_member_without_identity()]),
    ],
)
def test_sharing_acl_fails_closed_without_stable_principal_identity(
    users: list[object], groups: list[object], invitees: list[object]
) -> None:
    client = Mock()
    client.iter_shared_folders.return_value = [SharedFoldersPage(entries=[_folder()], cursor=None)]
    client.iter_shared_folder_members.return_value = [SharedFolderMembersPage(users=users, groups=groups, invitees=invitees, cursor=None)]

    with pytest.raises(ValueError, match="stable identity"):
        list(SharingAcl(client, SCOPED_CONFIG).read_records(SyncMode.full_refresh))


def test_sharing_acl_client_paginates_members_and_classifies_errors() -> None:
    client = DropboxClient.__new__(DropboxClient)
    client._client = Mock()
    client._client.sharing_list_folder_members.return_value = SharedFolderMembers(
        users=[_user_member()], groups=[], invitees=[], cursor="next"
    )
    client._client.sharing_list_folder_members_continue.return_value = SharedFolderMembers(
        users=[], groups=[_group_member()], invitees=[], cursor=None
    )

    pages = list(client.iter_shared_folder_members("sf:reports"))

    assert [(len(page.users), len(page.groups), page.cursor) for page in pages] == [
        (1, 0, "next"),
        (0, 1, None),
    ]
    client._client.sharing_list_folder_members.assert_called_once_with("sf:reports")
    client._client.sharing_list_folder_members_continue.assert_called_once_with("next")

    client._client.sharing_list_folder_members.side_effect = AuthError("request-id", SimpleNamespace(_tag="missing_scope"))
    with pytest.raises(DropboxSharingPermissionError, match="sharing.read"):
        list(client.iter_shared_folder_members("sf:reports"))

    client._client.sharing_list_folder_members.side_effect = BadInputError("request-id", '{"error":"invalid_grant"}')
    with pytest.raises(DropboxAuthenticationError, match="invalid or revoked"):
        list(client.iter_shared_folder_members("sf:reports"))

    client._client.sharing_list_folder_members.side_effect = RateLimitError("request-id")
    with pytest.raises(DropboxRateLimitError, match="membership"):
        list(client.iter_shared_folder_members("sf:reports"))


def test_sharing_acl_client_fails_on_member_continuation_failure() -> None:
    client = DropboxClient.__new__(DropboxClient)
    client._client = Mock()
    client._client.sharing_list_folder_members.return_value = SharedFolderMembers(users=[], groups=[], invitees=[], cursor="next")
    client._client.sharing_list_folder_members_continue.side_effect = ApiError(
        "request-id", ListFolderMembersContinueError.invalid_cursor, None, None
    )

    with pytest.raises(DropboxSharingAclError, match="continue"):
        list(client.iter_shared_folder_members("sf:reports"))
