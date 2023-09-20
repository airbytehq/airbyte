#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from google.cloud import storage
from google.oauth2 import service_account
from metadata_service.constants import (
    DOC_FILE_NAME,
    DOC_INAPP_FILE_NAME,
    DOCS_FOLDER_PATH,
    ICON_FILE_NAME,
    METADATA_FILE_NAME,
    METADATA_FOLDER,
)
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.models.transform import to_json_sanitized_dict
from metadata_service.validators.metadata_validator import POST_UPLOAD_VALIDATORS, ValidatorOptions, validate_and_load
from pydash.objects import get


@dataclass(frozen=True)
class UploadedFile:
    id: str
    uploaded: bool
    description: str
    blob_id: Optional[str]


@dataclass(frozen=True)
class MetadataUploadInfo:
    metadata_uploaded: bool
    metadata_file_path: str
    uploaded_files: List[UploadedFile]


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


def get_doc_remote_file_path(dockerRepository: str, version: str, inapp: bool) -> str:
    """Get the path to the icon file for a specific version of a connector.

    Args:
        dockerRepository (str): Name of the connector docker image.
        version (str): Version of the connector.
    Returns:
        str: Path to the icon file.
    """
    return f"{METADATA_FOLDER}/{dockerRepository}/{version}/{DOC_INAPP_FILE_NAME if inapp else DOC_FILE_NAME}"


def get_doc_local_file_path(metadata: ConnectorMetadataDefinitionV0, docs_path: Path, inapp: bool) -> Path:
    pattern = re.compile(r"^https://docs\.airbyte\.com/(.+)$")
    match = pattern.search(metadata.data.documentationUrl)
    if match:
        extension = ".inapp.md" if inapp else ".md"
        return (docs_path / match.group(1)).with_suffix(extension)
    return None


def compute_gcs_md5(file_name: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return base64.b64encode(hash_md5.digest()).decode("utf8")


def _save_blob_to_gcs(blob_to_save: storage.blob.Blob, file_path: str, disable_cache: bool = False) -> bool:
    """Uploads a file to the bucket."""
    print(f"Uploading {file_path} to {blob_to_save.name}...")

    # Set Cache-Control header to no-cache to avoid caching issues
    # This is IMPORTANT because if we don't set this header, the metadata file will be cached by GCS
    # and the next time we try to download it, we will get the stale version
    if disable_cache:
        blob_to_save.cache_control = "no-cache"

    blob_to_save.upload_from_filename(file_path)

    return True


def upload_file_if_changed(
    local_file_path: Path, bucket: storage.bucket.Bucket, blob_path: str, disable_cache: bool = False
) -> Tuple[bool, str]:
    local_file_md5_hash = compute_gcs_md5(local_file_path)
    remote_blob = bucket.blob(blob_path)

    # reload the blob to get the md5_hash
    if remote_blob.exists():
        remote_blob.reload()

    remote_blob_md5_hash = remote_blob.md5_hash if remote_blob.exists() else None

    print(f"Local {local_file_path} md5_hash: {local_file_md5_hash}")
    print(f"Remote {blob_path} md5_hash: {remote_blob_md5_hash}")

    if local_file_md5_hash != remote_blob_md5_hash:
        uploaded = _save_blob_to_gcs(remote_blob, local_file_path, disable_cache=disable_cache)
        return uploaded, remote_blob.id

    return False, remote_blob.id


def _latest_upload(metadata: ConnectorMetadataDefinitionV0, bucket: storage.bucket.Bucket, metadata_file_path: Path) -> Tuple[bool, str]:
    latest_path = get_metadata_remote_file_path(metadata.data.dockerRepository, "latest")
    return upload_file_if_changed(metadata_file_path, bucket, latest_path, disable_cache=True)


def _version_upload(metadata: ConnectorMetadataDefinitionV0, bucket: storage.bucket.Bucket, metadata_file_path: Path) -> Tuple[bool, str]:
    version_path = get_metadata_remote_file_path(metadata.data.dockerRepository, metadata.data.dockerImageTag)
    return upload_file_if_changed(metadata_file_path, bucket, version_path, disable_cache=True)


def _icon_upload(metadata: ConnectorMetadataDefinitionV0, bucket: storage.bucket.Bucket, metadata_file_path: Path) -> Tuple[bool, str]:
    local_icon_path = metadata_file_path.parent / ICON_FILE_NAME
    latest_icon_path = get_icon_remote_file_path(metadata.data.dockerRepository, "latest")
    if not local_icon_path.exists():
        return False, f"No Icon found at {local_icon_path}"
    return upload_file_if_changed(local_icon_path, bucket, latest_icon_path)


def _doc_upload(
    metadata: ConnectorMetadataDefinitionV0, bucket: storage.bucket.Bucket, docs_path: Path, latest: bool, inapp: bool
) -> Tuple[bool, str]:
    local_doc_path = get_doc_local_file_path(metadata, docs_path, inapp)
    if not local_doc_path:
        return False, f"Metadata does not contain a valid Airbyte documentation url, skipping doc upload."

    remote_doc_path = get_doc_remote_file_path(metadata.data.dockerRepository, "latest" if latest else metadata.data.dockerImageTag, inapp)

    if local_doc_path.exists():
        doc_uploaded, doc_blob_id = upload_file_if_changed(local_doc_path, bucket, remote_doc_path)
    else:
        if inapp:
            doc_uploaded, doc_blob_id = False, f"No inapp doc found at {local_doc_path}, skipping inapp doc upload."
        else:
            raise FileNotFoundError(f"Expected to find connector doc file at {local_doc_path}, but none was found.")

    return doc_uploaded, doc_blob_id


def create_prerelease_metadata_file(metadata_file_path: Path, validator_opts: ValidatorOptions) -> Path:
    metadata, error = validate_and_load(metadata_file_path, [], validator_opts)
    if metadata is None:
        raise ValueError(f"Metadata file {metadata_file_path} is invalid for uploading: {error}")

    # replace any dockerImageTag references with the actual tag
    # this includes metadata.data.dockerImageTag, metadata.data.registries[].dockerImageTag
    # where registries is a dictionary of registry name to registry object
    metadata_dict = to_json_sanitized_dict(metadata, exclude_none=True)
    metadata_dict["data"]["dockerImageTag"] = validator_opts.prerelease_tag
    for registry in get(metadata_dict, "data.registries", {}).values():
        if "dockerImageTag" in registry:
            registry["dockerImageTag"] = validator_opts.prerelease_tag

    # write metadata to yaml file in system tmp folder
    tmp_metadata_file_path = Path("/tmp") / metadata.data.dockerRepository / validator_opts.prerelease_tag / METADATA_FILE_NAME
    tmp_metadata_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp_metadata_file_path, "w") as f:
        yaml.dump(metadata_dict, f)

    return tmp_metadata_file_path


