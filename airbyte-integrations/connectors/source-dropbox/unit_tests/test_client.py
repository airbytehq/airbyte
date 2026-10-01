from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from dropbox.exceptions import ApiError, AuthError, BadInputError, RateLimitError
from dropbox.files import ListFolderContinueError
from source_dropbox.client import (
    DropboxAuthenticationError,
    DropboxClient,
    DropboxCursorResetError,
    DropboxPage,
    DropboxRateLimitError,
)


ACCESS_TOKEN_CONFIG = {"credentials": {"auth_type": "access_token", "access_token": "test-token"}}


def test_access_token_client_enables_sdk_retries() -> None:
    with patch("source_dropbox.dropbox_context.dropbox.Dropbox") as dropbox_client:
        DropboxClient(ACCESS_TOKEN_CONFIG)

    dropbox_client.assert_called_once_with(
        oauth2_access_token="test-token",
        max_retries_on_error=5,
        max_retries_on_rate_limit=5,
    )


def test_select_user_client_construction_applies_member_context() -> None:
    team = Mock()
    user_client = Mock()
    team.as_user.return_value = user_client
    with patch("source_dropbox.dropbox_context.dropbox.DropboxTeam", return_value=team):
        client = DropboxClient(
            {
                **ACCESS_TOKEN_CONFIG,
                "team_context": {"mode": "user", "select_user": "dbmid:member"},
            }
        )

    team.as_user.assert_called_once_with("dbmid:member")
    assert client._client is user_client


def test_path_root_namespace_is_applied_to_client() -> None:
    base = Mock()
    rooted = Mock()
    base.with_path_root.return_value = rooted
    with patch("source_dropbox.dropbox_context.dropbox.Dropbox", return_value=base):
        client = DropboxClient(
            {
                **ACCESS_TOKEN_CONFIG,
                "path_root": {"mode": "namespace_id", "namespace_id": "12345"},
            }
        )

    base.with_path_root.assert_called_once()
    assert client._client is rooted


def test_home_path_root_resolves_account_root_info() -> None:
    base = Mock()
    rooted = Mock()
    base.with_path_root.return_value = rooted
    base.users_get_current_account.return_value = SimpleNamespace(
        root_info=SimpleNamespace(home_namespace_id="home", root_namespace_id="root")
    )
    rooted.users_get_current_account.return_value = SimpleNamespace(
        root_info=SimpleNamespace(home_namespace_id="home", root_namespace_id="root")
    )
    with patch("source_dropbox.dropbox_context.dropbox.Dropbox", return_value=base):
        client = DropboxClient({**ACCESS_TOKEN_CONFIG, "path_root": {"mode": "home"}})

    base.users_get_current_account.assert_called_once()
    rooted.users_get_current_account.assert_called_once()
    base.with_path_root.assert_called_once()
    assert client._client is rooted
    assert client.context_scope() == {
        "team_mode": "none",
        "path_root_mode": "home",
        "namespace_id": "home",
    }


def test_current_account_classifies_authentication_errors() -> None:
    client = DropboxClient.__new__(DropboxClient)
    client._client = Mock()
    client._client.users_get_current_account.side_effect = AuthError("request-id", None)

    with pytest.raises(DropboxAuthenticationError, match="rejected"):
        client.current_account()


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ('{"error":"invalid_client"}', "app key"),
        ('{"error":"invalid_grant"}', "invalid or revoked"),
    ],
)
def test_current_account_classifies_refresh_token_exchange_errors(message, expected) -> None:
    client = DropboxClient.__new__(DropboxClient)
    client._client = Mock()
    client._client.users_get_current_account.side_effect = BadInputError("request-id", message)

    with pytest.raises(DropboxAuthenticationError, match=expected):
        client.current_account()


def test_current_account_classifies_revoked_access_token() -> None:
    client = DropboxClient.__new__(DropboxClient)
    client._client = Mock()
    client._client.users_get_current_account.side_effect = AuthError("request-id", SimpleNamespace(_tag="invalid_access_token"))

    with pytest.raises(DropboxAuthenticationError, match="invalid, expired, or revoked"):
        client.current_account()


