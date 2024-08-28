#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path
from typing import Optional

import pytest
import yaml
from metadata_service import gcs_upload
from metadata_service.constants import DOC_FILE_NAME, LATEST_GCS_FOLDER_NAME, METADATA_FILE_NAME, RELEASE_CANDIDATE_GCS_FOLDER_NAME
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.models.transform import to_json_sanitized_dict
from metadata_service.validators.metadata_validator import ValidatorOptions
from pydash.objects import get

MOCK_VERSIONS_THAT_DO_NOT_EXIST = ["99.99.99", "0.0.0"]
MISSING_SHA = "MISSINGSHA"
DOCS_PATH = "/docs"
MOCK_DOC_URL_PATH = "integrations/sources/existingsource.md"
VALID_DOC_FILE_PATH = Path(DOCS_PATH) / MOCK_DOC_URL_PATH


def stub_is_image_on_docker_hub(image_name: str, version: str, digest: Optional[str] = None, retries: int = 0, wait_sec: int = 30) -> bool:
    image_repo_exists = "exists" in image_name
    version_exists = version not in MOCK_VERSIONS_THAT_DO_NOT_EXIST
    sha_is_valid = (digest != MISSING_SHA) if digest is not None else True
    image_exists = all([image_repo_exists, version_exists, sha_is_valid])
    return image_exists


