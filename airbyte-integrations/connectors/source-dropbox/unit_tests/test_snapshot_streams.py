import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

from dropbox.files import (
    DeletedMetadata,
    FileLockMetadata,
    FileMetadata,
    FileSharingInfo,
    FolderMetadata,
    FolderSharingInfo,
)
from jsonschema import Draft7Validator
from source_dropbox.client import DropboxPage
from source_dropbox.source import SourceDropbox
from source_dropbox.streams.files import Files
from source_dropbox.streams.folders import Folders

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)


CONFIG = {
    "credentials": {"auth_type": "access_token", "access_token": "test-token"},
    "path": "/configured",
    "recursive": False,
    "include_deleted": True,
}
ACCOUNT_ID = "dbid:" + "e" * 35


def _file() -> FileMetadata:
    return FileMetadata(
        name="document.txt",
        id="id:file",
        client_modified=datetime(2026, 8, 3, tzinfo=UTC),
        server_modified=datetime(2026, 8, 4, tzinfo=UTC),
        rev="0123456789",
        size=42,
        path_lower="/configured/document.txt",
        path_display="/configured/document.txt",
        content_hash="a" * 64,
        is_downloadable=True,
        has_explicit_shared_members=True,
        sharing_info=FileSharingInfo(
            read_only=False,
            parent_shared_folder_id="shared:parent",
            modified_by=ACCOUNT_ID,
        ),
        file_lock_info=FileLockMetadata(
            is_lockholder=True,
            lockholder_name="Dropbox User",
            lockholder_account_id=ACCOUNT_ID,
            created=datetime(2026, 8, 5, tzinfo=UTC),
        ),
    )


def _folder() -> FolderMetadata:
    return FolderMetadata(
        name="documents",
        id="id:folder",
        path_lower="/configured/documents",
        path_display="/configured/Documents",
        shared_folder_id="shared:folder",
        sharing_info=FolderSharingInfo(
            read_only=False,
            parent_shared_folder_id="shared:parent",
            shared_folder_id="shared:folder",
            traverse_only=False,
            no_access=False,
        ),
    )


def _deleted() -> DeletedMetadata:
    return DeletedMetadata(
        name="deleted.txt",
        path_lower="/configured/deleted.txt",
        path_display="/configured/deleted.txt",
    )


def _schema(name: str) -> dict[str, object]:
    path = Path(__file__).parents[1] / "source_dropbox" / "schemas" / f"{name}.json"
    return json.loads(path.read_text())


def _schema_has_field_path(schema: dict[str, object], field_path: list[str]) -> bool:
    current = schema
    for field in field_path:
        properties = current.get("properties")
        if not isinstance(properties, dict) or field not in properties:
            return False
        next_schema = properties[field]
        if not isinstance(next_schema, dict):
            return False
        current = next_schema
    return True


def test_discover_exposes_snapshot_streams_in_order() -> None:
    with patch("source_dropbox.source.DropboxClient"):
        catalog = SourceDropbox().discover(Mock(), CONFIG)

    assert [stream.name for stream in catalog.streams] == [
        "entries",
        "files",
        "folders",
        "file_properties",
        "shared_links",
        "shared_folders",
        "sharing_acl",
    ]
    assert catalog.streams[0].supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental]
    assert catalog.streams[0].default_cursor_field == []
    assert catalog.streams[1].supported_sync_modes == [SyncMode.full_refresh]
    assert catalog.streams[2].supported_sync_modes == [SyncMode.full_refresh]
    assert catalog.streams[1].source_defined_primary_key == [["id"]]
    assert catalog.streams[2].source_defined_primary_key == [["id"]]
    assert catalog.streams[3].supported_sync_modes == [SyncMode.full_refresh]
    assert catalog.streams[3].source_defined_primary_key == [["property_key"]]
    assert catalog.streams[4].supported_sync_modes == [SyncMode.full_refresh]
    assert catalog.streams[5].supported_sync_modes == [SyncMode.full_refresh]
    assert catalog.streams[6].supported_sync_modes == [SyncMode.full_refresh]
    assert catalog.streams[6].source_defined_primary_key == [["acl_key"]]


