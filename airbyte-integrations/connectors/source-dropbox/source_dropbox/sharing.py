# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any

from dropbox.exceptions import ApiError, AuthError, BadInputError, RateLimitError
from dropbox.sharing import (
    ListFolderMembersContinueError,
    ListFoldersContinueError,
    ListFoldersResult,
    ListSharedLinksError,
    ListSharedLinksResult,
    SharedFolderMembers,
    SharedFolderMetadata,
    SharedLinkMetadata,
)

from source_dropbox.errors import (
    DropboxRateLimitError,
    DropboxSharedFoldersCursorResetError,
    DropboxSharedLinksCursorResetError,
    DropboxSharingAclError,
    raise_auth_or_refresh_error,
)
from source_dropbox.namespaces import NamespaceInfo


@dataclass(frozen=True)
class SharedLinksPage:
    links: list[SharedLinkMetadata]
    cursor: str | None
    has_more: bool
    namespace: NamespaceInfo | None = None


@dataclass(frozen=True)
class SharedFoldersPage:
    entries: list[SharedFolderMetadata]
    cursor: str | None
    namespace: NamespaceInfo | None = None


@dataclass(frozen=True)
class SharedFolderMembersPage:
    users: list[Any]
    groups: list[Any]
    invitees: list[Any]
    cursor: str | None


def iter_shared_links(
    namespace_clients: Callable[[], Iterator[tuple[NamespaceInfo | None, Any]]],
) -> Iterator[SharedLinksPage]:
    """List the authenticated account's shared-link inventory."""
    for namespace, client in namespace_clients():
        yield from iter_shared_links_for_client(client, namespace=namespace)


def iter_shared_links_for_client(client: Any, namespace: NamespaceInfo | None = None) -> Iterator[SharedLinksPage]:
    cursor: str | None = None
    reset_recovered = False
    while True:
        try:
            result = client.sharing_list_shared_links(cursor=cursor)
        except (AuthError, BadInputError) as exc:
            raise_auth_or_refresh_error(exc, required_scope="sharing.read")
        except RateLimitError as exc:
            raise DropboxRateLimitError("Dropbox rate limited sharing synchronization.") from exc
        except ApiError as exc:
            if isinstance(exc.error, ListSharedLinksError) and exc.error.is_reset():
                if reset_recovered:
                    raise DropboxSharedLinksCursorResetError("Dropbox repeatedly invalidated the shared-link pagination cursor.") from exc
                # A full refresh can safely restart. Previously emitted links may replay,
                # and destinations deduplicate them using the URL-based link_key.
                cursor = None
                reset_recovered = True
                continue
            raise
        page = to_shared_links_page(result, namespace=namespace)
        yield page
        if not page.has_more:
            break
        cursor = page.cursor
        if cursor is None:
            raise RuntimeError("Dropbox returned shared-link pagination without a cursor.")


def iter_shared_folders(
    namespace_clients: Callable[[], Iterator[tuple[NamespaceInfo | None, Any]]],
    *,
    shared_folder_clients: dict[str, Any],
) -> Iterator[SharedFoldersPage]:
    """List all shared folders available to the authenticated account."""
    for namespace, client in namespace_clients():
        yield from iter_shared_folders_for_client(client, namespace=namespace, shared_folder_clients=shared_folder_clients)


def iter_shared_folders_for_client(
    client: Any,
    namespace: NamespaceInfo | None = None,
    *,
    shared_folder_clients: dict[str, Any],
) -> Iterator[SharedFoldersPage]:
    reset_recovered = False
    result = list_shared_folders(client)
    while True:
        page = to_shared_folders_page(result, namespace=namespace)
        for folder in page.entries:
            folder_id = getattr(folder, "shared_folder_id", None)
            if isinstance(folder_id, str) and folder_id:
                shared_folder_clients[folder_id] = client
        yield page
        if page.cursor is None:
            break
        try:
            result = client.sharing_list_folders_continue(page.cursor)
        except (AuthError, BadInputError) as exc:
            raise_auth_or_refresh_error(exc, required_scope="sharing.read")
        except RateLimitError as exc:
            raise DropboxRateLimitError("Dropbox rate limited sharing synchronization.") from exc
        except ApiError as exc:
            is_invalid_cursor = isinstance(exc.error, ListFoldersContinueError) and exc.error.is_invalid_cursor()
            if is_invalid_cursor:
                if reset_recovered:
                    raise DropboxSharedFoldersCursorResetError(
                        "Dropbox repeatedly invalidated the shared-folder pagination cursor."
                    ) from exc
                # A full refresh can restart safely. The shared_folder_id primary key
                # lets destinations deduplicate entries replayed from the first page.
                result = list_shared_folders(client)
                reset_recovered = True
            else:
                raise


def iter_shared_folder_members(
    shared_folder_id: str,
    *,
    base_client: Any,
    shared_folder_clients: dict[str, Any],
) -> Iterator[SharedFolderMembersPage]:
    """List all user/group/invitee members for one shared folder."""
    client = shared_folder_clients.get(shared_folder_id, base_client)
    try:
        result = client.sharing_list_folder_members(shared_folder_id)
    except (AuthError, BadInputError) as exc:
        raise_auth_or_refresh_error(exc, required_scope="sharing.read")
    except RateLimitError as exc:
        raise DropboxRateLimitError("Dropbox rate limited shared-folder membership synchronization.") from exc
    except ApiError as exc:
        raise DropboxSharingAclError(f"Dropbox could not list members for shared folder {shared_folder_id}.") from exc

    while True:
        page = to_shared_folder_members_page(result)
        yield page
        if page.cursor is None:
            break
        try:
            result = client.sharing_list_folder_members_continue(page.cursor)
        except (AuthError, BadInputError) as exc:
            raise_auth_or_refresh_error(exc, required_scope="sharing.read")
        except RateLimitError as exc:
            raise DropboxRateLimitError("Dropbox rate limited shared-folder membership synchronization.") from exc
        except ApiError as exc:
            if isinstance(exc.error, ListFolderMembersContinueError):
                raise DropboxSharingAclError(f"Dropbox could not continue listing members for shared folder {shared_folder_id}.") from exc
            raise DropboxSharingAclError(f"Dropbox could not continue listing members for shared folder {shared_folder_id}.") from exc


def list_shared_folders(client: Any) -> ListFoldersResult:
    try:
        return client.sharing_list_folders()
    except (AuthError, BadInputError) as exc:
        raise_auth_or_refresh_error(exc, required_scope="sharing.read")
    except RateLimitError as exc:
        raise DropboxRateLimitError("Dropbox rate limited sharing synchronization.") from exc


def to_shared_links_page(result: ListSharedLinksResult, namespace: NamespaceInfo | None = None) -> SharedLinksPage:
    return SharedLinksPage(
        links=list(result.links),
        cursor=result.cursor,
        has_more=result.has_more,
        namespace=namespace,
    )


def to_shared_folders_page(result: ListFoldersResult, namespace: NamespaceInfo | None = None) -> SharedFoldersPage:
    return SharedFoldersPage(entries=list(result.entries), cursor=result.cursor, namespace=namespace)


def to_shared_folder_members_page(result: SharedFolderMembers) -> SharedFolderMembersPage:
    return SharedFolderMembersPage(
        users=list(result.users or []),
        groups=list(result.groups or []),
        invitees=list(result.invitees or []),
        cursor=result.cursor,
    )