@pytest.fixture(autouse=True)
def mock_local_doc_path_exists(monkeypatch):
    original_exists = Path.exists
    mocked_doc_path = Path(DOCS_PATH) / MOCK_DOC_URL_PATH

    def fake_exists(self):
        if self == Path(DOCS_PATH) or self == mocked_doc_path:
            return True
        return original_exists(self)

    monkeypatch.setattr(Path, "exists", fake_exists)


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

    mock_version_blob = mocker.Mock(exists=mocker.Mock(return_value=version_blob_exists), md5_hash=version_blob_md5_hash)
    mock_latest_blob = mocker.Mock(exists=mocker.Mock(return_value=latest_blob_exists), md5_hash=latest_blob_md5_hash)
    mock_doc_version_blob = mocker.Mock(exists=mocker.Mock(return_value=doc_version_blob_exists), md5_hash=doc_version_blob_md5_hash)
    mock_doc_latest_blob = mocker.Mock(exists=mocker.Mock(return_value=doc_latest_blob_exists), md5_hash=doc_latest_blob_md5_hash)
    mock_bucket = mock_storage_client.bucket.return_value
    mock_bucket.blob.side_effect = [mock_version_blob, mock_doc_version_blob, mock_latest_blob, mock_doc_latest_blob]

    mocker.patch.object(gcs_upload.service_account.Credentials, "from_service_account_info", mocker.Mock(return_value=mock_credentials))
    mocker.patch.object(gcs_upload.storage, "Client", mocker.Mock(return_value=mock_storage_client))

    # Mock md5 hash
    def side_effect_compute_gcs_md5(file_path):
        if str(file_path) == str(metadata_file_path):
            return local_file_md5_hash
        elif str(file_path) == str(doc_file_path):
            return doc_local_file_md5_hash
        else:
            raise ValueError(f"Unexpected path: {file_path}")

    mocker.patch.object(gcs_upload, "compute_gcs_md5", side_effect=side_effect_compute_gcs_md5)

    return {
        "mock_credentials": mock_credentials,
        "mock_storage_client": mock_storage_client,
        "mock_bucket": mock_bucket,
        "mock_version_blob": mock_version_blob,
        "mock_latest_blob": mock_latest_blob,
        "mock_doc_version_blob": mock_doc_version_blob,
        "mock_doc_latest_blob": mock_doc_latest_blob,
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
    mocker.spy(gcs_upload, "_metadata_upload")
    mocker.spy(gcs_upload, "_doc_upload")
    for valid_metadata_upload_file in valid_metadata_upload_files:
        print(f"\nTesting upload of valid metadata file: " + valid_metadata_upload_file)
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

        latest_blob_exists = latest_blob_md5_hash is not None
        version_blob_exists = version_blob_md5_hash is not None
        doc_version_blob_exists = doc_version_blob_md5_hash is not None
        doc_latest_blob_exists = doc_latest_blob_md5_hash is not None

        # Call function under tests

        upload_info = gcs_upload.upload_metadata_to_gcs(
            "my_bucket", metadata_file_path, validator_opts=ValidatorOptions(docs_path=DOCS_PATH)
        )

        # Assertions

        assert gcs_upload._metadata_upload.call_count == 2
        is_release_candidate = getattr(metadata.data.releases, "isReleaseCandidate", False)
        if is_release_candidate:
            gcs_upload._metadata_upload.assert_has_calls(
                [
                    mocker.call(metadata, mocks["mock_bucket"], metadata_file_path, metadata.data.dockerImageTag),
                    mocker.call(metadata, mocks["mock_bucket"], metadata_file_path, RELEASE_CANDIDATE_GCS_FOLDER_NAME),
                ]
            )
        else:
            gcs_upload._metadata_upload.assert_has_calls(
                [
                    mocker.call(metadata, mocks["mock_bucket"], metadata_file_path, metadata.data.dockerImageTag),
                    mocker.call(metadata, mocks["mock_bucket"], metadata_file_path, LATEST_GCS_FOLDER_NAME),
                ]
            )
        gcs_upload._doc_upload.assert_called()

        gcs_upload.service_account.Credentials.from_service_account_info.assert_called_with(json.loads(mocks["service_account_json"]))
        mocks["mock_storage_client"].bucket.assert_called_with("my_bucket")
        if is_release_candidate:
            mocks["mock_bucket"].blob.assert_has_calls(
                [
                    mocker.call(expected_version_key),
                    mocker.call(expected_version_doc_key),
                    mocker.call(expected_release_candidate_key),
                ]
            )
        else:
            mocks["mock_bucket"].blob.assert_has_calls(
                [
                    mocker.call(expected_version_key),
                    mocker.call(expected_version_doc_key),
                    mocker.call(expected_latest_key),
                    mocker.call(expected_latest_doc_key),
                ]
            )

        version_metadata_uploaded_file = next((file for file in upload_info.uploaded_files if file.id == "version_metadata"), None)
        assert version_metadata_uploaded_file, "version_metadata not found in uploaded files."
        assert version_metadata_uploaded_file.blob_id == mocks["mock_version_blob"].id

        doc_version_uploaded_file = next((file for file in upload_info.uploaded_files if file.id == "doc_version"), None)
        assert doc_version_uploaded_file, "doc_version not found in uploaded files."
        assert doc_version_uploaded_file.blob_id == mocks["mock_doc_version_blob"].id

        doc_latest_uploaded_file = next((file for file in upload_info.uploaded_files if file.id == "doc_latest"), None)
        if not is_release_candidate:
            assert doc_latest_uploaded_file, "doc_latest not found in uploaded files."
            assert doc_latest_uploaded_file.blob_id == mocks["mock_doc_latest_blob"].id
        else:
            assert not doc_latest_uploaded_file.uploaded

        if not version_blob_exists:
            mocks["mock_version_blob"].upload_from_filename.assert_called_with(metadata_file_path)
            assert upload_info.metadata_uploaded

        if not latest_blob_exists:
            mocks["mock_latest_blob"].upload_from_filename.assert_called_with(metadata_file_path)
            assert upload_info.metadata_uploaded

        if not doc_version_blob_exists:
            mocks["mock_doc_version_blob"].upload_from_filename.assert_called_with(VALID_DOC_FILE_PATH)
            assert doc_version_uploaded_file.uploaded

        if not doc_latest_blob_exists and not is_release_candidate:
            mocks["mock_doc_latest_blob"].upload_from_filename.assert_called_with(VALID_DOC_FILE_PATH)
            assert doc_latest_uploaded_file.uploaded

        if version_blob_md5_hash != local_file_md5_hash:
            mocks["mock_version_blob"].upload_from_filename.assert_called_with(metadata_file_path)
            assert upload_info.metadata_uploaded

        if latest_blob_md5_hash != local_file_md5_hash:
            mocks["mock_latest_blob"].upload_from_filename.assert_called_with(metadata_file_path)
            assert upload_info.metadata_uploaded

        if doc_version_blob_md5_hash != local_doc_file_md5_hash:
            mocks["mock_doc_version_blob"].upload_from_filename.assert_called_with(VALID_DOC_FILE_PATH)
            assert doc_version_uploaded_file.uploaded

        if (doc_latest_blob_md5_hash != local_doc_file_md5_hash) and not is_release_candidate:
            mocks["mock_doc_latest_blob"].upload_from_filename.assert_called_with(VALID_DOC_FILE_PATH)
            assert doc_latest_uploaded_file.uploaded

        # clear the call count
        gcs_upload._metadata_upload.reset_mock()
        gcs_upload._doc_upload.reset_mock()


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
        print(f"\nTesting upload of invalid metadata file: " + invalid_metadata_file)
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
        print(f"\nTesting upload of valid metadata file with invalid docker image: " + invalid_metadata_file)
        metadata_file_path = Path(invalid_metadata_file)

        error_match_if_validation_fails_as_expected = "does not exist in DockerHub"

        # If validation succeeds, it goes on to upload any new/changed files.
        # We mock gcs stuff in this test, so it fails trying to compare the md5 hashes.
        error_match_if_validation_succeeds = "Unexpected path"

        assert_upload_invalid_metadata_fails_correctly(
            metadata_file_path, error_match_if_validation_fails_as_expected, error_match_if_validation_succeeds
        )


def test_upload_metadata_to_gcs_with_prerelease(mocker, valid_metadata_upload_files, tmp_path):
    # Arrange
    mocker.patch("metadata_service.gcs_upload._metadata_upload", return_value=(True, "someid"))
    mocker.patch("metadata_service.gcs_upload.upload_file_if_changed", return_value=(True, "someid"))
    mocker.spy(gcs_upload, "_metadata_upload")
    doc_upload_spy = mocker.spy(gcs_upload, "_doc_upload")

    for valid_metadata_upload_file in valid_metadata_upload_files:
        tmp_metadata_file_path = tmp_path / "metadata.yaml"
        if tmp_metadata_file_path.exists():
            tmp_metadata_file_path.unlink()

        print(f"\nTesting prerelease upload of valid metadata file: " + valid_metadata_upload_file)
        # Assuming there is a valid metadata file in the list, if not, you might need to create one
        metadata_file_path = Path(valid_metadata_upload_file)
        mocks = setup_upload_mocks(mocker, "new_md5_hash1", "new_md5_hash2", "new_md5_hash3", None, None, None, metadata_file_path, None)
        # Mock tempfile to have a deterministic path
        mocker.patch.object(
            gcs_upload.tempfile,
            "NamedTemporaryFile",
            mocker.Mock(
                return_value=mocker.Mock(__enter__=mocker.Mock(return_value=tmp_metadata_file_path.open("w")), __exit__=mocker.Mock())
            ),
        )

        prerelease_image_tag = "1.5.6-dev.f80318f754"

        gcs_upload.upload_metadata_to_gcs(
            "my_bucket",
            metadata_file_path,
            ValidatorOptions(docs_path=DOCS_PATH, prerelease_tag=prerelease_image_tag),
        )

        assert gcs_upload._metadata_upload.call_count == 1
        overridden_metadata = ConnectorMetadataDefinitionV0.parse_obj(yaml.safe_load(tmp_metadata_file_path.read_text()))
        gcs_upload._metadata_upload.assert_called_with(
            overridden_metadata, mocks["mock_bucket"], tmp_metadata_file_path, prerelease_image_tag
        )

        # Assert that _doc_upload is only called twice, both with latest set to False
        assert doc_upload_spy.call_count == 2
        assert doc_upload_spy.call_args_list[0].args[-2] == False
        assert doc_upload_spy.call_args_list[1].args[-2] == False
        doc_upload_spy.reset_mock()

        # Verify the tmp metadata is overridden
        assert tmp_metadata_file_path.exists(), f"{tmp_metadata_file_path} does not exist"

        # verify that the metadata is overrode
        tmp_metadata, error = gcs_upload.validate_and_load(tmp_metadata_file_path, [], validator_opts=ValidatorOptions(docs_path=DOCS_PATH))
        tmp_metadata_dict = to_json_sanitized_dict(tmp_metadata, exclude_none=True)
        assert tmp_metadata_dict["data"]["dockerImageTag"] == prerelease_image_tag
        for registry in get(tmp_metadata_dict, "data.registryOverrides", {}).values():
            if "dockerImageTag" in registry:
                assert registry["dockerImageTag"] == prerelease_image_tag

        # clear the call count
        gcs_upload._metadata_upload.reset_mock()
        gcs_upload._doc_upload.reset_mock()
