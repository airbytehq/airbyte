#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from typing import Optional
from unittest.mock import call

from google.cloud import storage
from google.oauth2 import service_account
from metadata_service.integrations import gcs_client
from metadata_service.integrations.gcs_client import GCSClient, UploadResult
import pytest
import yaml

from metadata_service import gcs_upload
from metadata_service.constants import (
    COMPONENTS_PY_FILE_NAME,
    COMPONENTS_ZIP_SHA256_FILE_NAME,
    DOC_FILE_NAME,
    DOC_INAPP_FILE_NAME,
    ICON_FILE_NAME,
    LATEST_GCS_FOLDER_NAME,
    MANIFEST_FILE_NAME,
    METADATA_FILE_NAME,
    RELEASE_CANDIDATE_GCS_FOLDER_NAME,
)
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.validators.metadata_validator import ValidatorOptions

MOCK_VERSIONS_THAT_DO_NOT_EXIST = ["99.99.99", "0.0.0"]
MISSING_SHA = "MISSINGSHA"
DOCS_PATH = "/docs"
MOCK_DOC_URL_PATH = "integrations/sources/existingsource.md"
VALID_DOC_FILE_PATH = Path(DOCS_PATH) / MOCK_DOC_URL_PATH

# Helpers


def stub_is_image_on_docker_hub(image_name: str, version: str, digest: Optional[str] = None, retries: int = 0, wait_sec: int = 30) -> bool:
    image_repo_exists = "exists" in image_name
    version_exists = version not in MOCK_VERSIONS_THAT_DO_NOT_EXIST
    sha_is_valid = (digest != MISSING_SHA) if digest is not None else True
    image_exists = all([image_repo_exists, version_exists, sha_is_valid])
    return image_exists


# Fixtures


@pytest.fixture(autouse=True)
def mock_local_doc_path_exists(monkeypatch):
    original_exists = Path.exists
    mocked_doc_path = Path(DOCS_PATH) / MOCK_DOC_URL_PATH

    def fake_exists(self):
        if self == Path(DOCS_PATH) or self == mocked_doc_path:
            return True
        return original_exists(self)

    monkeypatch.setattr(Path, "exists", fake_exists)


# Custom Assertions


def assert_upload_invalid_metadata_fails_correctly(metadata_file_path: Path, expected_error_match: str, validate_success_error_match: str):
    """
    When attempting to upload invalid metadata, we expect it to fail in a predictable way, depending on what is exactly invalid
    about the file. This helper aims to make it easier for a developer who is adding new test cases to figure out that their test
    is failing because the test data that should be invalid is passing all of the validation steps.

    Because we don't exit the uploading process if validation fails, this case often looks like a weird error message that is hard to
    grok.
    """
    try:
        with pytest.raises(ValueError, match=expected_error_match) as exc_info:
            gcs_upload.upload_metadata_to_gcs(
                "my_bucket",
                metadata_file_path,
                validator_opts=ValidatorOptions(docs_path=DOCS_PATH),
            )
        print(f"Upload raised {exc_info.value}")
    except AssertionError as e:
        if validate_success_error_match in str(e):
            raise AssertionError(f"Validation succeeded (when it should have failed) for {metadata_file_path}") from e
        else:
            raise e


# Mocks


