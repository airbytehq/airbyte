#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from typing import Optional

import pytest
import yaml
from metadata_service import gcs_upload
from metadata_service.constants import (
    COMPONENTS_PY_FILE_NAME,
    DOC_FILE_NAME,
    LATEST_GCS_FOLDER_NAME,
    MANIFEST_FILE_NAME,
    METADATA_FILE_NAME,
    RELEASE_CANDIDATE_GCS_FOLDER_NAME,
)
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.models.transform import to_json_sanitized_dict
from metadata_service.validators.metadata_validator import ValidatorOptions
from pydash.objects import get

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


def assert_blob_upload(upload_info, upload_info_file_key, blob_mock, should_upload, file_path, failure_message):
    """
    Assert that the blob upload occurred (or not) as expected.
    """
    file_uploaded = next((file.uploaded for file in upload_info.uploaded_files if file.id == upload_info_file_key), False)
    if should_upload:
        blob_mock.upload_from_filename.assert_called_with(file_path)
        assert file_uploaded, failure_message
    else:
        blob_mock.upload_from_filename.assert_not_called()
        assert not file_uploaded, failure_message


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

    mocker.patch.object(gcs_upload.service_account.Credentials, "from_service_account_info", mocker.Mock(return_value=mock_credentials))
    mocker.patch.object(gcs_upload.storage, "Client", mocker.Mock(return_value=mock_storage_client))

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

    mocker.patch.object(gcs_upload, "compute_gcs_md5", side_effect=side_effect_compute_gcs_md5)

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


