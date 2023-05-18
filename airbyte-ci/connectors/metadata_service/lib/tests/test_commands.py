#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pytest
from click.testing import CliRunner
from metadata_service import commands
from pydantic import BaseModel, ValidationError, error_wrappers
from metadata_service.docker_hub import is_image_on_docker_hub

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

def stub_is_image_on_docker_hub(image_name: str, version: str) -> bool:
    # return true only if the image_name contains exists and the version contains exists
    print(f"Checking if {image_name}:{version} exists on dockerhub")
    raise Exception("This should not be called")
    return "exists" in image_name and "exists" in version

@pytest.fixture(autouse=True)
def setup_docker_hub_mock(mocker):
    # return true only if the image_name contains exists and the version contains exists
    # patch_is_image_on_docker_hub = mocker.Mock(side_effect=stub_is_image_on_docker_hub)

    # return mocker.patch(commands.upload_metadata_to_gcs, "is_image_on_docker_hub", patch_is_image_on_docker_hub)
   return mocker.patch('metadata_service.commands.gcs_upload.validators.metadata_validator.is_image_on_docker_hub', new=stub_is_image_on_docker_hub)


@pytest.mark.parametrize("uploaded", [True, False])
def test_valid_upload(mocker, valid_metadata_upload_files, uploaded):
    runner = CliRunner()
    mocker.patch.object(commands.click, "secho")
    mocker.patch.object(commands, "upload_metadata_to_gcs")
    commands.upload_metadata_to_gcs.return_value = uploaded, "blob_id"

    for metadata_file_path in valid_metadata_upload_files:
        result = runner.invoke(
            commands.upload, [metadata_file_path, "my-bucket"]
        )
        if uploaded:
            commands.click.secho.assert_called_with(f"The metadata file {metadata_file_path} was uploaded to blob_id.", color="green")
            assert result.exit_code == 0
        else:
            commands.click.secho.assert_called_with(f"The metadata file {metadata_file_path} was not uploaded.", color="yellow")
            # We exit with 5 status code to share with the CI pipeline that the upload was skipped.
            assert result.exit_code == 5

def test_invalid_upload(mocker, invalid_metadata_upload_files):
    runner = CliRunner()
    mocker.patch.object(commands.click, "secho")
    mocker.patch.object(commands, "upload_metadata_to_gcs")
    commands.upload_metadata_to_gcs.return_value = False, "blob_id"

    for metadata_file_path in invalid_metadata_upload_files:
        result = runner.invoke(
            commands.upload, [metadata_file_path, "my-bucket"]
        )
        assert result.exit_code == 1, f"Upload exited with code {result.exit_code} (when it shouldve failed) for {metadata_file_path}"


@pytest.mark.parametrize(
    "error, handled",
    [
        (ValidationError([error_wrappers.ErrorWrapper(Exception("Boom!"), "foo")], BaseModel), True),
        (FileNotFoundError("Boom!"), True),
        (ValueError("Boom!"), False),
    ],
)
def test_upload_with_gcs_errors(mocker, valid_metadata_yaml_files, error, handled):
    runner = CliRunner()
    mocker.patch.object(commands.click, "secho")
    mocker.patch.object(commands, "upload_metadata_to_gcs")
    commands.upload_metadata_to_gcs.side_effect = error
    result = runner.invoke(
        commands.upload, [valid_metadata_yaml_files[0], "my-bucket"]
    )
    assert result.exit_code == 1
    if handled:
        commands.click.secho.assert_called_with(f"The metadata file could not be uploaded: {str(error)}", color="red")