def setup_upload_mocks(
    mocker,
    version_blob_md5_hash,
    latest_blob_md5_hash,
    local_file_md5_hash,
    doc_local_file_md5_hash,
    doc_version_blob_md5_hash,
    doc_latest_blob_md5_hash,
    metadata_file_path,
    doc_file_path,
):
    # Mock dockerhub
    mocker.patch("metadata_service.validators.metadata_validator.is_image_on_docker_hub", side_effect=stub_is_image_on_docker_hub)

    # Mock GCS
    service_account_json = '{"type": "service_account"}'
    mocker.patch.dict("os.environ", {"GCS_CREDENTIALS": service_account_json})
    mock_credentials = mocker.Mock()
    mock_storage_client = mocker.Mock()

    latest_blob_exists = latest_blob_md5_hash is not None
    version_blob_exists = version_blob_md5_hash is not None
    doc_version_blob_exists = doc_version_blob_md5_hash is not None
    doc_latest_blob_exists = doc_latest_blob_md5_hash is not None
    release_candidate_blob_exists = False

    mock_version_blob = mocker.Mock(exists=mocker.Mock(return_value=version_blob_exists), md5_hash=version_blob_md5_hash)
    mock_latest_blob = mocker.Mock(exists=mocker.Mock(return_value=latest_blob_exists), md5_hash=latest_blob_md5_hash)

    mock_doc_version_blob = mocker.Mock(exists=mocker.Mock(return_value=doc_version_blob_exists), md5_hash=doc_version_blob_md5_hash)
    mock_doc_latest_blob = mocker.Mock(exists=mocker.Mock(return_value=doc_latest_blob_exists), md5_hash=doc_latest_blob_md5_hash)

    mock_release_candidate_blob = mocker.Mock(exists=mocker.Mock(return_value=release_candidate_blob_exists), md5_hash="rc_hash")

    mock_zip_latest_blob = mocker.Mock(exists=mocker.Mock(return_value=True), md5_hash="zip_hash")
    mock_zip_version_blob = mocker.Mock(exists=mocker.Mock(return_value=True), md5_hash="zip_hash")

    mock_sha_latest_blob = mocker.Mock(exists=mocker.Mock(return_value=True), md5_hash="sha_hash")
    mock_sha_version_blob = mocker.Mock(exists=mocker.Mock(return_value=True), md5_hash="sha_hash")

    mock_components_py_latest_blob = mocker.Mock(exists=mocker.Mock(return_value=True), md5_hash="components_py_hash")
    mock_components_py_version_blob = mocker.Mock(exists=mocker.Mock(return_value=True), md5_hash="components_py_hash")

    mock_manifest_latest_blob = mocker.Mock(exists=mocker.Mock(return_value=True), md5_hash="manifest_hash")
    mock_manifest_version_blob = mocker.Mock(exists=mocker.Mock(return_value=True), md5_hash="manifest_hash")

    mock_other_file_blob = mocker.Mock(exists=mocker.Mock(return_value=True), md5_hash="other_hash")
    mock_bucket = mock_storage_client.bucket.return_value

    mocker.patch.object(service_account, "Credentials", mocker.Mock(return_value=mock_credentials))
    mocker.patch.object(storage, "Client", mocker.Mock(return_value=mock_storage_client))

    # Mock bucket blob

    def side_effect_bucket_blob(file_path):
        # if file path ends in latest/metadata.yaml, return mock_latest_blob
        file_path_str = str(file_path)
        is_latest = f"{LATEST_GCS_FOLDER_NAME}/" in file_path_str

        if file_path_str.endswith(f"{RELEASE_CANDIDATE_GCS_FOLDER_NAME}/{METADATA_FILE_NAME}"):
            return mock_release_candidate_blob

        if file_path_str.endswith(METADATA_FILE_NAME):
            if is_latest:
                return mock_latest_blob
            else:
                return mock_version_blob

        if file_path_str.endswith(DOC_FILE_NAME):
            if is_latest:
                return mock_doc_latest_blob
            else:
                return mock_doc_version_blob

        if file_path_str.endswith(f"{MANIFEST_FILE_NAME}"):
            if is_latest:
                return mock_manifest_latest_blob
            else:
                return mock_manifest_version_blob

        if file_path_str.endswith(f"{COMPONENTS_PY_FILE_NAME}"):
            if is_latest:
                return mock_components_py_latest_blob
            else:
                return mock_components_py_version_blob

        if file_path_str.endswith(".sha256"):
            if is_latest:
                return mock_sha_latest_blob
            else:
                return mock_sha_version_blob

        if file_path_str.endswith(".zip"):
            if is_latest:
                return mock_zip_latest_blob
            else:
                return mock_zip_version_blob

        else:
            return mock_other_file_blob

    mock_bucket.blob.side_effect = side_effect_bucket_blob

    # Mock md5 hash
    def side_effect_compute_gcs_md5(file_path):
        if str(file_path) == str(metadata_file_path):
            return local_file_md5_hash
        elif str(file_path) == str(doc_file_path):
            return doc_local_file_md5_hash
        else:
            return f"mock_md5_hash_{file_path}"

    mocker.patch.object(gcs_client, "compute_gcs_md5", side_effect=side_effect_compute_gcs_md5)

    return {
        "mock_credentials": mock_credentials,
        "mock_storage_client": mock_storage_client,
        "mock_bucket": mock_bucket,
        "mock_version_blob": mock_version_blob,
        "mock_latest_blob": mock_latest_blob,
        "mock_release_candidate_blob": mock_release_candidate_blob,
        "mock_doc_version_blob": mock_doc_version_blob,
        "mock_doc_latest_blob": mock_doc_latest_blob,
        "mock_manifest_latest_blob": mock_manifest_latest_blob,
        "mock_components_py_latest_blob": mock_components_py_latest_blob,
        "mock_manifest_version_blob": mock_manifest_version_blob,
        "mock_components_py_version_blob": mock_components_py_version_blob,
        "mock_sha_latest_blob": mock_sha_latest_blob,
        "mock_sha_version_blob": mock_sha_version_blob,
        "mock_zip_latest_blob": mock_zip_latest_blob,
        "mock_zip_version_blob": mock_zip_version_blob,
        "mock_other_file_blob": mock_other_file_blob,
        "service_account_json": service_account_json,
    }