def test_discovered_cursor_fields_exist_in_stream_schemas() -> None:
    with patch("source_dropbox.source.DropboxClient"):
        catalog = SourceDropbox().discover(Mock(), CONFIG)

    streams = {stream.name: stream for stream in catalog.streams}
    entries = streams["entries"]
    assert SyncMode.incremental in entries.supported_sync_modes
    assert entries.default_cursor_field == []
    assert "cursor" not in entries.json_schema["properties"]

    for stream in catalog.streams:
        field_path = stream.default_cursor_field
        if field_path:
            assert _schema_has_field_path(stream.json_schema, field_path), (
                f"{stream.name} advertises missing cursor field path {field_path}"
            )


def test_files_filters_metadata_pages_and_preserves_optional_metadata() -> None:
    client = Mock()
    client.iter_entries.return_value = [
        DropboxPage(entries=[_file(), _folder(), _deleted()], cursor="page-one", has_more=True),
        DropboxPage(entries=[_file()], cursor="page-two", has_more=False),
    ]

    records = list(Files(client, CONFIG).read_records(SyncMode.full_refresh))

    assert [record["id"] for record in records] == ["id:file", "id:file"]
    assert records[0]["sharing_info"] == {
        "read_only": False,
        "parent_shared_folder_id": "shared:parent",
        "modified_by": ACCOUNT_ID,
    }
    assert records[0]["file_lock_info"] == {
        "is_lockholder": True,
        "lockholder_name": "Dropbox User",
        "lockholder_account_id": ACCOUNT_ID,
        "created": "2026-08-05T00:00:00+00:00",
    }
    client.iter_entries.assert_called_once_with(path="/configured", recursive=False, include_deleted=False)
    assert list(Draft7Validator(_schema("files")).iter_errors(records[0])) == []


def test_folders_filters_metadata_and_handles_optional_sharing_metadata() -> None:
    client = Mock()
    client.iter_entries.return_value = [DropboxPage(entries=[_file(), _folder(), _deleted()], cursor="page-one", has_more=False)]

    records = list(Folders(client, CONFIG).read_records(SyncMode.full_refresh))

    assert records == [
        {
            "id": "id:folder",
            "name": "documents",
            "path_lower": "/configured/documents",
            "path_display": "/configured/Documents",
            "shared_folder_id": "shared:folder",
            "sharing_info": {
                "read_only": False,
                "parent_shared_folder_id": "shared:parent",
                "shared_folder_id": "shared:folder",
                "traverse_only": False,
                "no_access": False,
            },
        }
    ]
    client.iter_entries.assert_called_once_with(path="/configured", recursive=False, include_deleted=False)
    assert list(Draft7Validator(_schema("folders")).iter_errors(records[0])) == []


def test_snapshot_records_allow_missing_optional_metadata() -> None:
    client = Mock()
    file = _file()
    file.sharing_info = None
    file.file_lock_info = None
    file.has_explicit_shared_members = None
    folder = FolderMetadata(name="root", id="id:root", path_lower=None, path_display=None)
    client.iter_entries.return_value = [DropboxPage(entries=[file, folder], cursor="page", has_more=False)]

    file_record = list(Files(client, CONFIG).read_records(SyncMode.full_refresh))[0]
    folder_record = list(Folders(client, CONFIG).read_records(SyncMode.full_refresh))[0]

    assert file_record["sharing_info"] is None
    assert file_record["file_lock_info"] is None
    assert file_record["has_explicit_shared_members"] is None
    assert folder_record["id"] == "id:root"
    assert list(Draft7Validator(_schema("files")).iter_errors(file_record)) == []
    assert list(Draft7Validator(_schema("folders")).iter_errors(folder_record)) == []


def test_snapshot_streams_read_through_source_protocol() -> None:
    client = Mock()
    client.iter_entries.return_value = [DropboxPage(entries=[_file(), _folder(), _deleted()], cursor="page", has_more=False)]
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=name,
                    json_schema=_schema(name),
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
                primary_key=[["id"]],
            )
            for name in ("files", "folders")
        ]
    )

    with patch("source_dropbox.source.DropboxClient", return_value=client):
        messages = list(SourceDropbox().read(Mock(), CONFIG, catalog))

    records = [message.record for message in messages if message.type == Type.RECORD]
    assert [(record.stream, record.data["id"]) for record in records] == [
        ("files", "id:file"),
        ("folders", "id:folder"),
    ]
    assert client.iter_entries.call_count == 2
    assert all(call.kwargs["include_deleted"] is False for call in client.iter_entries.call_args_list)
