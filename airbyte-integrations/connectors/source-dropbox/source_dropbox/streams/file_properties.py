from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from dropbox.files import FileMetadata
from source_dropbox.client import DropboxFilePropertiesError
from source_dropbox.normalizer import normalize_file_property
from source_dropbox.streams.base import DropboxStream, with_namespace

from airbyte_cdk.models import SyncMode


class FileProperties(DropboxStream):
    """Full-refresh File Properties inventory, one record per field value."""

    name = "file_properties"
    primary_key = "property_key"

    @property
    def supports_incremental(self) -> bool:
        return False

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: list[str] | None = None,
        stream_slice: Mapping[str, Any] | None = None,
        stream_state: Mapping[str, Any] | None = None,
    ) -> Iterable[Mapping[str, Any]]:
        template_names: dict[str, str | None] = {}
        seen: dict[str, Mapping[str, Any]] = {}
        for page in self.client.iter_entries_with_property_groups(
            path=self.config.get("path", ""),
            recursive=self.config.get("recursive", True),
        ):
            for entry in page.entries:
                if not isinstance(entry, FileMetadata):
                    continue
                for property_group in entry.property_groups or []:
                    template_id = getattr(property_group, "template_id", None)
                    if not isinstance(template_id, str) or not template_id:
                        raise DropboxFilePropertiesError("Dropbox returned a File Properties group without a template ID.")
                    if template_id not in template_names:
                        template_names[template_id] = self._template_name(template_id)
                    for field in property_group.fields or []:
                        record = normalize_file_property(
                            entry,
                            property_group,
                            field,
                            template_name=template_names[template_id],
                        )
                        property_key = record["property_key"]
                        duplicate = seen.get(property_key)
                        if duplicate == record:
                            continue
                        if duplicate is not None:
                            raise DropboxFilePropertiesError(
                                f"Dropbox returned conflicting duplicate File Properties records for property key {property_key}."
                            )
                        seen[property_key] = record
                        yield with_namespace(dict(record), page.namespace)

    def _template_name(self, template_id: str) -> str | None:
        template = self.client.get_property_template(template_id)
        name = getattr(template, "name", None) if template is not None else None
        return name if isinstance(name, str) else None