def test_upload_metadata_to_gcs_non_existent_metadata_file():
    metadata_file_path = Path("./i_dont_exist.yaml")
    with pytest.raises(ValueError, match="No such file or directory"):
        gcs_upload.upload_metadata_to_gcs(
            "my_bucket",
            metadata_file_path,
            validator_opts=ValidatorOptions(docs_path=DOCS_PATH),
        )


@pytest.mark.parametrize(
    "is_release_candidate,is_prerelease,expect_latest_upload,expect_rc_upload",
    [
        (False, False, True, False),   # Normal release - upload latest
        (True, False, False, True),    # Release candidate - upload RC
        (False, True, False, False),   # Prerelease - no latest or RC
        (True, True, False, False),    # Prerelease RC - no latest or RC
    ],
)
def test_upload_metadata_to_gcs_file_upload_calls(
    mocker,
    valid_metadata_upload_files,
    tmp_path,
    is_release_candidate,
    is_prerelease,
    expect_latest_upload,
    expect_rc_upload
):
    """Test that _file_upload is called with expected arguments for different scenarios."""

    # Mock dependencies
    mock_file_upload = mocker.spy(gcs_upload, "_file_upload")
    mock_gcs_client = mocker.Mock(spec=GCSClient)

    # Configure the mock client to return UploadResult objects
    mock_upload_result = UploadResult(uploaded=True, blob_id="mock_blob_id")
    mock_gcs_client.upload_file_if_changed.return_value = mock_upload_result

    mocker.patch.object(GCSClient, "__init__", return_value=None)
    mocker.patch.object(gcs_upload, "GCSClient", return_value=mock_gcs_client)

    # Mock validation
    mock_validate_and_load = mocker.patch.object(gcs_upload, "validate_and_load")

    # Setup test metadata
    metadata_file_path = Path(valid_metadata_upload_files[0])
    metadata = ConnectorMetadataDefinitionV0.parse_obj(yaml.safe_load(metadata_file_path.read_text()))

    # Modify dockerImageTag based on test parameters
    if is_release_candidate:
        metadata.data.dockerImageTag = "1.0.0-rc.1"
    else:
        metadata.data.dockerImageTag = "1.0.0"

    # Setup prerelease tag
    prerelease_tag = "1.0.0-dev.123" if is_prerelease else None

    mock_validate_and_load.return_value = (metadata, None)

    # Mock file modifications
    tmp_metadata_file = tmp_path / "metadata.yaml"
    tmp_metadata_file.write_text(yaml.dump({"data": {"dockerImageTag": metadata.data.dockerImageTag}}))
    mocker.patch.object(gcs_upload, "_apply_modifications_to_metadata_file", return_value=tmp_metadata_file)

    # Mock manifest file paths
    mock_manifest_paths = mocker.Mock()
    mock_manifest_paths.manifest_file_path = metadata_file_path.parent / MANIFEST_FILE_NAME
    mock_manifest_paths.zip_file_path = None
    mock_manifest_paths.sha256_file_path = None
    mock_manifest_paths.sha256 = None
    mocker.patch.object(gcs_upload, "get_manifest_only_file_paths", return_value=mock_manifest_paths)

    # Mock doc path
    docs_path = Path(DOCS_PATH)
    expected_doc_path = docs_path / "integrations/sources/existingsource.md"
    mocker.patch.object(gcs_upload, "get_doc_local_file_path", side_effect=lambda metadata, docs_path, inapp:
                       expected_doc_path if not inapp else expected_doc_path.with_suffix(".inapp.md"))

    # Call the function under test
    validator_opts = ValidatorOptions(docs_path=DOCS_PATH, prerelease_tag=prerelease_tag)
    result = gcs_upload.upload_metadata_to_gcs("test-bucket", metadata_file_path, validator_opts)

    # Calculate expected paths
    expected_gcp_connector_dir = f"metadata/{metadata.data.dockerRepository}"
    expected_version_folder = prerelease_tag if is_prerelease else metadata.data.dockerImageTag

    # Verify _file_upload calls
    expected_calls = []

    # 1. Metadata upload (always happens)
    expected_calls.append(call(
        file_key="metadata",
        local_path=tmp_metadata_file,
        gcp_connector_dir=expected_gcp_connector_dir,
        client=mock_gcs_client,
        version_folder=expected_version_folder,
        upload_as_version=True,
        upload_as_latest=expect_latest_upload,
        disable_cache=True,
        override_destination_file_name=METADATA_FILE_NAME,
    ))

    # 2. Release candidate upload (only for RC and not prerelease)
    if expect_rc_upload:
        expected_calls.append(call(
            file_key="release_candidate",
            local_path=tmp_metadata_file,
            gcp_connector_dir=expected_gcp_connector_dir,
            client=mock_gcs_client,
            version_folder=RELEASE_CANDIDATE_GCS_FOLDER_NAME,
            upload_as_version=True,
            upload_as_latest=False,
            disable_cache=True,
            override_destination_file_name=METADATA_FILE_NAME,
        ))

    # 3. Icon upload (latest only)
    expected_calls.append(call(
        file_key="icon",
        local_path=metadata_file_path.parent / ICON_FILE_NAME,
        gcp_connector_dir=expected_gcp_connector_dir,
        client=mock_gcs_client,
        upload_as_version=False,
        upload_as_latest=expect_latest_upload,
    ))

    # 4. Doc upload (always happens)
    expected_calls.append(call(
        file_key="doc",
        local_path=expected_doc_path,
        gcp_connector_dir=expected_gcp_connector_dir,
        client=mock_gcs_client,
        upload_as_version=True,
        version_folder=expected_version_folder,
        upload_as_latest=expect_latest_upload,
        override_destination_file_name=DOC_FILE_NAME,
    ))

    # 5. In-app doc upload (always happens)
    expected_calls.append(call(
        file_key="inapp_doc",
        local_path=expected_doc_path.with_suffix(".inapp.md"),
        gcp_connector_dir=expected_gcp_connector_dir,
        client=mock_gcs_client,
        upload_as_version=True,
        version_folder=expected_version_folder,
        upload_as_latest=expect_latest_upload,
        override_destination_file_name=DOC_INAPP_FILE_NAME,
    ))

    # 6. Manifest upload (always happens)
    expected_calls.append(call(
        file_key="manifest",
        local_path=mock_manifest_paths.manifest_file_path,
        gcp_connector_dir=expected_gcp_connector_dir,
        client=mock_gcs_client,
        upload_as_version=True,
        version_folder=expected_version_folder,
        upload_as_latest=expect_latest_upload,
        override_destination_file_name=MANIFEST_FILE_NAME,
    ))

    # 7. Components ZIP SHA256 upload (when zip_file_path is None, this should still be called)
    expected_calls.append(call(
        file_key="components_zip_sha256",
        local_path=mock_manifest_paths.sha256_file_path,
        gcp_connector_dir=expected_gcp_connector_dir,
        client=mock_gcs_client,
        upload_as_version=True,
        version_folder=expected_version_folder,
        upload_as_latest=expect_latest_upload,
        override_destination_file_name=COMPONENTS_ZIP_SHA256_FILE_NAME,
    ))

    # 8. Components ZIP upload (when zip_file_path is None, this should still be called)
    expected_calls.append(call(
        file_key="components_zip",
        local_path=mock_manifest_paths.zip_file_path,
        gcp_connector_dir=expected_gcp_connector_dir,
        client=mock_gcs_client,
        upload_as_version=True,
        version_folder=expected_version_folder,
        upload_as_latest=expect_latest_upload,
        override_destination_file_name="components.zip",
    ))

    # Assert all expected calls were made
    mock_file_upload.assert_has_calls(expected_calls, any_order=False)

    # Verify the result structure
    assert isinstance(result, gcs_upload.MetadataUploadInfo)
    assert result.metadata_file_path == str(tmp_metadata_file)