def upload_metadata_to_gcs(bucket_name: str, metadata_file_path: Path, validator_opts: ValidatorOptions) -> MetadataUploadInfo:
    """Upload a metadata file to a GCS bucket.

    If the per 'version' key already exists it won't be overwritten.
    Also updates the 'latest' key on each new version.

    Args:
        bucket_name (str): Name of the GCS bucket to which the metadata file will be uploade.
        metadata_file_path (Path): Path to the metadata file.
        service_account_file_path (Path): Path to the JSON file with the service account allowed to read and write on the bucket.
        prerelease_tag (Optional[str]): Whether the connector is a prerelease_tag or not.
    Returns:
        Tuple[bool, str]: Whether the metadata file was uploaded and its blob id.
    """
    if validator_opts.prerelease_tag:
        metadata_file_path = create_prerelease_metadata_file(metadata_file_path, validator_opts)

    metadata, error = validate_and_load(metadata_file_path, POST_UPLOAD_VALIDATORS, validator_opts)

    if metadata is None:
        raise ValueError(f"Metadata file {metadata_file_path} is invalid for uploading: {error}")

    service_account_info = json.loads(os.environ.get("GCS_CREDENTIALS"))
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    docs_path = Path(validator_opts.docs_path)

    icon_uploaded, icon_blob_id = _icon_upload(metadata, bucket, metadata_file_path)

    version_uploaded, version_blob_id = _version_upload(metadata, bucket, metadata_file_path)

    doc_version_uploaded, doc_version_blob_id = _doc_upload(metadata, bucket, docs_path, False, False)
    doc_inapp_version_uploaded, doc_inapp_version_blob_id = _doc_upload(metadata, bucket, docs_path, False, True)

    if not validator_opts.prerelease_tag:
        latest_uploaded, latest_blob_id = _latest_upload(metadata, bucket, metadata_file_path)
        doc_latest_uploaded, doc_latest_blob_id = _doc_upload(metadata, bucket, docs_path, True, False)
        doc_inapp_latest_uploaded, doc_inapp_latest_blob_id = _doc_upload(metadata, bucket, docs_path, True, True)
    else:
        latest_uploaded, latest_blob_id = False, None
        doc_latest_uploaded, doc_latest_blob_id = doc_inapp_latest_uploaded, doc_inapp_latest_blob_id = False, None

    return MetadataUploadInfo(
        metadata_uploaded=version_uploaded or latest_uploaded,
        metadata_file_path=str(metadata_file_path),
        uploaded_files=[
            UploadedFile(
                id="version_metadata",
                uploaded=version_uploaded,
                description="versioned metadata",
                blob_id=version_blob_id,
            ),
            UploadedFile(
                id="latest_metadata",
                uploaded=latest_uploaded,
                description="latest metadata",
                blob_id=latest_blob_id,
            ),
            UploadedFile(
                id="icon",
                uploaded=icon_uploaded,
                description="icon",
                blob_id=icon_blob_id,
            ),
            UploadedFile(
                id="doc_version",
                uploaded=doc_version_uploaded,
                description="versioned doc",
                blob_id=doc_version_blob_id,
            ),
            UploadedFile(
                id="doc_latest",
                uploaded=doc_latest_uploaded,
                description="latest doc",
                blob_id=doc_latest_blob_id,
            ),
            UploadedFile(
                id="doc_inapp_version",
                uploaded=doc_inapp_version_uploaded,
                description="versioned inapp doc",
                blob_id=doc_inapp_version_blob_id,
            ),
            UploadedFile(
                id="doc_inapp_latest",
                uploaded=doc_inapp_latest_uploaded,
                description="latest inapp doc",
                blob_id=doc_inapp_latest_blob_id,
            ),
        ],
    )

