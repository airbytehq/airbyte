"""Internal functions for syncing local Airbyte resources with the Airbyte API."""


## Enum class "Fail", "Replace", "Update", "Ignore"
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from airbyte_lib.cloud import _api_util as api_util
from airbyte_lib.exceptions import MissingResourceError


if TYPE_CHECKING:
    from airbyte_lib.cloud.hosts import HostedAirbyteInstance
    from airbyte_lib.source import Source


class IfExists(Enum, str):
    """IfExists enum class."""

    FAIL = "fail"
    """Fail if the resource already exists."""

    REPLACE = "replace"
    """Replace the resource if it already exists."""

    UPDATE = "update"
    """Update the resource if it already exists.

    This will fail if the resource is not compatible.
    """

    IGNORE = "ignore"
    """Do nothing if the resource already exists."""


class SyncMode(Enum, str):
    """IfExists enum class."""

    CREATE = "create"
    """Create the resource. Fail if it already exists."""

    CREATE_OR_REPLACE = "create_or_replace"
    """Create the resource. Replace (delete and recreate) if it already exists."""

    CREATE_OR_UPDATE = "create_or_update"
    """Create the resource. Update the existing copy if it already exists."""

    GET = "get"
    """Get the resource without updating.

    Fail if the resource does not exist.
    """

    UPDATE = "update"
    """Update an already-existing resource.

    Fail if the resource is not compatible or not able to be updated.
    Fail if the resource does not exist.
    """

def sync_source_definition(
    source: Source,
    airbyte_instance: HostedAirbyteInstance,
    *,
    name: str | None = None,
    source_id: str | None = None,
    sync_mode: SyncMode = SyncMode.CREATE,
) -> str:
    """Upload a source definition.

    Returns the source ID if successful.
    """
    if source_id and name:
        raise ValueError("Cannot specify both name and source_id.")

    try:
        if name:
            remote_source = api_util.get_source_by_name(
                name=name,
                api_key=airbyte_instance.api_key,
                api_root=airbyte_instance.api_root,
            )
        elif source_id:
            remote_source = api_util.get_source(
                source_id=source_id,
                api_key=airbyte_instance.api_key,
                api_root=airbyte_instance.api_root,
            )
    except MissingResourceError:
        pass

    if not remote_source and sync_mode in [SyncMode.GET, SyncMode.UPDATE]:
        raise ValueError("Source does not exist.")

    if remote_source and sync_mode == SyncMode.CREATE:
        raise ValueError(f"Source {source.name} already exists.")

    # Remaining modes all support creating a new source if missing.

    if not remote_source:
        # Create the source and we're done.
        remote_source = api_util.create_source(
            name=name,
            source_type=source.source_type,
            config=source.config,
            api_key=airbyte_instance.api_key,
            api_root=airbyte_instance.api_root,
        )
        return remote_source.connection_id

    # Else: source already exists.

    if sync_mode == SyncMode.GET:
        return source.connection_id

    if sync_mode == SyncMode.CREATE_OR_REPLACE:
        # TODO: implement a rename-swap operation so we do not delete the
        # existing source until and unless the new one is created.
        api_util.delete_source(
            source_id=remote_source.connection_id,
            api_key=airbyte_instance.api_key,
            api_root=airbyte_instance.api_root,
        )
        remote_source = api_util.create_source(
            name=name,
            source_type=source.source_type,
            config=source.config,
            api_key=airbyte_instance.api_key,
            api_root=airbyte_instance.api_root,
        )
        return remote_source.connection_id

    if sync_mode == SyncMode.CREATE_OR_UPDATE:
        if remote_source.type != source.source_type:
            raise ValueError(
                f"Source {remote_source.name} already exists "
                f"with incompatible type {remote_source.type}."
                f" Expected {source.source_type}."
            )
        api_util.update_source(
            source_id=source.source_id,
            name=name,
            source_type=source.source_type,
            config=source.config,
            api_key=airbyte_instance.api_key,
            api_root=airbyte_instance.api_root,
        )
        return source_id

    raise ValueError(f"Invalid sync mode: {sync_mode}")