def test_upload_metadata_to_gcs_with_components_py(mocker, valid_metadata_upload_files, tmp_path):
    """Test that components.py files are handled correctly when they exist."""

    # Mock dependencies
    mock_file_upload = mocker.spy(gcs_upload, "_file_upload")
    mock_gcs_client = mocker.Mock(spec=GCSClient)

    # Configure the mock client to return UploadResult objects
    mock_upload_result = UploadResult(uploaded=True, blob_id="mock_blob_id")
    mock_gcs_client.upload_file_if_changed.return_value = mock_upload_result

    mocker.patch.object(GCSClient, "__init__", return_value=None)
    mocker.patch.object(gcs_upload, "GCSClient", return_value=mock_gcs_client)

    # Setup test metadata
    metadata_file_path = Path(valid_metadata_upload_files[0])
    metadata = ConnectorMetadataDefinitionV0.parse_obj(yaml.safe_load(metadata_file_path.read_text()))

    # Mock validation
    mock_validate_and_load = mocker.patch.object(gcs_upload, "validate_and_load")
    mock_validate_and_load.return_value = (metadata, None)

    # Mock file modifications
    tmp_metadata_file = tmp_path / "metadata.yaml"
    tmp_metadata_file.write_text(yaml.dump({"data": {"dockerImageTag": metadata.data.dockerImageTag}}))
    mocker.patch.object(gcs_upload, "_apply_modifications_to_metadata_file", return_value=tmp_metadata_file)

    # Mock manifest file paths with components.py files
    tmp_zip_file = tmp_path / "components.zip"
    tmp_sha256_file = tmp_path / "components.sha256"
    tmp_zip_file.write_bytes(b"fake zip content")
    tmp_sha256_file.write_text("fake_sha256_hash")

    mock_manifest_paths = mocker.Mock()
    mock_manifest_paths.manifest_file_path = metadata_file_path.parent / MANIFEST_FILE_NAME
    mock_manifest_paths.zip_file_path = tmp_zip_file
    mock_manifest_paths.sha256_file_path = tmp_sha256_file
    mock_manifest_paths.sha256 = "fake_sha256_hash"
    mocker.patch.object(gcs_upload, "get_manifest_only_file_paths", return_value=mock_manifest_paths)

    # Mock doc path
    docs_path = Path(DOCS_PATH)
    expected_doc_path = docs_path / "integrations/sources/existingsource.md"
    mocker.patch.object(gcs_upload, "get_doc_local_file_path", side_effect=lambda metadata, docs_path, inapp:
                       expected_doc_path if not inapp else expected_doc_path.with_suffix(".inapp.md"))

    # Call the function under test
    validator_opts = ValidatorOptions(docs_path=DOCS_PATH)
    gcs_upload.upload_metadata_to_gcs("test-bucket", metadata_file_path, validator_opts)

    # Verify that components ZIP files are uploaded correctly
    components_zip_calls = [call for call in mock_file_upload.call_args_list if call[1]['file_key'] == 'components_zip']
    components_sha256_calls = [call for call in mock_file_upload.call_args_list if call[1]['file_key'] == 'components_zip_sha256']

    assert len(components_zip_calls) == 1
    assert len(components_sha256_calls) == 1

    # Verify the ZIP file path is correct
    zip_call = components_zip_calls[0]
    assert zip_call[1]['local_path'] == tmp_zip_file

    # Verify the SHA256 file path is correct
    sha256_call = components_sha256_calls[0]
    assert sha256_call[1]['local_path'] == tmp_sha256_file


