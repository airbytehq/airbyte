# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from dropbox.file_properties import (
    GetTemplateResult,
    PropertyField,
    PropertyGroup,
    TemplateFilter,
    TemplateFilterBase,
    TemplateFilterBase_validator,
)
from dropbox.files import DeletedMetadata, FileMetadata, FolderMetadata, ListFolderArg
from jsonschema import Draft7Validator
from source_dropbox.client import DropboxClient, DropboxFilePropertiesError, DropboxPage
from source_dropbox.source import SourceDropbox
from source_dropbox.streams.file_properties import FileProperties

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
    "path": "/Contracts",
    "recursive": False,
}


def _schema() -> dict[str, object]:
    path = Path(__file__).parents[1] / "source_dropbox" / "schemas" / "file_properties.json"
    return json.loads(path.read_text())


def _file(
    *,
    file_id: str = "id:file",
    path_lower: str = "/contracts/report.pdf",
    path_display: str = "/Contracts/report.pdf",
    property_groups: list[PropertyGroup] | None = None,
) -> FileMetadata:
    return FileMetadata(
        name=Path(path_display).name,
        id=file_id,
        client_modified=datetime(2026, 8, 1, tzinfo=UTC),
        server_modified=datetime(2026, 8, 2, tzinfo=UTC),
        rev="012345678",
        size=10,
        path_lower=path_lower,
        path_display=path_display,
        content_hash="a" * 64,
        is_downloadable=True,
        property_groups=property_groups,
    )


def _group(template_id: str, *fields: tuple[str, str | None]) -> PropertyGroup:
    return PropertyGroup(
        template_id=template_id,
        fields=[PropertyField(name=name, value=value) for name, value in fields],
    )


def test_file_properties_normalizes_one_file_multiple_fields() -> None:
    client = Mock()
    client.iter_entries_with_property_groups.return_value = [
        DropboxPage(
            entries=[_file(property_groups=[_group("ptid:contract", ("Customer", "Acme"), ("Status", "Signed"))])],
            cursor="cursor",
            has_more=False,
        )
    ]
    client.get_property_template.return_value = GetTemplateResult(name="Contract", description="Contract metadata", fields=[])

    records = list(FileProperties(client, CONFIG).read_records(SyncMode.full_refresh))

    assert records == [
        {
            "property_key": "id:file|ptid:contract|Customer",
            "file_id": "id:file",
            "file_name": "report.pdf",
            "path_lower": "/contracts/report.pdf",
            "path_display": "/Contracts/report.pdf",
            "template_id": "ptid:contract",
            "template_name": "Contract",
            "field_id": None,
            "field_name": "Customer",
            "field_value": "Acme",
        },
        {
            "property_key": "id:file|ptid:contract|Status",
            "file_id": "id:file",
            "file_name": "report.pdf",
            "path_lower": "/contracts/report.pdf",
            "path_display": "/Contracts/report.pdf",
            "template_id": "ptid:contract",
            "template_name": "Contract",
            "field_id": None,
            "field_name": "Status",
            "field_value": "Signed",
        },
    ]
    client.iter_entries_with_property_groups.assert_called_once_with(path="/Contracts", recursive=False)
    client.get_property_template.assert_called_once_with("ptid:contract")
    assert list(Draft7Validator(_schema()).iter_errors(records[0])) == []


def test_file_properties_supports_multiple_templates_and_caches_names() -> None:
    client = Mock()
    client.iter_entries_with_property_groups.return_value = [
        DropboxPage(
            entries=[
                _file(
                    property_groups=[
                        _group("ptid:contract", ("Customer", "Acme")),
                        _group("ptid:classification", ("Region", "US")),
                    ]
                ),
                _file(
                    file_id="id:other",
                    path_lower="/contracts/other.pdf",
                    path_display="/Contracts/other.pdf",
                    property_groups=[_group("ptid:contract", ("Customer", "Beta"))],
                ),
            ],
            cursor="cursor",
            has_more=False,
        )
    ]
    client.get_property_template.side_effect = [
        GetTemplateResult(name="Contract", description=None, fields=[]),
        GetTemplateResult(name="Classification", description=None, fields=[]),
    ]

    records = list(FileProperties(client, CONFIG).read_records(SyncMode.full_refresh))

    assert [record["property_key"] for record in records] == [
        "id:file|ptid:contract|Customer",
        "id:file|ptid:classification|Region",
        "id:other|ptid:contract|Customer",
    ]
    assert client.get_property_template.call_count == 2