@pytest.mark.parametrize(
    "version_blob_md5_hash, latest_blob_md5_hash, local_file_md5_hash, local_doc_file_md5_hash, doc_version_blob_md5_hash, doc_latest_blob_md5_hash",
    [
        pytest.param(
            None,
            "same_md5_hash",
            "same_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            id="Version blob does not exist: Version blob should be uploaded.",
        ),
        pytest.param(
            "same_md5_hash",
            None,
            "same_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            id="Latest blob does not exist: Latest blob should be uploaded.",
        ),
        pytest.param(
            None,
            None,
            "same_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            id="Latest blob and Version blob does not exist: both should be uploaded.",
        ),
        pytest.param(
            "different_md5_hash",
            "same_md5_hash",
            "same_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            id="Version blob does not match: Version blob should be uploaded.",
        ),
        pytest.param(
            "same_md5_hash",
            "same_md5_hash",
            "same_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            id="Version blob and Latest blob match, and version and latest doc blobs match: no upload should happen.",
        ),
        pytest.param(
            "same_md5_hash",
            "different_md5_hash",
            "same_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            id="Latest blob does not match: Latest blob should be uploaded.",
        ),
        pytest.param(
            "same_md5_hash",
            "same_md5_hash",
            "different_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            id="Latest blob and Version blob does not match: both should be uploaded.",
        ),
        pytest.param(
            "same_md5_hash",
            "same_md5_hash",
            "same_md5_hash",
            "same_doc_md5_hash",
            None,
            "same_doc_md5_hash",
            id="Version doc blob does not exist: Doc version blob should be uploaded.",
        ),
        pytest.param(
            "same_md5_hash",
            "same_md5_hash",
            "same_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            None,
            id="Latest doc blob does not exist: Doc latest blob should be uploaded.",
        ),
        pytest.param(
            "same_md5_hash",
            "same_md5_hash",
            "same_md5_hash",
            "same_doc_md5_hash",
            "different_doc_md5_hash",
            "same_doc_md5_hash",
            id="Version doc blob does not match: Doc version blob should be uploaded.",
        ),
        pytest.param(
            "same_md5_hash",
            "same_md5_hash",
            "same_md5_hash",
            "same_doc_md5_hash",
            "same_doc_md5_hash",
            "different_doc_md5_hash",
            id="Latest doc blob does not match: Doc version blob should be uploaded.",
        ),
    ],
)
def test_upload_metadata_to_gcs_valid_metadata(
    mocker,
    valid_metadata_upload_files,
    version_blob_md5_hash,
    latest_blob_md5_hash,
    local_file_md5_hash,
    local_doc_file_md5_hash,
    doc_version_blob_md5_hash,
    doc_latest_blob_md5_hash,
):
    mocker.spy(gcs_upload, "_file_upload")
    mocker.spy(gcs_upload, "upload_file_if_changed")
    for valid_metadata_upload_file in valid_metadata_upload_files:
        print("\nTesting upload of valid metadata file: " + valid_metadata_upload_file)
        metadata_file_path = Path(valid_metadata_upload_file)
        metadata = ConnectorMetadataDefinitionV0.parse_obj(yaml.safe_load(metadata_file_path.read_text()))
        mocks = setup_upload_mocks(
            mocker,
            version_blob_md5_hash,
            latest_blob_md5_hash,
            local_file_md5_hash,
            local_doc_file_md5_hash,
            doc_version_blob_md5_hash,
            doc_latest_blob_md5_hash,
            metadata_file_path,
            VALID_DOC_FILE_PATH,
        )
        mocker.patch.object(gcs_upload, "_write_metadata_to_tmp_file", mocker.Mock(return_value=metadata_file_path))

        expected_version_key = f"metadata/{metadata.data.dockerRepository}/{metadata.data.dockerImageTag}/{METADATA_FILE_NAME}"
        expected_latest_key = f"metadata/{metadata.data.dockerRepository}/{LATEST_GCS_FOLDER_NAME}/{METADATA_FILE_NAME}"
        expected_release_candidate_key = (
            f"metadata/{metadata.data.dockerRepository}/{RELEASE_CANDIDATE_GCS_FOLDER_NAME}/{METADATA_FILE_NAME}"
        )
        expected_version_doc_key = f"metadata/{metadata.data.dockerRepository}/{metadata.data.dockerImageTag}/{DOC_FILE_NAME}"
        expected_latest_doc_key = f"metadata/{metadata.data.dockerRepository}/latest/{DOC_FILE_NAME}"

        is_release_candidate = "-rc" in metadata.data.dockerImageTag

        # Call function under tests

        upload_info = gcs_upload.upload_metadata_to_gcs(
            "my_bucket", metadata_file_path, validator_opts=ValidatorOptions(docs_path=DOCS_PATH)
        )

        # Assert correct file upload attempts were made

        expected_calls = [
            # Always upload the versioned metadata
            mocker.call(
                local_file_path=metadata_file_path, bucket=mocks["mock_bucket"], blob_path=expected_version_key, disable_cache=True
            ),
            # Always upload the versioned doc
            mocker.call(
                local_file_path=VALID_DOC_FILE_PATH,
                bucket=mocks["mock_bucket"],
                blob_path=expected_version_doc_key,
                disable_cache=False,
            ),
        ]

        if is_release_candidate:
            expected_calls.append(
                mocker.call(
                    local_file_path=metadata_file_path,
                    bucket=mocks["mock_bucket"],
                    blob_path=expected_release_candidate_key,
                    disable_cache=True,
                )
            )
        else:
            expected_calls.append(
                mocker.call(
                    local_file_path=VALID_DOC_FILE_PATH, bucket=mocks["mock_bucket"], blob_path=expected_latest_doc_key, disable_cache=False
                )
            )
            expected_calls.append(
                mocker.call(
                    local_file_path=metadata_file_path, bucket=mocks["mock_bucket"], blob_path=expected_latest_key, disable_cache=True
                )
            )

        gcs_upload.upload_file_if_changed.assert_has_calls(expected_calls, any_order=True)

        # Assert correct files were uploaded

        assert_blob_upload(
            upload_info=upload_info,
            upload_info_file_key="latest_metadata",
            blob_mock=mocks["mock_latest_blob"],
            should_upload=latest_blob_md5_hash != local_file_md5_hash and not is_release_candidate,
            file_path=metadata_file_path,
            failure_message="Latest blob should be uploaded.",
        )

        assert_blob_upload(
            upload_info=upload_info,
            upload_info_file_key="versioned_release_candidate",
            blob_mock=mocks["mock_release_candidate_blob"],
            should_upload=is_release_candidate,
            file_path=metadata_file_path,
            failure_message="Release candidate blob should be uploaded.",
        )

        assert_blob_upload(
            upload_info=upload_info,
            upload_info_file_key="versioned_metadata",
            blob_mock=mocks["mock_version_blob"],
            should_upload=version_blob_md5_hash != local_file_md5_hash,
            file_path=metadata_file_path,
            failure_message="Version blob should be uploaded.",
        )

        assert_blob_upload(
            upload_info=upload_info,
            upload_info_file_key="versioned_doc",
            blob_mock=mocks["mock_doc_version_blob"],
            should_upload=doc_version_blob_md5_hash != local_doc_file_md5_hash,
            file_path=VALID_DOC_FILE_PATH,
            failure_message="Doc version blob should be uploaded.",
        )

        assert_blob_upload(
            upload_info=upload_info,
            upload_info_file_key="latest_doc",
            blob_mock=mocks["mock_doc_latest_blob"],
            should_upload=doc_latest_blob_md5_hash != local_doc_file_md5_hash and not is_release_candidate,
            file_path=VALID_DOC_FILE_PATH,
            failure_message="Doc latest blob should be uploaded.",
        )

        # clear the call count
        gcs_upload.upload_file_if_changed.reset_mock()


