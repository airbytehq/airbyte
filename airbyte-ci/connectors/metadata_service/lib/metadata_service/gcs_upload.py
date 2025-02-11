#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple

import git
import requests
import yaml
from google.cloud import storage
from google.oauth2 import service_account
from pydash import set_
from pydash.objects import get

from metadata_service.constants import (
    COMPONENTS_PY_FILE_NAME,
    COMPONENTS_ZIP_FILE_NAME,
    COMPONENTS_ZIP_SHA256_FILE_NAME,
    DOC_FILE_NAME,
    DOC_INAPP_FILE_NAME,
    ICON_FILE_NAME,
    LATEST_GCS_FOLDER_NAME,
    MANIFEST_FILE_NAME,
    METADATA_FILE_NAME,
    METADATA_FOLDER,
    RELEASE_CANDIDATE_GCS_FOLDER_NAME,
)
from metadata_service.helpers.files import compute_gcs_md5, create_zip_and_get_sha256
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.models.generated.GitInfo import GitInfo
from metadata_service.models.transform import to_json_sanitized_dict
from metadata_service.validators.metadata_validator import POST_UPLOAD_VALIDATORS, ValidatorOptions, validate_and_load

# 🧩 TYPES


@dataclass(frozen=True)
class UploadedFile:
    id: str
    uploaded: bool
    blob_id: Optional[str]


@dataclass(frozen=True)
class DeletedFile:
    id: str
    deleted: bool
    description: str
    blob_id: Optional[str]


@dataclass(frozen=True)
class MetadataUploadInfo:
    metadata_uploaded: bool
    metadata_file_path: str
    uploaded_files: List[UploadedFile]


@dataclass(frozen=True)
class MetadataDeleteInfo:
    metadata_deleted: bool
    deleted_files: List[DeletedFile]


class MaybeUpload(NamedTuple):
    uploaded: bool
    blob_id: str


@dataclass
class ManifestOnlyFilePaths:
    zip_file_path: Path | None
    sha256_file_path: Path | None
    sha256: str | None
    manifest_file_path: Path


# 🛣️ FILES AND PATHS


def get_doc_local_file_path(metadata: ConnectorMetadataDefinitionV0, docs_path: Path, inapp: bool) -> Optional[Path]:
    pattern = re.compile(r"^https://docs\.airbyte\.com/(.+)$")
    match = pattern.search(metadata.data.documentationUrl)
    if match:
        extension = ".inapp.md" if inapp else ".md"
        return (docs_path / match.group(1)).with_suffix(extension)
    return None


def get_manifest_only_file_paths(working_directory: Path) -> ManifestOnlyFilePaths:
    """Create a zip file for components if they exist and return its SHA256 hash."""
    yaml_manifest_file_path = working_directory / MANIFEST_FILE_NAME
    components_py_file_path = working_directory / COMPONENTS_PY_FILE_NAME

    if not components_py_file_path.exists():
        return ManifestOnlyFilePaths(
            zip_file_path=None,
            sha256_file_path=None,
            sha256=None,
            manifest_file_path=yaml_manifest_file_path,
        )

    with (
        tempfile.NamedTemporaryFile(mode="wb", suffix=".zip", delete=False) as zip_tmp_file,
        tempfile.NamedTemporaryFile(mode="w", suffix=".sha256", delete=False) as sha256_tmp_file,
    ):
        python_components_zip_file_path = Path(zip_tmp_file.name)
        python_components_zip_sha256_file_path = Path(sha256_tmp_file.name)

        files_to_zip: List[Path] = [components_py_file_path, yaml_manifest_file_path]
        components_zip_sha256 = create_zip_and_get_sha256(files_to_zip, python_components_zip_file_path)
        sha256_tmp_file.write(components_zip_sha256)

        return ManifestOnlyFilePaths(
            zip_file_path=python_components_zip_file_path,
            sha256_file_path=python_components_zip_sha256_file_path,
            sha256=components_zip_sha256,
            manifest_file_path=yaml_manifest_file_path,
        )


