#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pathlib

import pytest
import yaml
from metadata_service import gcs_upload
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from pydantic import ValidationError
from metadata_service.constants import METADATA_FILE_NAME


@pytest.mark.parametrize(
    "version_blob_exists, version_blob_etag, latest_blob_etag",
    [
        pytest.param(False, "same_etag", "different_etag", id="Version blob does not exists: Version and latest blob should be uploaded."),
        pytest.param(
            False,
            "same_etag",
            "same_etag",
            id="Version blob does not exists but etags are equal: Version blob should be uploaded but latest should not.",
        ),
        pytest.param(True, "same_etag", "same_etag", id="Version exists and etags are equal: no upload should happen."),
        pytest.param(
            True, "same_etag", "different_etag", id="Version exists but latest etag is different: latest blob should be uploaded."
        ),
    ],
)
def test_upload_metadata_to_gcs_valid_metadata(mocker, valid_metadata_yaml_files, version_blob_exists, version_blob_etag, latest_blob_etag):
    metadata_file_path = pathlib.Path(valid_metadata_yaml_files[0])
    metadata = ConnectorMetadataDefinitionV0.parse_obj(yaml.safe_load(metadata_file_path.read_text()))
    expected_version_key = f"metadata/{metadata.data.dockerRepository}/{metadata.data.dockerImageTag}/{METADATA_FILE_NAME}"
    expected_latest_key = f"metadata/{metadata.data.dockerRepository}/latest/{METADATA_FILE_NAME}"

    mock_credentials = mocker.Mock()
    mock_storage_client = mocker.Mock()

    mock_version_blob = mocker.Mock(exists=mocker.Mock(return_value=version_blob_exists), etag=version_blob_etag)
    mock_latest_blob = mocker.Mock(etag=latest_blob_etag)
    mock_bucket = mock_storage_client.bucket.return_value
    mock_bucket.blob.side_effect = [mock_version_blob, mock_latest_blob]

    mocker.patch.object(gcs_upload.service_account.Credentials, "from_service_account_file", mocker.Mock(return_value=mock_credentials))
    mocker.patch.object(gcs_upload.storage, "Client", mocker.Mock(return_value=mock_storage_client))
    mocker.patch.object(gcs_upload, "validate_metadata_images_in_dockerhub", mocker.Mock(return_value=(True, None)))

    # Call function under tests

    uploaded, blob_id = gcs_upload.upload_metadata_to_gcs(
        "my_bucket",
        metadata_file_path,
        "my_service_account_path",
    )

    # Assertions

    gcs_upload.service_account.Credentials.from_service_account_file.assert_called_with("my_service_account_path")
    mock_storage_client.bucket.assert_called_with("my_bucket")
    mock_bucket.blob.assert_has_calls([mocker.call(expected_version_key), mocker.call(expected_latest_key)])
    assert blob_id == mock_version_blob.id

    if not version_blob_exists:
        mock_version_blob.upload_from_filename.assert_called_with(str(metadata_file_path))
        assert uploaded
    else:
        mock_version_blob.upload_from_filename.assert_not_called()
        assert not uploaded

    if version_blob_etag != latest_blob_etag:
        mock_latest_blob.upload_from_filename.assert_called_with(str(metadata_file_path))


def test_upload_metadata_to_gcs_invalid_metadata(invalid_metadata_yaml_files):
    metadata_file_path = pathlib.Path(invalid_metadata_yaml_files[0])
    with pytest.raises(ValidationError):
        gcs_upload.upload_metadata_to_gcs(
            "my_bucket",
            metadata_file_path,
            "my_service_account_path",
        )


def test_upload_metadata_to_gcs_non_existent_metadata_file():
    metadata_file_path = pathlib.Path("./i_dont_exist.yaml")
    with pytest.raises(FileNotFoundError):
        gcs_upload.upload_metadata_to_gcs(
            "my_bucket",
            metadata_file_path,
            "my_service_account_path",
        )