def test_upload_metadata_to_gcs_non_existent_metadata_file():
    metadata_file_path = Path("./i_dont_exist.yaml")
    with pytest.raises(ValueError, match="No such file or directory"):
        gcs_upload.upload_metadata_to_gcs(
            "my_bucket",
            metadata_file_path,
            validator_opts=ValidatorOptions(docs_path=DOCS_PATH),
        )


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


def test_upload_metadata_to_gcs_with_prerelease(mocker, valid_metadata_upload_files, tmp_path):
    mocker.spy(gcs_upload, "_file_upload")
    mocker.spy(gcs_upload, "upload_file_if_changed")
    prerelease_image_tag = "1.5.6-dev.f80318f754"

    for valid_metadata_upload_file in valid_metadata_upload_files:
        tmp_metadata_file_path = tmp_path / "metadata.yaml"
        if tmp_metadata_file_path.exists():
            tmp_metadata_file_path.unlink()

        print("\nTesting prerelease upload of valid metadata file: " + valid_metadata_upload_file)
        metadata_file_path = Path(valid_metadata_upload_file)
        metadata = ConnectorMetadataDefinitionV0.parse_obj(yaml.safe_load(metadata_file_path.read_text()))
        expected_version_key = f"metadata/{metadata.data.dockerRepository}/{prerelease_image_tag}/{METADATA_FILE_NAME}"

        mocks = setup_upload_mocks(mocker, "new_md5_hash1", "new_md5_hash2", "new_md5_hash3", None, None, None, metadata_file_path, None)

        # Mock tempfile to have a deterministic path
        mocker.patch.object(
            gcs_upload.tempfile,
            "NamedTemporaryFile",
            mocker.Mock(
                return_value=mocker.Mock(__enter__=mocker.Mock(return_value=tmp_metadata_file_path.open("w")), __exit__=mocker.Mock())
            ),
        )

        upload_info = gcs_upload.upload_metadata_to_gcs(
            "my_bucket",
            metadata_file_path,
            ValidatorOptions(docs_path=DOCS_PATH, prerelease_tag=prerelease_image_tag),
        )

        # Assert that the metadata is overrode
        tmp_metadata, error = gcs_upload.validate_and_load(tmp_metadata_file_path, [], validator_opts=ValidatorOptions(docs_path=DOCS_PATH))
        tmp_metadata_dict = to_json_sanitized_dict(tmp_metadata, exclude_none=True)
        assert tmp_metadata_dict["data"]["dockerImageTag"] == prerelease_image_tag
        for registry in get(tmp_metadata_dict, "data.registryOverrides", {}).values():
            if "dockerImageTag" in registry:
                assert registry["dockerImageTag"] == prerelease_image_tag

        # Assert uploads attempted

        expected_calls = [
            mocker.call(
                local_file_path=tmp_metadata_file_path, bucket=mocks["mock_bucket"], blob_path=expected_version_key, disable_cache=True
            ),
        ]

        gcs_upload.upload_file_if_changed.assert_has_calls(expected_calls, any_order=True)

        # Assert versioned uploads happened

        assert_blob_upload(
            upload_info=upload_info,
            upload_info_file_key="versioned_metadata",
            blob_mock=mocks["mock_version_blob"],
            should_upload=True,
            file_path=tmp_metadata_file_path,
            failure_message="Latest blob should be uploaded.",
        )

        assert_blob_upload(
            upload_info=upload_info,
            upload_info_file_key="versioned_doc",
            blob_mock=mocks["mock_doc_version_blob"],
            should_upload=True,
            file_path=VALID_DOC_FILE_PATH,
            failure_message="Latest blob should be uploaded.",
        )

        # Assert latest uploads did not happen

        assert_blob_upload(
            upload_info=upload_info,
            upload_info_file_key="latest_metadata",
            blob_mock=mocks["mock_latest_blob"],
            should_upload=False,
            file_path=metadata_file_path,
            failure_message="Latest blob should be uploaded.",
        )

        assert_blob_upload(
            upload_info=upload_info,
            upload_info_file_key="latest_doc",
            blob_mock=mocks["mock_doc_latest_blob"],
            should_upload=False,
            file_path=VALID_DOC_FILE_PATH,
            failure_message="Latest blob should be uploaded.",
        )

        # clear the call count
        gcs_upload._file_upload.reset_mock()
        gcs_upload.upload_file_if_changed.reset_mock()