def test_file_properties_uses_file_id_not_path_for_rename_stability() -> None:
    client = Mock()
    client.iter_entries_with_property_groups.return_value = [
        DropboxPage(
            entries=[
                _file(
                    file_id="id:stable",
                    path_lower="/contracts/renamed.pdf",
                    path_display="/Contracts/renamed.pdf",
                    property_groups=[_group("ptid:contract", ("Customer", "Acme"))],
                )
            ],
            cursor="cursor",
            has_more=False,
        )
    ]
    client.get_property_template.return_value = None

    record = list(FileProperties(client, CONFIG).read_records(SyncMode.full_refresh))[0]

    assert record["property_key"] == "id:stable|ptid:contract|Customer"
    assert record["template_name"] is None


def test_file_properties_empty_properties_and_non_files_emit_zero_records() -> None:
    client = Mock()
    client.iter_entries_with_property_groups.return_value = [
        DropboxPage(
            entries=[
                _file(property_groups=[]),
                FolderMetadata(
                    name="folder",
                    id="id:folder",
                    path_lower="/contracts/folder",
                    path_display="/Contracts/folder",
                ),
                DeletedMetadata(
                    name="deleted.pdf",
                    path_lower="/contracts/deleted.pdf",
                    path_display="/Contracts/deleted.pdf",
                ),
            ],
            cursor="cursor",
            has_more=False,
        )
    ]

    assert list(FileProperties(client, CONFIG).read_records(SyncMode.full_refresh)) == []


def test_file_properties_paginates_complete_inventory() -> None:
    client = Mock()
    client.iter_entries_with_property_groups.return_value = [
        DropboxPage(
            entries=[_file(property_groups=[_group("ptid:a", ("A", "1"))])],
            cursor="one",
            has_more=True,
        ),
        DropboxPage(
            entries=[
                _file(
                    file_id="id:two",
                    path_lower="/contracts/two.pdf",
                    path_display="/Contracts/two.pdf",
                    property_groups=[_group("ptid:b", ("B", "2"))],
                )
            ],
            cursor="two",
            has_more=False,
        ),
    ]
    client.get_property_template.return_value = None

    records = list(FileProperties(client, CONFIG).read_records(SyncMode.full_refresh))

    assert [record["property_key"] for record in records] == [
        "id:file|ptid:a|A",
        "id:two|ptid:b|B",
    ]


def test_file_properties_fails_on_inventory_pagination_failure() -> None:
    client = Mock()
    client.iter_entries_with_property_groups.side_effect = RuntimeError("pagination failed")

    with pytest.raises(RuntimeError, match="pagination failed"):
        list(FileProperties(client, CONFIG).read_records(SyncMode.full_refresh))


def test_file_properties_deduplicates_identical_records_and_fails_conflicts() -> None:
    identical = _group("ptid:contract", ("Customer", "Acme"), ("Customer", "Acme"))
    conflicting = _group("ptid:contract", ("Customer", "Acme"), ("Customer", "Secret Value"))
    client = Mock()
    client.get_property_template.return_value = None
    client.iter_entries_with_property_groups.return_value = [
        DropboxPage(
            entries=[_file(property_groups=[identical])],
            cursor="cursor",
            has_more=False,
        )
    ]

    assert len(list(FileProperties(client, CONFIG).read_records(SyncMode.full_refresh))) == 1

    client.iter_entries_with_property_groups.return_value = [
        DropboxPage(
            entries=[_file(property_groups=[conflicting])],
            cursor="cursor",
            has_more=False,
        )
    ]
    with pytest.raises(DropboxFilePropertiesError) as exc_info:
        list(FileProperties(client, CONFIG).read_records(SyncMode.full_refresh))
    assert "Secret Value" not in str(exc_info.value)
    assert "property key id:file|ptid:contract|Customer" in str(exc_info.value)