def upload_all_docs_to_gcs(connectors_dir: Path, docs_dir: Path, bucket_name: str):
    service_account_info = json.loads(os.environ.get("GCS_CREDENTIALS"))
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)

    # A function to extract type and name from the folder name
    def parse_folder_name(folder_name: str) -> (str, str):
        if "scaffol" in folder_name:
            return None, None
        elif folder_name.startswith('source-'):
            return 'source', folder_name[len('source-'):]
        elif folder_name.startswith('destination-'):
            return 'destination', folder_name[len('destination-'):]
        else:
            return None, None

    def read_metadata_yaml(path: Path) -> ConnectorMetadataDefinitionV0:
        return ConnectorMetadataDefinitionV0.parse_obj(yaml.safe_load(path.read_text()))

    def get_doc_paths(metadata: ConnectorMetadataDefinitionV0, connector_name: str) -> (str, str):
        sub_dir = f"{metadata.data.connectorType}s"
        doc_file_name = metadata.data.documentationUrl.split('/')[-1]
        doc_path = docs_dir / sub_dir / f"{doc_file_name}.md"
        inapp_doc_path = docs_dir / sub_dir / f"{doc_file_name}.inapp.md"

        # some connectors like source-appstore-singer have an old documentationUrl, so we need to check with the connector name too
        alt_doc_path = docs_dir / sub_dir / f"{connector_name}.md"
        alt_inapp_doc_path = docs_dir / sub_dir / f"{connector_name}.inapp.md"

        if (doc_path.exists()):
            return doc_path, inapp_doc_path if inapp_doc_path.exists() else None
        elif (alt_doc_path.exists()):
            return alt_doc_path, alt_inapp_doc_path if alt_inapp_doc_path.exists() else None
        else:
            return None, None

    excluded_connectors = []
    connector_infos = []
    
    for connector_dir in connectors_dir.iterdir():
        if connector_dir.is_dir():
            connector_type, connector_name = parse_folder_name(connector_dir.name)
            if connector_type and connector_name:  # Skip folders that don't match the pattern
                metadata_file_path = connector_dir / METADATA_FILE_NAME
                if metadata_file_path.exists():
                    metadata = read_metadata_yaml(metadata_file_path)
                    doc_path, inapp_doc_path = get_doc_paths(metadata, connector_name)  # 'source' becomes 'sources', 'destination' becomes 'destinations'
                    
                    if not doc_path:
                        raise FileNotFoundError(f"Expected to find connector doc file at {doc_path} for metadata file at {metadata_file_path}, but none was found.")

                    directory_info = {
                        'type': connector_type,
                        'name': connector_name,
                        'path': connector_dir,
                        'metadata': metadata,
                        'doc_path': doc_path
                    }
                    if inapp_doc_path:
                        directory_info['inapp_doc_path'] = inapp_doc_path

                    connector_infos.append(directory_info)
                else:
                    excluded_connectors.append(connector_dir.name)

    print("excluded_connectors: ", excluded_connectors)
    print(f"Found docs for {len(connector_infos)} connectors")

    # Example to show uploading the docs for a single connector. Comment these lines out when uploading all docs.
    github_connector_info = [connector_info for connector_info in connector_infos if connector_info['name'] == "github"][0]
    # versioned uploads
    _doc_upload(github_connector_info['metadata'], bucket, github_connector_info['doc_path'], False, False)
    _doc_upload(github_connector_info['metadata'], bucket, github_connector_info['doc_path'], False, True)
    # latest uploads
    _doc_upload(github_connector_info['metadata'], bucket, github_connector_info['doc_path'], True, False)
    _doc_upload(github_connector_info['metadata'], bucket, github_connector_info['doc_path'], True, True)

    # Uncomment these lines to upload all docs
    # for connector_info in connector_infos:
    #     print(f"Uploading docs for connector {connector_info['name']}")
    #     # versioned uploads
    #     _doc_upload(connector_info['metadata'], bucket, connector_info['doc_path'], False, False)
    #     _doc_upload(connector_info['metadata'], bucket, connector_info['doc_path'], False, True)
    #     # latest uploads
    #     _doc_upload(connector_info['metadata'], bucket, connector_info['doc_path'], True, False)
    #     _doc_upload(connector_info['metadata'], bucket, connector_info['doc_path'], True, True)
