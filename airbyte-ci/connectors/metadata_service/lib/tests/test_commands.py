#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pytest

from click.testing import CliRunner
from metadata_service import commands
from metadata_service.gcs_upload import MetadataUploadInfo
from pydantic import BaseModel, ValidationError, error_wrappers


# TEST VALIDATE COMMAND
def test_valid_metadata_yaml_files(valid_metadata_yaml_files):
    runner = CliRunner()

    assert len(valid_metadata_yaml_files) > 0, "No files found"

    for file_path in valid_metadata_yaml_files:
        result = runner.invoke(commands.validate, [file_path])
        assert result.exit_code == 0, f"Validation failed for {file_path} with error: {result.output}"


def test_invalid_metadata_yaml_files(invalid_metadata_yaml_files):
    runner = CliRunner()

    assert len(invalid_metadata_yaml_files) > 0, "No files found"

    for file_path in invalid_metadata_yaml_files:
        result = runner.invoke(commands.validate, [file_path])
        assert result.exit_code != 0, f"Validation succeeded (when it shouldve failed) for {file_path}"


def test_file_not_found_fails():
    runner = CliRunner()
    result = runner.invoke(commands.validate, ["non_existent_file.yaml"])
    assert result.exit_code != 0, "Validation succeeded (when it shouldve failed) for non_existent_file.yaml"


def mock_metadata_upload_info(
    latest_uploaded: bool, version_uploaded: bool, icon_uploaded: bool, metadata_file_path: str
) -> MetadataUploadInfo:
    return MetadataUploadInfo(
        uploaded=(latest_uploaded or version_uploaded),
        latest_uploaded=latest_uploaded,
        latest_blob_id="latest_blob_id" if latest_uploaded else None,
        version_uploaded=version_uploaded,
        version_blob_id="version_blob_id" if version_uploaded else None,
        icon_uploaded=icon_uploaded,
        icon_blob_id="icon_blob_id" if icon_uploaded else None,
        metadata_file_path=metadata_file_path,
    )


# TEST UPLOAD COMMAND
@pytest.mark.parametrize(
    "latest_uploaded, version_uploaded, icon_uploaded",
    [
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (False, False, True),
        (True, True, False),
        (True, False, True),
        (False, True, True),
        (True, True, True),
    ],
)
def test_upload(mocker, valid_metadata_yaml_files, latest_uploaded, version_uploaded, icon_uploaded):
    runner = CliRunner()
    mocker.patch.object(commands.click, "secho")
    mocker.patch.object(commands, "upload_metadata_to_gcs")
    metadata_file_path = valid_metadata_yaml_files[0]
    upload_info = mock_metadata_upload_info(latest_uploaded, version_uploaded, icon_uploaded, metadata_file_path)
    commands.upload_metadata_to_gcs.return_value = upload_info
    result = runner.invoke(
        commands.upload, [metadata_file_path, "my-bucket"]
    )  # Using valid_metadata_yaml_files[0] as SA because it exists...

    if latest_uploaded:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The metadata file {metadata_file_path} was uploaded to latest_blob_id.", color="green")]
        )
        assert result.exit_code == 0

    if version_uploaded:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The metadata file {metadata_file_path} was uploaded to version_blob_id.", color="green")]
        )
        assert result.exit_code == 0

    if icon_uploaded:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The icon file {metadata_file_path} was uploaded to icon_blob_id.", color="green")]
        )

    if not (latest_uploaded or version_uploaded):
        commands.click.secho.assert_has_calls([mocker.call(f"The metadata file {metadata_file_path} was not uploaded.", color="yellow")])
        # We exit with 5 status code to share with the CI pipeline that the upload was skipped.
        assert result.exit_code == 5


@pytest.mark.parametrize(
    "error, handled",
    [
        (ValidationError([error_wrappers.ErrorWrapper(Exception("Boom!"), "foo")], BaseModel), True),
        (FileNotFoundError("Boom!"), True),
        (ValueError("Boom!"), False),
    ],
)
def test_upload_with_errors(mocker, valid_metadata_yaml_files, error, handled):
    runner = CliRunner()
    mocker.patch.object(commands.click, "secho")
    mocker.patch.object(commands, "upload_metadata_to_gcs")
    commands.upload_metadata_to_gcs.side_effect = error
    result = runner.invoke(
        commands.upload, [valid_metadata_yaml_files[0], "my-bucket"]
    )  # Using valid_metadata_yaml_files[0] as SA because it exists...
    assert result.exit_code == 1
    if handled:
        commands.click.secho.assert_called_with(f"The metadata file could not be uploaded: {str(error)}", color="red")