def test_file_properties_read_through_source_protocol() -> None:
    client = Mock()
    client.iter_entries_with_property_groups.return_value = [
        DropboxPage(
            entries=[_file(property_groups=[_group("ptid:contract", ("Customer", "Acme"))])],
            cursor="cursor",
            has_more=False,
        )
    ]
    client.get_property_template.return_value = GetTemplateResult(name="Contract", description=None, fields=[])
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="file_properties",
                    json_schema=_schema(),
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
                primary_key=[["property_key"]],
            )
        ]
    )

    with patch("source_dropbox.source.DropboxClient", return_value=client):
        messages = list(SourceDropbox().read(Mock(), CONFIG, catalog))

    records = [message.record for message in messages if message.type == Type.RECORD]
    assert [(record.stream, record.data["field_value"]) for record in records] == [("file_properties", "Acme")]
    assert not hasattr(client, "files_download") or not client.files_download.called


def test_client_lists_file_properties_with_property_groups_and_pagination() -> None:
    sdk = Mock()
    sdk.file_properties_templates_list_for_user.return_value = Mock(template_ids=["ptid:contract"])

    def list_folder(**kwargs: object) -> Mock:
        # This validates the exact Dropbox SDK generated route argument type.
        # TemplateFilter.filter_none is a TemplateFilter concrete union value,
        # but this route expects TemplateFilterBase and rejects it in the
        # installed SDK.
        ListFolderArg(**kwargs)
        return Mock(
            entries=[_file(property_groups=[_group("ptid:contract", ("Customer", "Acme"))])],
            cursor="next",
            has_more=True,
        )

    sdk.files_list_folder.side_effect = list_folder
    sdk.files_list_folder_continue.return_value = Mock(entries=[], cursor="done", has_more=False)

    with patch("source_dropbox.dropbox_context.dropbox.Dropbox", return_value=sdk):
        client = DropboxClient(CONFIG)
        pages = list(client.iter_entries_with_property_groups(path="/Contracts", recursive=False))

    assert len(pages) == 2
    sdk.file_properties_templates_list_for_user.assert_called_once_with()
    sdk.files_list_folder.assert_called_once()
    include_property_groups = sdk.files_list_folder.call_args.kwargs["include_property_groups"]
    assert isinstance(include_property_groups, TemplateFilterBase)
    assert not isinstance(include_property_groups, TemplateFilter)
    TemplateFilterBase_validator.validate(include_property_groups)
    assert include_property_groups.is_filter_some()
    assert include_property_groups.get_filter_some() == ["ptid:contract"]
    sdk.files_list_folder.assert_called_once_with(
        path="/Contracts",
        recursive=False,
        include_deleted=False,
        include_property_groups=include_property_groups,
    )
    sdk.files_list_folder_continue.assert_called_once_with("next")


def test_client_skips_file_property_listing_when_no_templates_are_visible() -> None:
    sdk = Mock()
    sdk.file_properties_templates_list_for_user.return_value = Mock(template_ids=[])

    with patch("source_dropbox.dropbox_context.dropbox.Dropbox", return_value=sdk):
        client = DropboxClient(CONFIG)
        pages = list(client.iter_entries_with_property_groups(path="/Contracts", recursive=False))

    assert pages == []
    sdk.file_properties_templates_list_for_user.assert_called_once_with()
    sdk.files_list_folder.assert_not_called()
    sdk.files_list_folder_continue.assert_not_called()


def test_template_filter_none_reproduces_installed_sdk_route_type_mismatch() -> None:
    with pytest.raises(Exception, match="expected type dropbox.file_properties.TemplateFilterBase"):
        ListFolderArg(
            path="/Contracts",
            recursive=False,
            include_deleted=False,
            include_property_groups=TemplateFilter.filter_none,
        )


def test_client_rejects_malformed_file_property_template_ids() -> None:
    sdk = Mock()
    sdk.file_properties_templates_list_for_user.return_value = Mock(template_ids=[None])

    with patch("source_dropbox.dropbox_context.dropbox.Dropbox", return_value=sdk):
        client = DropboxClient(CONFIG)
        with pytest.raises(DropboxFilePropertiesError, match="malformed"):
            list(client.iter_entries_with_property_groups(path="/Contracts", recursive=False))