def _write_metadata_to_tmp_file(metadata_dict: dict) -> Path:
    """Write the metadata to a temporary file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp_file:
        yaml.dump(metadata_dict, tmp_file)
        return Path(tmp_file.name)


# 🛠️ HELPERS


def _get_storage_client() -> storage.Client:
    """Get the GCS storage client using credentials form GCS_CREDENTIALS env variable."""
    gcs_creds = os.environ.get("GCS_CREDENTIALS")
    if not gcs_creds:
        raise ValueError("Please set the GCS_CREDENTIALS env var.")

    service_account_info = json.loads(gcs_creds)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    return storage.Client(credentials=credentials)


def _safe_load_metadata_file(metadata_file_path: Path) -> dict:
    try:
        metadata = yaml.safe_load(metadata_file_path.read_text())
        if metadata is None or not isinstance(metadata, dict):
            raise ValueError(f"Validation error: Metadata file {metadata_file_path} is invalid yaml.")
        return metadata
    except Exception as e:
        raise ValueError(f"Validation error: Metadata file {metadata_file_path} is invalid yaml: {e}")


def _any_uploaded(uploaded_files: List[UploadedFile], keys: List[str]) -> bool:
    """Check if the list of uploaded files contains any of the provided keys."""
    for uploaded_file in uploaded_files:
        if uploaded_file.id in keys:
            return True
    return False


def _commit_to_git_info(commit: git.Commit) -> GitInfo:
    return GitInfo(
        commit_sha=commit.hexsha,
        commit_timestamp=commit.authored_datetime,
        commit_author=commit.author.name,
        commit_author_email=commit.author.email,
    )


def _get_git_info_for_file(original_metadata_file_path: Path) -> Optional[GitInfo]:
    """
    Add additional information to the metadata file before uploading it to GCS.

    e.g. The git commit hash, the date of the commit, the author of the commit, etc.

    """
    try:
        repo = git.Repo(search_parent_directories=True)

        # get the commit hash for the last commit that modified the metadata file
        commit_sha = repo.git.log("-1", "--format=%H", str(original_metadata_file_path))

        commit = repo.commit(commit_sha)
        return _commit_to_git_info(commit)
    except git.exc.InvalidGitRepositoryError:
        logging.warning(f"Metadata file {original_metadata_file_path} is not in a git repository, skipping author info attachment.")
        return None
    except git.exc.GitCommandError as e:
        if "unknown revision or path not in the working tree" in str(e):
            logging.warning(f"Metadata file {original_metadata_file_path} is not tracked by git, skipping author info attachment.")
            return None
        else:
            raise e


# 🚀 UPLOAD


def _save_blob_to_gcs(blob_to_save: storage.blob.Blob, file_path: Path, disable_cache: bool = False) -> bool:
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
) -> MaybeUpload:
    """Upload a file to GCS if it has changed."""
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
        return MaybeUpload(uploaded, remote_blob.id)

    return MaybeUpload(False, remote_blob.id)


def _file_upload(
    local_path: Path | None,
    gcp_connector_dir: str,
    bucket: storage.bucket.Bucket,
    file_key: str,
    *,
    upload_as_version: bool,
    upload_as_latest: bool,
    skip_if_not_exists: bool = True,
    disable_cache: bool = False,
    version_folder: Optional[str] = None,
    override_destination_file_name: str | None = None,
) -> tuple[UploadedFile, UploadedFile]:
    """Upload a file to GCS.

    Optionally upload it as a versioned file and/or as the latest version.

    Args:
        local_path: Path to the file to upload.
        gcp_connector_dir: Path to the connector folder in GCS. This is the parent folder,
            containing the versioned and "latest" folders as its subdirectories.
        bucket: GCS bucket to upload the file to.
        upload_as_version: The version to upload the file as or 'False' to skip uploading
            the versioned copy.
        upload_as_latest: Whether to upload the file as the latest version.
        skip_if_not_exists: Whether to skip the upload if the file does not exist. Otherwise,
            an exception will be raised if the file does not exist.

    Returns: Tuple of two UploadInfo objects, each containing a boolean indicating whether the file was
        uploaded, the blob id, and the description. The first tuple is for the versioned file, the second for the
        latest file.
    """
    if upload_as_version and not version_folder:
        raise ValueError("version_folder must be provided if upload_as_version is True")

    latest_file_key = f"latest_{file_key}"
    versioned_file_key = f"versioned_{file_key}"
    versioned_file_info = UploadedFile(id=versioned_file_key, uploaded=False, blob_id=None)
    latest_file_info = UploadedFile(id=latest_file_key, uploaded=False, blob_id=None)
    if not local_path or not local_path.exists():
        msg = f"Expected to find file at {local_path}, but none was found."
        if skip_if_not_exists:
            logging.warning(msg)
            return versioned_file_info, latest_file_info

        raise FileNotFoundError(msg)

    file_name = local_path.name if override_destination_file_name is None else override_destination_file_name

    if upload_as_version:
        remote_upload_path = f"{gcp_connector_dir}/{version_folder}"
        versioned_uploaded, versioned_blob_id = upload_file_if_changed(
            local_file_path=local_path,
            bucket=bucket,
            blob_path=f"{remote_upload_path}/{file_name}",
            disable_cache=disable_cache,
        )
        versioned_file_info = UploadedFile(id=versioned_file_key, uploaded=versioned_uploaded, blob_id=versioned_blob_id)

    if upload_as_latest:
        remote_upload_path = f"{gcp_connector_dir}/{LATEST_GCS_FOLDER_NAME}"
        latest_uploaded, latest_blob_id = upload_file_if_changed(
            local_file_path=local_path,
            bucket=bucket,
            blob_path=f"{remote_upload_path}/{file_name}",
            disable_cache=disable_cache,
        )
        latest_file_info = UploadedFile(id=latest_file_key, uploaded=latest_uploaded, blob_id=latest_blob_id)

    return versioned_file_info, latest_file_info


# 🔧 METADATA MODIFICATIONS


def _apply_prerelease_overrides(metadata_dict: dict, validator_opts: ValidatorOptions) -> dict:
    """Apply any prerelease overrides to the metadata file before uploading it to GCS."""
    if validator_opts.prerelease_tag is None:
        return metadata_dict

    # replace any dockerImageTag references with the actual tag
    # this includes metadata.data.dockerImageTag, metadata.data.registryOverrides[].dockerImageTag
    # where registries is a dictionary of registry name to registry object
    metadata_dict["data"]["dockerImageTag"] = validator_opts.prerelease_tag
    for registry in get(metadata_dict, "data.registryOverrides", {}).values():
        if "dockerImageTag" in registry:
            registry["dockerImageTag"] = validator_opts.prerelease_tag

    return metadata_dict


def _apply_author_info_to_metadata_file(metadata_dict: dict, original_metadata_file_path: Path) -> dict:
    """Apply author info to the metadata file before uploading it to GCS."""
    git_info = _get_git_info_for_file(original_metadata_file_path)
    if git_info:
        # Apply to the nested / optional field at metadata.data.generated.git
        git_info_dict = to_json_sanitized_dict(git_info, exclude_none=True)
        metadata_dict = set_(metadata_dict, "data.generated.git", git_info_dict)
    return metadata_dict


def _apply_python_components_sha_to_metadata_file(
    metadata_dict: dict,
    python_components_sha256: Optional[str] = None,
) -> dict:
    """If a `components.py` file is required, store the necessary information in the metadata.

    This adds a `required=True` flag and the sha256 hash of the `python_components.zip` file.

    This is a no-op if `python_components_sha256` is not provided.
    """
    if python_components_sha256:
        metadata_dict = set_(metadata_dict, "data.generated.pythonComponents.required", True)
        metadata_dict = set_(
            metadata_dict,
            "data.generated.pythonComponents.sha256",
            python_components_sha256,
        )

    return metadata_dict


def _apply_sbom_url_to_metadata_file(metadata_dict: dict) -> dict:
    """Apply sbom url to the metadata file before uploading it to GCS."""
    try:
        sbom_url = f"https://connectors.airbyte.com/files/sbom/{metadata_dict['data']['dockerRepository']}/{metadata_dict['data']['dockerImageTag']}.spdx.json"
    except KeyError:
        return metadata_dict
    response = requests.head(sbom_url)
    if response.ok:
        metadata_dict = set_(metadata_dict, "data.generated.sbomUrl", sbom_url)
    return metadata_dict


def _apply_modifications_to_metadata_file(
    original_metadata_file_path: Path,
    validator_opts: ValidatorOptions,
    components_zip_sha256: str | None = None,
) -> Path:
    """Apply modifications to the metadata file before uploading it to GCS.

    e.g. The git commit hash, the date of the commit, the author of the commit, etc.

    Args:
        original_metadata_file_path (Path): Path to the original metadata file.
        validator_opts (ValidatorOptions): Options to use when validating the metadata file.
        components_zip_sha256 (str): The sha256 hash of the `python_components.zip` file. This is
            required if the `python_components.zip` file is present.
    """
    metadata = _safe_load_metadata_file(original_metadata_file_path)
    metadata = _apply_prerelease_overrides(metadata, validator_opts)
    metadata = _apply_author_info_to_metadata_file(metadata, original_metadata_file_path)
    metadata = _apply_python_components_sha_to_metadata_file(metadata, components_zip_sha256)
    metadata = _apply_sbom_url_to_metadata_file(metadata)
    return _write_metadata_to_tmp_file(metadata)


# 💎 Main Logic


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
    # Get our working directory
    working_directory = metadata_file_path.parent
    manifest_only_file_info = get_manifest_only_file_paths(working_directory)

    metadata_file_path = _apply_modifications_to_metadata_file(
        original_metadata_file_path=metadata_file_path,
        validator_opts=validator_opts,
        components_zip_sha256=manifest_only_file_info.sha256,
    )

    metadata, error = validate_and_load(metadata_file_path, POST_UPLOAD_VALIDATORS, validator_opts)
    if metadata is None:
        raise ValueError(f"Metadata file {metadata_file_path} is invalid for uploading: {error}")

    is_pre_release = validator_opts.prerelease_tag is not None
    is_release_candidate = "-rc" in metadata.data.dockerImageTag
    should_upload_release_candidate = is_release_candidate and not is_pre_release
    should_upload_latest = not is_release_candidate and not is_pre_release

    storage_client = _get_storage_client()
    bucket = storage_client.bucket(bucket_name)
    docs_path = Path(validator_opts.docs_path)
    gcp_connector_dir = f"{METADATA_FOLDER}/{metadata.data.dockerRepository}"

    # Upload version metadata and doc
    # If the connector is a pre-release, we use the pre-release tag as the version
    # Otherwise, we use the dockerImageTag from the metadata
    version_folder = metadata.data.dockerImageTag if not is_pre_release else validator_opts.prerelease_tag

    # Start uploading files
    uploaded_files = []

    # Metadata upload
    metadata_files_uploaded = _file_upload(
        file_key="metadata",
        local_path=metadata_file_path,
        gcp_connector_dir=gcp_connector_dir,
        bucket=bucket,
        version_folder=version_folder,
        upload_as_version=True,
        upload_as_latest=should_upload_latest,
        disable_cache=True,
        override_destination_file_name=METADATA_FILE_NAME,
    )
    uploaded_files.extend(metadata_files_uploaded)

    # Release candidate upload
    # We just upload the current metadata to the "release_candidate" path
    # The doc and inapp doc are not uploaded, which means that the release candidate will still point to the latest doc
    if should_upload_release_candidate:
        release_candidate_files_uploaded = _file_upload(
            file_key="release_candidate",
            local_path=metadata_file_path,
            gcp_connector_dir=gcp_connector_dir,
            bucket=bucket,
            version_folder=RELEASE_CANDIDATE_GCS_FOLDER_NAME,
            upload_as_version=True,
            upload_as_latest=False,
            disable_cache=True,
            override_destination_file_name=METADATA_FILE_NAME,
        )
        uploaded_files.extend(release_candidate_files_uploaded)

    # Icon upload

    icon_files_uploaded = _file_upload(
        file_key="icon",
        local_path=working_directory / ICON_FILE_NAME,
        gcp_connector_dir=gcp_connector_dir,
        bucket=bucket,
        upload_as_version=False,
        upload_as_latest=should_upload_latest,
    )
    uploaded_files.extend(icon_files_uploaded)

    # Doc upload

    local_doc_path = get_doc_local_file_path(metadata, docs_path, inapp=False)
    doc_files_uploaded = _file_upload(
        file_key="doc",
        local_path=local_doc_path,
        gcp_connector_dir=gcp_connector_dir,
        bucket=bucket,
        upload_as_version=True,
        version_folder=version_folder,
        upload_as_latest=should_upload_latest,
        override_destination_file_name=DOC_FILE_NAME,
    )
    uploaded_files.extend(doc_files_uploaded)

    local_inapp_doc_path = get_doc_local_file_path(metadata, docs_path, inapp=True)
    inapp_doc_files_uploaded = _file_upload(
        file_key="inapp_doc",
        local_path=local_inapp_doc_path,
        gcp_connector_dir=gcp_connector_dir,
        bucket=bucket,
        upload_as_version=True,
        version_folder=version_folder,
        upload_as_latest=should_upload_latest,
        override_destination_file_name=DOC_INAPP_FILE_NAME,
    )
    uploaded_files.extend(inapp_doc_files_uploaded)

    # Manifest and components upload

    manifest_files_uploaded = _file_upload(
        file_key="manifest",
        local_path=manifest_only_file_info.manifest_file_path,
        gcp_connector_dir=gcp_connector_dir,
        bucket=bucket,
        upload_as_version=True,
        version_folder=version_folder,
        upload_as_latest=should_upload_latest,
        override_destination_file_name=MANIFEST_FILE_NAME,
    )
    uploaded_files.extend(manifest_files_uploaded)

    components_zip_sha256_files_uploaded = _file_upload(
        file_key="components_zip_sha256",
        local_path=manifest_only_file_info.sha256_file_path,
        gcp_connector_dir=gcp_connector_dir,
        bucket=bucket,
        upload_as_version=True,
        version_folder=version_folder,
        upload_as_latest=should_upload_latest,
        override_destination_file_name=COMPONENTS_ZIP_SHA256_FILE_NAME,
    )
    uploaded_files.extend(components_zip_sha256_files_uploaded)

    components_zip_files_uploaded = _file_upload(
        file_key="components_zip",
        local_path=manifest_only_file_info.zip_file_path,
        gcp_connector_dir=gcp_connector_dir,
        bucket=bucket,
        upload_as_version=True,
        version_folder=version_folder,
        upload_as_latest=should_upload_latest,
        override_destination_file_name=COMPONENTS_ZIP_FILE_NAME,
    )
    uploaded_files.extend(components_zip_files_uploaded)

    return MetadataUploadInfo(
        uploaded_files=uploaded_files,
        metadata_file_path=str(metadata_file_path),
        metadata_uploaded=_any_uploaded(
            uploaded_files,
            [
                "latest_metadata",
                "version_metadata",
                "version_release_candidate",
            ],
        ),
    )


def delete_release_candidate_from_gcs(bucket_name: str, docker_repository: str, connector_version: str) -> MetadataDeleteInfo:
    """
    Delete a release candidate from a GCS bucket.
    The release candidate and version metadata file will be deleted.
    We first check that the release candidate metadata file hash matches the version metadata file hash.
    Args:
        bucket_name (str): Name of the GCS bucket from which the release candidate will be deleted.
        docker_repository (str): Name of the connector docker image.
        connector_version (str): Version of the connector.
    Returns:
        MetadataDeleteInfo: Information about the files that were deleted.
    """
    storage_client = _get_storage_client()
    bucket = storage_client.bucket(bucket_name)

    gcp_connector_dir = f"{METADATA_FOLDER}/{docker_repository}"
    version_path = f"{gcp_connector_dir}/{connector_version}/{METADATA_FILE_NAME}"
    rc_path = f"{gcp_connector_dir}/{RELEASE_CANDIDATE_GCS_FOLDER_NAME}/{METADATA_FILE_NAME}"

    version_blob = bucket.blob(version_path)
    rc_blob = bucket.blob(rc_path)

    if not version_blob.exists():
        raise FileNotFoundError(f"Version metadata file {version_path} does not exist in the bucket. ")
    if not rc_blob.exists():
        raise FileNotFoundError(f"Release candidate metadata file {rc_path} does not exist in the bucket. ")
    if rc_blob.md5_hash != version_blob.md5_hash:
        raise ValueError(
            f"Release candidate metadata file {rc_path} hash does not match the version metadata file {version_path} hash. Unsafe to delete. Please check the Remote Release Candidate to confirm its the version you would like to remove and rerun with --force"
        )

    deleted_files = []
    rc_blob.delete()
    deleted_files.append(
        DeletedFile(
            id="release_candidate_metadata",
            deleted=True,
            description="release candidate metadata",
            blob_id=rc_blob.id,
        )
    )
    version_blob.delete()
    deleted_files.append(
        DeletedFile(
            id="version_metadata",
            deleted=True,
            description="versioned metadata",
            blob_id=version_blob.id,
        )
    )

    return MetadataDeleteInfo(
        metadata_deleted=True,
        deleted_files=deleted_files,
    )


def promote_release_candidate_in_gcs(
    bucket_name: str, docker_repository: str, connector_version: str
) -> Tuple[MetadataUploadInfo, MetadataDeleteInfo]:
    """Promote a release candidate to the latest version in a GCS bucket.
    The release candidate metadata file will be copied to the latest metadata file and then deleted.
    We first check that the release candidate metadata file hash matches the version metadata file hash.
    Args:
        bucket_name (str): Name of the GCS bucket from which the release candidate will be deleted.
        docker_repository (str): Name of the connector docker image.
        connector_version (str): Version of the connector.
    Returns:
        Tuple[MetadataUploadInfo, MetadataDeleteInfo]: Information about the files that were uploaded (new latest version) and deleted (release candidate).
    """

    storage_client = _get_storage_client()
    bucket = storage_client.bucket(bucket_name)

    gcp_connector_dir = f"{METADATA_FOLDER}/{docker_repository}"
    version_path = f"{gcp_connector_dir}/{connector_version}/{METADATA_FILE_NAME}"
    rc_path = f"{gcp_connector_dir}/{RELEASE_CANDIDATE_GCS_FOLDER_NAME}/{METADATA_FILE_NAME}"
    latest_path = f"{gcp_connector_dir}/{LATEST_GCS_FOLDER_NAME}/{METADATA_FILE_NAME}"

    version_blob = bucket.blob(version_path)
    latest_blob = bucket.blob(latest_path)
    rc_blob = bucket.blob(rc_path)

    if not version_blob.exists():
        raise FileNotFoundError(f"Version metadata file {version_path} does not exist in the bucket.")
    if not rc_blob.exists():
        raise FileNotFoundError(f"Release candidate metadata file {rc_path} does not exist in the bucket.")

    if rc_blob.md5_hash != version_blob.md5_hash:
        raise ValueError(
            f"""Release candidate metadata file {rc_path} hash does not match the version metadata file {version_path} hash. Unsafe to promote.
            It's likely that something changed the release candidate hash but have not changed the metadata for the lastest matching version."""
        )

    uploaded_files = []
    deleted_files = []

    bucket.copy_blob(rc_blob, bucket, latest_blob)
    uploaded_files.append(
        UploadedFile(
            id="latest_metadata",
            uploaded=True,
            blob_id=latest_blob.id,
        )
    )

    rc_blob.delete()
    deleted_files.append(
        DeletedFile(
            id="release_candidate_metadata",
            deleted=True,
            description="release candidate metadata",
            blob_id=rc_blob.id,
        )
    )

    return MetadataUploadInfo(
        metadata_uploaded=True,
        metadata_file_path=str(version_path),
        uploaded_files=uploaded_files,
    ), MetadataDeleteInfo(
        metadata_deleted=True,
        deleted_files=deleted_files,
    )
