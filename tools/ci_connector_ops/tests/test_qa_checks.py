#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pathlib import Path

import pytest
from ci_connector_ops import qa_checks, utils


@pytest.mark.parametrize(
    "connector, expect_exists",
    [
        (utils.Connector("source-faker"), True),
        (utils.Connector("source-foobar"), False),
    ],
)
def test_check_documentation_file_exists(connector, expect_exists):
    assert qa_checks.check_documentation_file_exists(connector) == expect_exists


def test_check_changelog_entry_is_updated_missing_doc(mocker):
    mocker.patch.object(qa_checks, "check_documentation_file_exists", mocker.Mock(return_value=False))
    assert qa_checks.check_changelog_entry_is_updated(qa_checks.Connector("source-foobar")) is False


def test_check_changelog_entry_is_updated_no_changelog_section(mocker, tmp_path):
    mock_documentation_file_path = Path(tmp_path / "doc.md")
    mock_documentation_file_path.touch()

    mocker.patch.object(qa_checks.Connector, "documentation_file_path", mock_documentation_file_path)
    assert qa_checks.check_changelog_entry_is_updated(qa_checks.Connector("source-foobar")) is False


def test_check_changelog_entry_is_updated_version_not_in_changelog(mocker, tmp_path):
    mock_documentation_file_path = Path(tmp_path / "doc.md")
    with open(mock_documentation_file_path, "w") as f:
        f.write("# Changelog")

    mocker.patch.object(qa_checks.Connector, "documentation_file_path", mock_documentation_file_path)

    mocker.patch.object(qa_checks.Connector, "version", "0.0.0")

    assert qa_checks.check_changelog_entry_is_updated(qa_checks.Connector("source-foobar")) is False


def test_check_changelog_entry_is_updated_version_in_changelog(mocker, tmp_path):
    mock_documentation_file_path = Path(tmp_path / "doc.md")
    with open(mock_documentation_file_path, "w") as f:
        f.write("# Changelog\n0.0.0")

    mocker.patch.object(qa_checks.Connector, "documentation_file_path", mock_documentation_file_path)

    mocker.patch.object(qa_checks.Connector, "version", "0.0.0")
    assert qa_checks.check_changelog_entry_is_updated(qa_checks.Connector("source-foobar"))


@pytest.mark.parametrize(
    "connector, expect_exists",
    [
        (utils.Connector("source-faker"), True),
        (utils.Connector("source-foobar"), False),
    ],
)
def test_check_connector_icon_is_available(connector, expect_exists):
    assert qa_checks.check_connector_icon_is_available(connector) == expect_exists


@pytest.mark.parametrize(
    "user_input, expect_qa_checks_to_run",
    [
        ("not-a-connector", False),
        ("connectors/source-faker", True),
        ("source-faker", True),
    ],
)
def test_run_qa_checks_success(capsys, mocker, user_input, expect_qa_checks_to_run):
    mocker.patch.object(qa_checks.sys, "argv", ["", user_input])
    mocker.patch.object(qa_checks, "Connector")
    mock_qa_check = mocker.Mock(return_value=True, __name__="mock_qa_check")
    if expect_qa_checks_to_run:
        mocker.patch.object(qa_checks, "QA_CHECKS", [mock_qa_check])
    with pytest.raises(SystemExit) as wrapped_error:
        qa_checks.run_qa_checks()
    assert wrapped_error.value.code == 0
    if not expect_qa_checks_to_run:
        qa_checks.Connector.assert_not_called()
        stdout, _ = capsys.readouterr()
        assert "No QA check to run" in stdout
    else:
        expected_connector_technical_name = user_input.split("/")[-1]
        qa_checks.Connector.assert_called_with(expected_connector_technical_name)
        mock_qa_check.assert_called_with(qa_checks.Connector.return_value)
        stdout, _ = capsys.readouterr()
        assert f"Running QA checks for {expected_connector_technical_name}" in stdout
        assert f"All QA checks succeeded for {expected_connector_technical_name}" in stdout


def test_run_qa_checks_error(capsys, mocker):
    mocker.patch.object(qa_checks.sys, "argv", ["", "source-faker"])
    mocker.patch.object(qa_checks, "Connector")
    mock_qa_check = mocker.Mock(return_value=False, __name__="mock_qa_check")
    mocker.patch.object(qa_checks, "QA_CHECKS", [mock_qa_check])
    with pytest.raises(SystemExit) as wrapped_error:
        qa_checks.run_qa_checks()
    assert wrapped_error.value.code == 1
    stdout, _ = capsys.readouterr()
    assert "QA checks failed for source-faker" in stdout
    assert "❌ - mock_qa_check" in stdout


