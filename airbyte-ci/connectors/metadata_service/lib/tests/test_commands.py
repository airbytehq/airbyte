#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pytest
from click.testing import CliRunner
from metadata_service import commands
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


# TEST UPLOAD COMMAND
@pytest.mark.parametrize("uploaded", [True, False])
def test_upload(mocker, valid_metadata_yaml_files, uploaded):
    runner = CliRunner()
    mocker.patch.object(commands.click, "secho")
    mocker.patch.object(commands, "upload_metadata_to_gcs")
    commands.upload_metadata_to_gcs.return_value = uploaded, "blob_id"
    metadata_file_path = valid_metadata_yaml_files[0]
    result = runner.invoke(
        commands.upload, [metadata_file_path, "my-bucket"]
    )  # Using valid_metadata_yaml_files[0] as SA because it exists...
    if uploaded:
        commands.click.secho.assert_called_with(f"The metadata file {metadata_file_path} was uploaded to blob_id.", color="green")
        assert result.exit_code == 0
    else:
        commands.click.secho.assert_called_with(f"The metadata file {metadata_file_path} was not uploaded.", color="yellow")
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