def test_list_folder_continue_classifies_exhausted_rate_limit() -> None:
    client = DropboxClient.__new__(DropboxClient)
    client._client = Mock()
    client._client.files_list_folder_continue.side_effect = RateLimitError("request-id")

    with pytest.raises(DropboxRateLimitError, match="rate limited"):
        client.list_folder_continue("cursor")


def test_list_folder_classifies_authentication_errors() -> None:
    client = DropboxClient.__new__(DropboxClient)
    client._client = Mock()
    client._client.files_list_folder.side_effect = AuthError("request-id", None)

    with pytest.raises(DropboxAuthenticationError, match="rejected"):
        client.list_folder("", recursive=True, include_deleted=True)


def test_list_folder_classifies_refresh_token_failure_during_sync() -> None:
    client = DropboxClient.__new__(DropboxClient)
    client._client = Mock()
    client._client.files_list_folder.side_effect = BadInputError("request-id", '{"error":"invalid_grant"}')

    with pytest.raises(DropboxAuthenticationError, match="invalid or revoked"):
        client.list_folder("", recursive=True, include_deleted=True)


def test_list_folder_continue_classifies_refresh_token_failure_during_sync() -> None:
    client = DropboxClient.__new__(DropboxClient)
    client._client = Mock()
    client._client.files_list_folder_continue.side_effect = BadInputError("request-id", '{"error":"invalid_grant"}')

    with pytest.raises(DropboxAuthenticationError, match="invalid or revoked"):
        client.list_folder_continue("cursor")


def test_list_folder_continue_classifies_cursor_reset() -> None:
    client = DropboxClient.__new__(DropboxClient)
    client._client = Mock()
    client._client.files_list_folder_continue.side_effect = ApiError("request-id", ListFolderContinueError.reset, None, None)

    with pytest.raises(DropboxCursorResetError, match="invalidated"):
        client.list_folder_continue("cursor")


def test_iter_entries_replays_from_root_after_saved_cursor_reset() -> None:
    client = DropboxClient.__new__(DropboxClient)
    page = DropboxPage(entries=[Mock()], cursor="new-cursor", has_more=False)
    client.list_folder_continue = Mock(side_effect=DropboxCursorResetError("reset"))
    client.list_folder = Mock(return_value=page)

    # A reset cannot safely resume the old listing. Replaying this page is safe
    # because entries use entry_key as their destination primary key.
    assert list(client.iter_entries(path="/test", recursive=True, include_deleted=True, cursor="old")) == [page]
    client.list_folder.assert_called_once_with("/test", True, True)


def test_iter_entries_paginates_all_pages() -> None:
    client = DropboxClient.__new__(DropboxClient)
    first_page = DropboxPage(entries=[], cursor="page-one", has_more=True)
    second_page = DropboxPage(entries=[], cursor="page-two", has_more=False)
    client.list_folder = Mock(return_value=first_page)
    client.list_folder_continue = Mock(return_value=second_page)

    assert list(client.iter_entries(path="/test", recursive=True, include_deleted=False)) == [
        first_page,
        second_page,
    ]
    client.list_folder_continue.assert_called_once_with("page-one")


def test_iter_entries_does_not_loop_when_a_reset_repeats() -> None:
    client = DropboxClient.__new__(DropboxClient)
    first_page = DropboxPage(entries=[], cursor="page-one", has_more=True)
    client.list_folder_continue = Mock(side_effect=[DropboxCursorResetError("reset"), DropboxCursorResetError("reset")])
    client.list_folder = Mock(return_value=first_page)

    with pytest.raises(DropboxCursorResetError):
        list(client.iter_entries(path="/test", recursive=True, include_deleted=True, cursor="old"))

    client.list_folder.assert_called_once_with("/test", True, True)
