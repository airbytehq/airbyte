import base64
import hashlib
from pathlib import Path

def compute_gcs_md5(file_name: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return base64.b64encode(hash_md5.digest()).decode("utf8")

def compute_sha256(file_name: str) -> str:
    hash_sha256 = hashlib.sha256()
    with Path.open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)

    return base64.b64encode(hash_sha256.digest()).decode("utf8")
