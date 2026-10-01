from datetime import UTC, datetime

from dropbox.files import DeletedMetadata, FileMetadata, FolderMetadata
from source_dropbox.normalizer import normalize_entry


def test_normalize_file() -> None:
    entry = FileMetadata(
        name="example.txt",
        id="id:file1",
        client_modified=datetime(2026, 8, 3, tzinfo=UTC),
        server_modified=datetime(2026, 8, 3, tzinfo=UTC),
        rev="0123456789abcdef",
        size=12,
        path_lower="/example.txt",
        path_display="/example.txt",
        content_hash="0123456789abcdef" * 4,
        is_downloadable=True,
    )

    record = normalize_entry(entry)

    assert record["entry_key"] == "file:id:file1"
    assert record["entry_type"] == "file"
    assert record["operation"] == "upsert"


def test_normalize_folder() -> None:
    entry = FolderMetadata(
        name="docs",
        id="id:folder1",
        path_lower="/docs",
        path_display="/Docs",
    )

    record = normalize_entry(entry)

    assert record["entry_key"] == "folder:id:folder1"
    assert record["entry_type"] == "folder"


def test_normalize_deleted_entry() -> None:
    entry = DeletedMetadata(
        name="old.txt",
        path_lower="/old.txt",
        path_display="/old.txt",
    )

    record = normalize_entry(entry)

    assert record["entry_key"] == "deleted:/old.txt"
    assert record["operation"] == "delete"