@pytest.mark.parametrize("prerelease", [True, False])
def test_upload_metadata_to_gcs_release_candidate(mocker, get_fixture_path, tmp_path, prerelease):
    mocker.spy(gcs_upload, "_file_upload")
    mocker.spy(gcs_upload, "upload_file_if_changed")
    release_candidate_metadata_file = get_fixture_path(
        "metadata_upload/valid/referenced_image_in_dockerhub/metadata_release_candidate.yaml"
    )
    release_candidate_metadata_file_path = Path(release_candidate_metadata_file)
    metadata = ConnectorMetadataDefinitionV0.parse_obj(yaml.safe_load(release_candidate_metadata_file_path.read_text()))

    tmp_metadata_file_path = tmp_path / "metadata.yaml"
    if tmp_metadata_file_path.exists():
        tmp_metadata_file_path.unlink()

    mocks = setup_upload_mocks(
        mocker, "new_md5_hash1", "new_md5_hash2", "new_md5_hash3", None, None, None, release_candidate_metadata_file_path, None
    )

    # Mock tempfile to have a deterministic path
    mocker.patch.object(
        gcs_upload.tempfile,
        "NamedTemporaryFile",
        mocker.Mock(return_value=mocker.Mock(__enter__=mocker.Mock(return_value=tmp_metadata_file_path.open("w")), __exit__=mocker.Mock())),
    )
    assert metadata.data.releases.rolloutConfiguration.enableProgressiveRollout

    prerelease_tag = "1.5.6-dev.f80318f754" if prerelease else None

    upload_info = gcs_upload.upload_metadata_to_gcs(
        "my_bucket",
        release_candidate_metadata_file_path,
        ValidatorOptions(docs_path=DOCS_PATH, prerelease_tag=prerelease_tag),
    )

    # Assert versioned uploads happened

    assert_blob_upload(
        upload_info=upload_info,
        upload_info_file_key="versioned_release_candidate",
        blob_mock=mocks["mock_release_candidate_blob"],
        should_upload=not prerelease,
        file_path=tmp_metadata_file_path,
        failure_message="Latest blob should be uploaded.",
    )

    assert_blob_upload(
        upload_info=upload_info,
        upload_info_file_key="versioned_doc",
        blob_mock=mocks["mock_doc_version_blob"],
        should_upload=True,
        file_path=VALID_DOC_FILE_PATH,
        failure_message="Latest blob should be uploaded.",
    )

    # Assert latest uploads did not happen

    assert_blob_upload(
        upload_info=upload_info,
        upload_info_file_key="latest_metadata",
        blob_mock=mocks["mock_latest_blob"],
        should_upload=False,
        file_path=tmp_metadata_file_path,
        failure_message="Latest blob should be uploaded.",
    )

    assert_blob_upload(
        upload_info=upload_info,
        upload_info_file_key="latest_doc",
        blob_mock=mocks["mock_doc_latest_blob"],
        should_upload=False,
        file_path=VALID_DOC_FILE_PATH,
        failure_message="Latest blob should be uploaded.",
    )


