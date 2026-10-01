from __future__ import annotations

from typing import Any

from source_dropbox.client import DropboxClient, NamespaceInfo

from airbyte_cdk.sources.streams import Stream


class DropboxStream(Stream):
    def __init__(self, client: DropboxClient, config: dict[str, Any]) -> None:
        super().__init__()
        self.client = client
        self.config = config


def with_namespace(record: dict[str, Any], namespace: NamespaceInfo | None) -> dict[str, Any]:
    if namespace is None:
        return record
    namespaced = {**record, **namespace.provenance()}
    if isinstance(namespaced.get("entry_key"), str):
        namespaced["entry_key"] = f"{namespace.namespace_id}:{namespaced['entry_key']}"
    return namespaced
