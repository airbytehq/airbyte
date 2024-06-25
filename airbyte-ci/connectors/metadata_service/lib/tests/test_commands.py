#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pathlib

import pytest
from click.testing import CliRunner
from metadata_service import commands
from metadata_service.gcs_upload import MetadataUploadInfo, UploadedFile
from metadata_service.validators.metadata_validator import ValidatorOptions
from pydantic import BaseModel, ValidationError, error_wrappers
from test_gcs_upload import stub_is_image_on_docker_hub


# TEST VALIDATE COMMAND
def test_valid_metadata_yaml_files(mocker, valid_metadata_yaml_files, tmp_path):
    runner = CliRunner()

    # Mock dockerhub for base image checks
    mocker.patch("metadata_service.validators.metadata_validator.is_image_on_docker_hub", side_effect=stub_is_image_on_docker_hub)

    assert len(valid_metadata_yaml_files) > 0, "No files found"

    for file_path in valid_metadata_yaml_files:
        result = runner.invoke(commands.validate, [file_path, str(tmp_path)])
        assert result.exit_code == 0, f"Validation failed for {file_path} with error: {result.output}"


def test_invalid_metadata_yaml_files(mocker, invalid_metadata_yaml_files, tmp_path):
    runner = CliRunner()

    mocker.patch("metadata_service.validators.metadata_validator.is_image_on_docker_hub", side_effect=stub_is_image_on_docker_hub)

    assert len(invalid_metadata_yaml_files) > 0, "No files found"

    for file_path in invalid_metadata_yaml_files:
        result = runner.invoke(commands.validate, [file_path, str(tmp_path)])
        assert result.exit_code != 0, f"Validation succeeded (when it should have failed) for {file_path}"


def test_metadata_file_not_found_fails(tmp_path):
    runner = CliRunner()
    result = runner.invoke(commands.validate, ["non_existent_file.yaml", str(tmp_path)])
    assert result.exit_code != 0, "Validation succeeded (when it should have failed) for non_existent_file.yaml"


def test_docs_path_not_found_fails(valid_metadata_yaml_files):
    runner = CliRunner()

    assert len(valid_metadata_yaml_files) > 0, "No files found"

    result = runner.invoke(commands.validate, [valid_metadata_yaml_files[0], "non_existent_docs_path"])
    assert result.exit_code != 0, "Validation succeeded (when it should have failed) for non_existent_docs_path"


def mock_metadata_upload_info(
    latest_uploaded: bool,
    version_uploaded: bool,
    icon_uploaded: bool,
    doc_version_uploaded: bool,
    doc_inapp_version_uploaded: bool,
    doc_latest_uploaded: bool,
    doc_inapp_latest_uploaded: bool,
    metadata_file_path: str,
) -> MetadataUploadInfo:
    return MetadataUploadInfo(
        metadata_uploaded=(latest_uploaded or version_uploaded),
        metadata_file_path=metadata_file_path,
        uploaded_files=[
            UploadedFile(
                id="version_metadata",
                uploaded=version_uploaded,
                description="versioned metadata",
                blob_id="version_blob_id" if version_uploaded else None,
            ),
            UploadedFile(
                id="latest_metadata",
                uploaded=latest_uploaded,
                description="latest metadata",
                blob_id="latest_blob_id" if latest_uploaded else None,
            ),
            UploadedFile(
                id="icon",
                uploaded=icon_uploaded,
                description="icon",
                blob_id="icon_blob_id" if icon_uploaded else None,
            ),
            UploadedFile(
                id="doc_version",
                uploaded=doc_version_uploaded,
                description="versioned doc",
                blob_id="doc_version_blob_id" if doc_version_uploaded else None,
            ),
            UploadedFile(
                id="doc_latest",
                uploaded=doc_latest_uploaded,
                description="latest doc",
                blob_id="doc_latest_blob_id" if doc_latest_uploaded else None,
            ),
            UploadedFile(
                id="doc_inapp_version",
                uploaded=doc_inapp_version_uploaded,
                description="versioned inapp doc",
                blob_id="doc_inapp_version_blob_id" if doc_inapp_version_uploaded else None,
            ),
            UploadedFile(
                id="doc_inapp_latest",
                uploaded=doc_inapp_latest_uploaded,
                description="latest inapp doc",
                blob_id="doc_inapp_latest_blob_id" if doc_inapp_latest_uploaded else None,
            ),
        ],
    )