def test_upload_metadata_to_gcs_validation_failure(mocker, valid_metadata_upload_files, tmp_path):
    """Test that upload_metadata_to_gcs raises ValueError when validation fails."""

    # Mock dependencies
    mock_file_upload = mocker.spy(gcs_upload, "_file_upload")
    mock_gcs_client = mocker.Mock(spec=GCSClient)

    # Configure the mock client to return UploadResult objects
    mock_upload_result = UploadResult(uploaded=True, blob_id="mock_blob_id")
    mock_gcs_client.upload_file_if_changed.return_value = mock_upload_result

    mocker.patch.object(GCSClient, "__init__", return_value=None)
    mocker.patch.object(gcs_upload, "GCSClient", return_value=mock_gcs_client)

    # Setup test metadata
    metadata_file_path = Path(valid_metadata_upload_files[0])

    # Mock file modifications to return a valid file
    tmp_metadata_file = tmp_path / "metadata.yaml"
    tmp_metadata_file.write_text("invalid: yaml: content")
    mocker.patch.object(gcs_upload, "_apply_modifications_to_metadata_file", return_value=tmp_metadata_file)

    # Mock manifest file paths
    mock_manifest_paths = mocker.Mock()
    mock_manifest_paths.manifest_file_path = metadata_file_path.parent / MANIFEST_FILE_NAME
    mock_manifest_paths.zip_file_path = None
    mock_manifest_paths.sha256_file_path = None
    mock_manifest_paths.sha256 = None
    mocker.patch.object(gcs_upload, "get_manifest_only_file_paths", return_value=mock_manifest_paths)

    # Mock validation to return error
    mock_validate_and_load = mocker.patch.object(gcs_upload, "validate_and_load")
    mock_validate_and_load.return_value = (None, "Validation failed: invalid metadata")

    # Call the function under test and expect ValueError
    validator_opts = ValidatorOptions(docs_path=DOCS_PATH)

    with pytest.raises(ValueError, match="Metadata file .* is invalid for uploading: Validation failed: invalid metadata"):
        gcs_upload.upload_metadata_to_gcs("test-bucket", metadata_file_path, validator_opts)

    # Verify that _file_upload was never called since validation failed
    mock_file_upload.assert_not_called()


