# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import base64
import hashlib
import zipfile
from pathlib import Path
from typing import List


def compute_gcs_md5(file_name: Path) -> str:
    hash_md5 = hashlib.md5()
    with Path.open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return base64.b64encode(hash_md5.digest()).decode("utf8")


def compute_sha256(file_name: Path) -> str:
    hash_sha256 = hashlib.sha256()
    with Path.open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)

    return base64.b64encode(hash_sha256.digest()).decode("utf8")


def create_zip_and_get_sha256(files_to_zip: List[Path], output_zip_path: Path) -> str:
    """Create a zip file from given files and return its SHA256 hash."""
    with zipfile.ZipFile(output_zip_path, "w") as zipf:
        for file_path in files_to_zip:
            if file_path.exists():
                zipf.write(filename=file_path, arcname=file_path.name)

    zip_sha256 = compute_sha256(output_zip_path)
    return zip_sha256