# TEST UPLOAD COMMAND
@pytest.mark.parametrize(
    "latest_uploaded, version_uploaded, icon_uploaded, doc_version_uploaded, doc_inapp_version_uploaded, doc_latest_uploaded, doc_inapp_latest_uploaded",
    [
        (False, False, False, False, False, False, False),
        (True, False, False, False, False, False, False),
        (False, True, False, False, False, False, False),
        (False, False, True, False, False, False, False),
        (True, True, False, False, False, False, False),
        (True, False, True, False, False, False, False),
        (False, True, True, False, False, False, False),
        (True, True, True, False, False, False, False),
        (True, True, True, True, True, True, True),
    ],
)
def test_upload(
    mocker,
    tmp_path,
    valid_metadata_yaml_files,
    latest_uploaded,
    version_uploaded,
    icon_uploaded,
    doc_version_uploaded,
    doc_inapp_version_uploaded,
    doc_latest_uploaded,
    doc_inapp_latest_uploaded,
):
    runner = CliRunner()
    mocker.patch.object(commands.click, "secho")
    mocker.patch.object(commands, "upload_metadata_to_gcs")
    metadata_file_path = valid_metadata_yaml_files[0]
    upload_info = mock_metadata_upload_info(
        latest_uploaded,
        version_uploaded,
        icon_uploaded,
        doc_version_uploaded,
        doc_inapp_version_uploaded,
        doc_latest_uploaded,
        doc_inapp_latest_uploaded,
        metadata_file_path,
    )
    commands.upload_metadata_to_gcs.return_value = upload_info
    result = runner.invoke(
        commands.upload, [metadata_file_path, str(tmp_path), "my-bucket"]
    )  # Using valid_metadata_yaml_files[0] as SA because it exists...

    if latest_uploaded:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The latest metadata file for {metadata_file_path} was uploaded to latest_blob_id.", fg="green")]
        )
        assert result.exit_code == 0
    else:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The latest metadata file for {metadata_file_path} was not uploaded. Reason: None", fg="yellow")]
        )

    if version_uploaded:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The versioned metadata file for {metadata_file_path} was uploaded to version_blob_id.", fg="green")]
        )
        assert result.exit_code == 0
    else:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The versioned metadata file for {metadata_file_path} was not uploaded. Reason: None", fg="yellow")]
        )

    if icon_uploaded:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The icon file for {metadata_file_path} was uploaded to icon_blob_id.", fg="green")]
        )
    else:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The icon file for {metadata_file_path} was not uploaded. Reason: None", fg="yellow")]
        )

    if doc_version_uploaded:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The versioned doc file for {metadata_file_path} was uploaded to doc_version_blob_id.", fg="green")]
        )
    else:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The versioned doc file for {metadata_file_path} was not uploaded. Reason: None", fg="yellow")]
        )

    if doc_inapp_version_uploaded:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The versioned inapp doc file for {metadata_file_path} was uploaded to doc_inapp_version_blob_id.", fg="green")]
        )
    else:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The versioned inapp doc file for {metadata_file_path} was not uploaded. Reason: None", fg="yellow")]
        )

    if doc_latest_uploaded:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The latest doc file for {metadata_file_path} was uploaded to doc_latest_blob_id.", fg="green")]
        )
    else:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The latest doc file for {metadata_file_path} was not uploaded. Reason: None", fg="yellow")]
        )

    if doc_inapp_latest_uploaded:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The latest inapp doc file for {metadata_file_path} was uploaded to doc_inapp_latest_blob_id.", fg="green")]
        )
    else:
        commands.click.secho.assert_has_calls(
            [mocker.call(f"The latest inapp doc file for {metadata_file_path} was not uploaded. Reason: None", fg="yellow")]
        )

    if not (latest_uploaded or version_uploaded):
        # We exit with 5 status code to share with the CI pipeline that the upload was skipped.
        assert result.exit_code == 5


def test_upload_prerelease(mocker, valid_metadata_yaml_files, tmp_path):
    runner = CliRunner()
    mocker.patch.object(commands.click, "secho")
    mocker.patch.object(commands, "upload_metadata_to_gcs")

    prerelease_tag = "0.3.0-dev.6d33165120"
    bucket = "my-bucket"
    metadata_file_path = valid_metadata_yaml_files[0]
    validator_opts = ValidatorOptions(docs_path=str(tmp_path), prerelease_tag=prerelease_tag)

    upload_info = mock_metadata_upload_info(False, True, False, True, False, False, False, metadata_file_path)
    commands.upload_metadata_to_gcs.return_value = upload_info
    result = runner.invoke(
        commands.upload, [metadata_file_path, str(tmp_path), bucket, "--prerelease", prerelease_tag]
    )  # Using valid_metadata_yaml_files[0] as SA because it exists...

    commands.upload_metadata_to_gcs.assert_has_calls([mocker.call(bucket, pathlib.Path(metadata_file_path), validator_opts)])
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "error, handled",
    [
        (ValidationError([error_wrappers.ErrorWrapper(Exception("Boom!"), "foo")], BaseModel), True),
        (FileNotFoundError("Boom!"), True),
        (ValueError("Boom!"), False),
    ],
)
def test_upload_with_errors(mocker, valid_metadata_yaml_files, tmp_path, error, handled):
    runner = CliRunner()
    mocker.patch.object(commands.click, "secho")
    mocker.patch.object(commands, "upload_metadata_to_gcs")
    commands.upload_metadata_to_gcs.side_effect = error
    result = runner.invoke(
        commands.upload, [valid_metadata_yaml_files[0], str(tmp_path), "my-bucket"]
    )  # Using valid_metadata_yaml_files[0] as SA because it exists...
    assert result.exit_code == 1
    if handled:
        commands.click.secho.assert_called_with(f"The metadata file could not be uploaded: {str(error)}", fg="red")