def test_upload_invalid_metadata_to_gcs(mocker, invalid_metadata_yaml_files):
    # Mock dockerhub
    mocker.patch("metadata_service.validators.metadata_validator.is_image_on_docker_hub", side_effect=stub_is_image_on_docker_hub)

    # Test that all invalid metadata files throw a ValueError
    for invalid_metadata_file in invalid_metadata_yaml_files:
        print("\nTesting upload of invalid metadata file: " + invalid_metadata_file)
        metadata_file_path = Path(invalid_metadata_file)

        error_match_if_validation_fails_as_expected = "Validation error"

        # If validation succeeds, it goes on to upload any new/changed files.
        # We don't mock the gcs stuff in this test, so it fails trying to
        # mock compute the md5 hash.
        error_match_if_validation_succeeds = "Please set the GCS_CREDENTIALS env var."

        assert_upload_invalid_metadata_fails_correctly(
            metadata_file_path, error_match_if_validation_fails_as_expected, error_match_if_validation_succeeds
        )


def test_upload_metadata_to_gcs_invalid_docker_images(mocker, invalid_metadata_upload_files):
    setup_upload_mocks(mocker, None, None, "new_md5_hash", None, None, None, None, None)

    # Test that valid metadata files that reference invalid docker images throw a ValueError
    for invalid_metadata_file in invalid_metadata_upload_files:
        print("\nTesting upload of valid metadata file with invalid docker image: " + invalid_metadata_file)
        metadata_file_path = Path(invalid_metadata_file)

        error_match_if_validation_fails_as_expected = "does not exist in DockerHub"

        # If validation succeeds, it goes on to upload any new/changed files.
        # We mock gcs stuff in this test, so it fails trying to compare the md5 hashes.
        error_match_if_validation_succeeds = "Unexpected path"

        assert_upload_invalid_metadata_fails_correctly(
            metadata_file_path, error_match_if_validation_fails_as_expected, error_match_if_validation_succeeds
        )
