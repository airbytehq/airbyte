from click.testing import CliRunner
from metadata_service.commands import validate


def test_valid_metadata_yaml_files(valid_metadata_yaml_files):
    runner = CliRunner()

    assert len(valid_metadata_yaml_files) > 0, "No files found"

    for file_path in valid_metadata_yaml_files:
        result = runner.invoke(validate, [file_path])
        assert result.exit_code == 0, f"Validation failed for {file_path} with error: {result.output}"


def test_invalid_metadata_yaml_files(invalid_metadata_yaml_files):
    runner = CliRunner()

    assert len(invalid_metadata_yaml_files) > 0, "No files found"

    for file_path in invalid_metadata_yaml_files:
        result = runner.invoke(validate, [file_path])
        assert result.exit_code != 0, f"Validation succeeded (when it shouldve failed) for {file_path}"


def test_file_not_found_fails():
    runner = CliRunner()
    result = runner.invoke(validate, ["non_existent_file.yaml"])
    assert result.exit_code != 0, "Validation succeeded (when it shouldve failed) for non_existent_file.yaml"