@pytest.mark.parametrize(
    "manifest_exists, components_py_exists",
    [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ],
)
def test_upload_metadata_to_gcs_with_manifest_files(
    mocker, valid_metadata_upload_files, tmp_path, monkeypatch, manifest_exists, components_py_exists
):
    mocker.spy(gcs_upload, "_file_upload")
    mocker.spy(gcs_upload, "upload_file_if_changed")
    valid_metadata_upload_file = valid_metadata_upload_files[0]

    metadata_file_path = Path(valid_metadata_upload_file)
    expected_manifest_file_path = metadata_file_path.parent / MANIFEST_FILE_NAME
    expected_components_py_file_path = metadata_file_path.parent / COMPONENTS_PY_FILE_NAME

    # Mock file paths to conditionally exist
    original_exists = Path.exists

    def fake_exists(self):
        if self == expected_manifest_file_path:
            return manifest_exists
        if self == expected_components_py_file_path:
            return components_py_exists
        return original_exists(self)

    monkeypatch.setattr(Path, "exists", fake_exists)

    # mock create_zip_and_get_sha256
    mocker.patch.object(gcs_upload, "create_zip_and_get_sha256", mocker.Mock(return_value="fake_zip_sha256"))

    tmp_metadata_file_path = tmp_path / "metadata.yaml"
    tmp_zip_file_path = tmp_path / "components.zip"
    tmp_sha256_file_path = tmp_path / "components.sha256"

    def mock_tmp_files(*args, **kwargs):
        file_to_return = tmp_metadata_file_path.open("w")
        if kwargs.get("suffix") == ".zip":
            file_to_return = tmp_zip_file_path.open("w")
        if kwargs.get("suffix") == ".sha256":
            file_to_return = tmp_sha256_file_path.open("w")

        return mocker.Mock(__enter__=mocker.Mock(return_value=file_to_return), __exit__=mocker.Mock())

    # Mock tempfile to have a deterministic path
    mocker.patch.object(
        gcs_upload.tempfile,
        "NamedTemporaryFile",
        mocker.Mock(side_effect=mock_tmp_files),
    )

    mocks = setup_upload_mocks(mocker, "new_md5_hash1", "new_md5_hash2", "new_md5_hash3", None, None, None, metadata_file_path, None)

    upload_info = gcs_upload.upload_metadata_to_gcs(
        "my_bucket",
        metadata_file_path,
        validator_opts=ValidatorOptions(docs_path=DOCS_PATH),
    )

    # Latest Uploads

    assert_blob_upload(
        upload_info=upload_info,
        upload_info_file_key="latest_manifest",
        blob_mock=mocks["mock_manifest_latest_blob"],
        should_upload=manifest_exists,
        file_path=expected_manifest_file_path,
        failure_message="Latest manifest should be uploaded.",
    )

    assert_blob_upload(
        upload_info=upload_info,
        upload_info_file_key="latest_components_zip",
        blob_mock=mocks["mock_zip_latest_blob"],
        should_upload=components_py_exists,
        file_path=tmp_zip_file_path,
        failure_message="Latest components.py should be uploaded.",
    )

    # Versioned Uploads

    assert_blob_upload(
        upload_info=upload_info,
        upload_info_file_key="versioned_manifest",
        blob_mock=mocks["mock_manifest_version_blob"],
        should_upload=manifest_exists,
        file_path=expected_manifest_file_path,
        failure_message="Versioned manifest should be uploaded.",
    )

    assert_blob_upload(
        upload_info=upload_info,
        upload_info_file_key="versioned_components_zip",
        blob_mock=mocks["mock_zip_version_blob"],
        should_upload=components_py_exists,
        file_path=tmp_zip_file_path,
        failure_message="Versioned components.py should be uploaded.",
    )

    # clear the call count
    gcs_upload._file_upload.reset_mock()
    gcs_upload.upload_file_if_changed.reset_mock()
