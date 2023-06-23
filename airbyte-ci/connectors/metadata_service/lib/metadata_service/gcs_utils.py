import base64
import hashlib
from pathlib import Path

from google.cloud import storage

from metadata_service.constants import METADATA_FOLDER, METADATA_FILE_NAME, ICON_FILE_NAME


def get_metadata_remote_file_path(dockerRepository: str, version: str) -> str:
    """Get the path to the metadata file for a specific version of a connector.
    Args:
        dockerRepository (str): Name of the connector docker image.
        version (str): Version of the connector.
    Returns:
        str: Path to the metadata file.
    """
    return f"{METADATA_FOLDER}/{dockerRepository}/{version}/{METADATA_FILE_NAME}"


def get_icon_remote_file_path(dockerRepository: str, version: str) -> str:
    """Get the path to the icon file for a specific version of a connector.
    Args:
        dockerRepository (str): Name of the connector docker image.
        version (str): Version of the connector.
    Returns:
        str: Path to the icon file.
    """
    return f"{METADATA_FOLDER}/{dockerRepository}/{version}/{ICON_FILE_NAME}"


def compute_gcs_md5(file_name: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return base64.b64encode(hash_md5.digest()).decode("utf8")


def get_remote_blob(bucket: storage.bucket.Bucket, blob_path: str) -> storage.blob.Blob:
    """Get the blob object for a given path in a bucket.
    Args:
        bucket (storage.bucket.Bucket): Bucket object.
        blob_path (str): Path to the blob.
    Returns:
        storage.blob.Blob: Blob object.
    """
    return bucket.blob(blob_path)


def file_changed(local_file_path: Path, remote_blob: storage.blob.Blob) -> bool:
    """Check if a local file has changed compared to a remote blob.
    Args:
        local_file_path (Path): Path to the local file.
        remote_blob (storage.blob.Blob): Blob object.
    Returns:
        bool: True if the file has changed.
    """
    local_file_md5_hash = compute_gcs_md5(local_file_path)
    remote_blob_md5_hash = remote_blob.md5_hash if remote_blob.exists() else None

    print(f"Local {local_file_path} md5_hash: {local_file_md5_hash}")
    print(f"Remote {remote_blob.name} md5_hash: {remote_blob_md5_hash}")

    return local_file_md5_hash != remote_blob_md5_hash
