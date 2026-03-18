# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import io
import tempfile
import zipfile
from datetime import datetime
from unittest.mock import MagicMock, Mock

from source_gcs.helpers import GCSUploadableRemoteFile
from source_gcs.zip_helper import ZipHelper


def _make_zip_bytes(files: dict[str, str]) -> bytes:
    """Create a ZIP archive in memory. files is a mapping of {filename: content}."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _make_blob(zip_bytes: bytes) -> Mock:
    blob = Mock()
    blob.download_as_bytes.return_value = zip_bytes
    blob.size = len(zip_bytes)
    blob.public_url = "gs://bucket/test.zip"
    return blob


def _make_remote_file(uri: str = "gs://bucket/test.zip") -> GCSUploadableRemoteFile:
    return GCSUploadableRemoteFile(
        uri=uri,
        blob=MagicMock(),
        last_modified=datetime.today(),
        displayed_uri=uri,
    )


def test_get_gcs_remote_files(mocked_blob, zip_file, caplog):
    with tempfile.TemporaryDirectory() as tmp_dir_path:
        files = list(ZipHelper(mocked_blob, zip_file, tmp_dir_path).get_gcs_remote_files())
    assert len(files) == 1
    assert "Picking up file test.csv from zip archive" in caplog.text


def test_nested_directories_in_zip_are_traversed():
    """Files inside subdirectories within a ZIP must be yielded."""
    zip_bytes = _make_zip_bytes(
        {
            "top.csv": "top_level",
            "subdir/nested.csv": "nested_level",
            "subdir/deep/deep_nested.csv": "deep_level",
        }
    )

    blob = _make_blob(zip_bytes)
    remote_file = _make_remote_file()
    with tempfile.TemporaryDirectory() as tmp_dir_path:
        files = list(ZipHelper(blob, remote_file, tmp_dir_path).get_gcs_remote_files())

    filenames = sorted(f.uri.split("/")[-1] for f in files)
    assert filenames == ["deep_nested.csv", "nested.csv", "top.csv"]


def test_shared_tmp_dir_no_duplicates():
    """When multiple ZIPs extract to the same temp dir, each ZIP should only
    yield its own files, not files from previously extracted ZIPs."""
    zip1_bytes = _make_zip_bytes({"a.csv": "col\n1"})
    zip2_bytes = _make_zip_bytes({"b.csv": "col\n2"})
    zip3_bytes = _make_zip_bytes({"c.csv": "col\n3"})

    all_files = []
    with tempfile.TemporaryDirectory() as shared_tmp_dir_path:
        for zip_bytes in [zip1_bytes, zip2_bytes, zip3_bytes]:
            blob = _make_blob(zip_bytes)
            remote_file = _make_remote_file()
            files = list(ZipHelper(blob, remote_file, shared_tmp_dir_path).get_gcs_remote_files())
            all_files.extend(files)

    assert len(all_files) == 3


def test_filename_collision_shared_tmp_dir():
    """When two ZIPs contain a file with the same name and share a temp dir,
    the second extractall() silently overwrites the first file. Reading the
    file after each extraction should return that ZIP's content."""
    zip1_bytes = _make_zip_bytes({"data.csv": "zip1_content"})
    zip2_bytes = _make_zip_bytes({"data.csv": "zip2_content"})

    contents_per_zip = []
    with tempfile.TemporaryDirectory() as shared_tmp_dir_path:
        for zip_bytes in [zip1_bytes, zip2_bytes]:
            blob = _make_blob(zip_bytes)
            remote_file = _make_remote_file()
            files = list(ZipHelper(blob, remote_file, shared_tmp_dir_path).get_gcs_remote_files())
            zip_contents = []
            for f in files:
                with open(f.uri, "r") as fh:
                    zip_contents.append(fh.read())
            contents_per_zip.append(zip_contents)

    assert contents_per_zip[0] == ["zip1_content"]
    assert contents_per_zip[1] == ["zip2_content"]