@pytest.mark.parametrize(
    "file_name, file_line, expected_in_stdout",
    [
        ("file_with_http_url.foo", "http://foo.bar", True),
        ("file_without_https_url.foo", "", False),
        ("file_with_https_url.foo", "https://airbyte.com", False),
        ("file_with_http_url_and_ignored.foo", "http://localhost http://airbyte.com", True),
        ("file_with_ignored_url.foo", "http://localhost", False),
        ("file_with_http_url_in_comment.py", "# http://dev.foo", False),
        ("file_with_http_url_in_comment.yml", "# http://dev.foo", False),
        ("file_with_http_url_in_comment.yaml", "# http://dev.foo", False),
        ("file_with_http_url_in_comment.java", "// http://dev.foo", False),
        ("file_with_http_url_in_comment.md", "<!-- http://dev.foo", False),
    ],
)
def test_check_connector_https_url_only(capsys, tmp_path, mocker, file_name, file_line, expected_in_stdout):
    file_with_url = Path(tmp_path / file_name)
    mocker.patch.object(qa_checks, "IGNORED_DIRECTORIES_FOR_HTTPS_CHECKS", set())
    with open(file_with_url, "w") as f:
        f.write(file_line)
    connector = mocker.Mock(code_directory=tmp_path)
    assert expected_in_stdout != qa_checks.check_connector_https_url_only(connector)
    stdout, _ = capsys.readouterr()
    if expected_in_stdout:
        assert file_name in stdout


@pytest.mark.skip(reason="This should only be run when we want to test all connectors for their https url only compliance")
def test_check_connector_https_url_only_all_connectors():
    failing_connectors = []
    for raw_connector in utils.OSS_CATALOG["sources"] + utils.OSS_CATALOG["destinations"]:
        technical_name = raw_connector["dockerRepository"].replace("airbyte/", "")
        connector = utils.Connector(technical_name)
        if not qa_checks.check_connector_https_url_only(connector):
            failing_connectors.append(connector)
    if failing_connectors:
        by_release_stage = {}
        for failing_connector in failing_connectors:
            by_release_stage.setdefault(failing_connector.release_stage, [])
            by_release_stage[failing_connector.release_stage].append(failing_connector)
        failure_message = ""
        for release_stage in by_release_stage.keys():
            failure_message += f"\nFailing {release_stage} connectors:\n"
            for connector in by_release_stage[release_stage]:
                failure_message += f"\t- {connector.technical_name}\n"
        pytest.fail(failure_message)


@pytest.mark.parametrize(
    "file_name, line, expect_is_comment",
    [
        ("foo.py", "# I'm a comment", True),
        ("foo.py", "   # I'm a comment", True),
        ("foo.py", "I'm not # a comment", False),
        ("foo.yaml", "# I'm a comment", True),
        ("foo.yaml", "   # I'm a comment", True),
        ("foo.yaml", "I'm not # a comment", False),
        ("foo.yml", "# I'm a comment", True),
        ("foo.yml", "   # I'm a comment", True),
        ("foo.yml", "I'm not # a comment", False),
        ("foo.java", "// I'm a comment", True),
        ("foo.java", "   // I'm a comment", True),
        ("foo.java", "I'm not // a comment", False),
        ("foo.md", "<!-- I'm a comment", True),
        ("foo.md", "   <!-- I'm a comment", True),
        ("foo.md", "I'm not <!-- a comment", False),
    ],
)
def test_is_comment(tmp_path, file_name, line, expect_is_comment):
    file_path = tmp_path / file_name
    assert qa_checks.is_comment(line, file_path) is expect_is_comment


def test_check_missing_migration_guide(mocker, tmp_path, capsys):
    connector = qa_checks.Connector("source-foobar")
    mock_documentation_directory_path = Path(tmp_path)
    mocker.patch.object(qa_checks.Connector, "documentation_directory", mock_documentation_directory_path)

    mock_metadata_dict = {"documentationUrl": tmp_path, "releases": {"breakingChanges": {"2.0.0": {
        "upgradeDeadline": "2021-01-01",
        "message": "This is a breaking change",
    }}}}
    mocker.patch.object(qa_checks.Connector, "metadata", mock_metadata_dict)

    assert qa_checks.check_migration_guide(connector) == False
    stdout, _ = capsys.readouterr()
    assert "Migration guide file is missing for foobar. Please create a foobar-migrations.md file in the docs folder" in stdout


@pytest.mark.parametrize(
    "test_file, expected_stdout", [
        ("bad-header.md", "has incorrect version headings"),
        ("out-of-order.md", "has incorrect version headings"),
        ("missing-entry.md", "has incorrect version headings"),
        ("bad-title.md", "does not start with the correct header"),
        ("extra-header.md", "has incorrect version headings"),
    ]
)
def test_check_invalid_migration_guides(
        mocker,
        tmp_path,
        capsys,
        test_file,
        expected_stdout
):
    connector = qa_checks.Connector("source-foobar")
    mock_documentation_directory_path = Path(tmp_path)
    mocker.patch.object(qa_checks.Connector, "documentation_directory", mock_documentation_directory_path)
    mock_migration_file = mock_documentation_directory_path / f"{connector.name}-migrations.md"

    mock_breaking_change_value = {
        "upgradeDeadline": "2021-01-01",
        "message": "This is a breaking change",
    }

    # transform metadata_breaking_changes into a dictionary
    mock_breaking_change_dict = {version: mock_breaking_change_value for version in ["2.0.0", "1.0.0"]}

    mock_metadata_dict = {"name": "Foobar", "documentationUrl": tmp_path, "releases": {"breakingChanges": mock_breaking_change_dict}}

    test_file = Path("tools/ci_connector_ops/tests/test_migration_files") / test_file
    with open(test_file, "r") as f:
        contents = f.read()

    with open(mock_migration_file, "w") as f:
        f.write(contents)

    mocker.patch.object(qa_checks.Connector, "metadata", mock_metadata_dict)

    assert qa_checks.check_migration_guide(connector) == False
    stdout, _ = capsys.readouterr()
    assert expected_stdout in stdout
