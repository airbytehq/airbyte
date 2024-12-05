#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import difflib
from pathlib import Path

import pytest
import semver
from pipelines.helpers.changelog import Changelog, ChangelogParsingException

pytestmark = [
    pytest.mark.anyio,
]

PATH_TO_INITIAL_FILES = Path("airbyte-ci/connectors/pipelines/tests/test_changelog/initial_files")
PATH_TO_RESULT_FILES = Path("airbyte-ci/connectors/pipelines/tests/test_changelog/result_files")

# When WRITE_TO_RESULT_FILE is set to True, all tests below will generate the resulting markdown
# and write it back to the fixture files.
# This is useful when you changed the source files and need to regenrate the fixtures.
# The comparison against target will still fail, but it will succeed on the subsequent test run.
WRITE_TO_RESULT_FILE = False


def check_result(changelog: Changelog, result_filename: str):
    markdown = changelog.to_markdown()
    result_filepath = PATH_TO_RESULT_FILES / result_filename
    if not result_filepath.exists():
        expected_text = ""
    else:
        expected_text = result_filepath.read_text()
    diff = "".join(difflib.unified_diff(expected_text.splitlines(1), markdown.splitlines(1)))
    if WRITE_TO_RESULT_FILE:
        result_file = open(result_filepath, "w")
        result_file.write(markdown)
        result_file.close()
    assert diff == ""


def get_changelog(filename: str) -> Changelog:
    filepath = PATH_TO_INITIAL_FILES / filename
    return Changelog(open(filepath).read())


@pytest.mark.parametrize("filename", ["valid_changelog_at_end.md", "valid_changelog_in_middle.md"])
def test_single_insert(dagger_client, filename):
    changelog = get_changelog(filename)
    changelog.add_entry(semver.VersionInfo.parse("3.4.0"), datetime.date.fromisoformat("2024-03-01"), 123456, "test")
    check_result(changelog, "single_insert_" + filename)


@pytest.mark.parametrize("filename", ["valid_changelog_at_end.md", "valid_changelog_in_middle.md"])
def test_insert_duplicate_versions(dagger_client, filename):
    changelog = get_changelog(filename)
    changelog.add_entry(semver.VersionInfo.parse("3.4.0"), datetime.date.fromisoformat("2024-03-01"), 123456, "test1")
    changelog.add_entry(semver.VersionInfo.parse("3.4.0"), datetime.date.fromisoformat("2024-03-02"), 123457, "test2")
    check_result(changelog, "dupicate_versions_" + filename)


# This test is disabled because the current implementation allows inserting non number PR numbers.
# This is because AddChangelogEntry defaults PR number is a string placeholder that is meant to be filled by the pull-request command
# @pytest.mark.parametrize("filename", ["valid_changelog_at_end.md", "valid_changelog_in_middle.md"])
# def test_insert_duplicate_version_date(dagger_client, filename):
#     changelog = get_changelog(filename)
#     changelog.add_entry(semver.VersionInfo.parse("3.4.0"), datetime.date.fromisoformat("2024-03-01"), 123456, "test1")
#     changelog.add_entry(semver.VersionInfo.parse("3.4.0"), datetime.date.fromisoformat("2024-03-01"), 123457, "test2")
#     check_result(changelog, "dupicate_version_date_" + filename)


@pytest.mark.parametrize("filename", ["valid_changelog_at_end.md", "valid_changelog_in_middle.md"])
def test_insert_duplicate_entries(dagger_client, filename):
    changelog = get_changelog(filename)
    changelog.add_entry(semver.VersionInfo.parse("3.4.0"), datetime.date.fromisoformat("2024-03-01"), 123456, "test")
    changelog.add_entry(semver.VersionInfo.parse("3.4.0"), datetime.date.fromisoformat("2024-03-01"), 123456, "test")
    check_result(changelog, "duplicate_entry_" + filename)


@pytest.mark.parametrize("filename", ["valid_changelog_at_end.md", "valid_changelog_in_middle.md"])
def test_insert_existing_entries(dagger_client, filename):
    changelog = get_changelog(filename)
    changelog.add_entry(semver.VersionInfo.parse("3.3.3"), datetime.date.fromisoformat("2024-01-26"), 34573, "Adopt CDK v0.16.0")
    changelog.add_entry(
        semver.VersionInfo.parse("3.3.2"),
        datetime.date.fromisoformat("2024-01-24"),
        34465,
        "Check xmin only if user selects xmin sync mode.",
    )
    check_result(changelog, "existing_entries_" + filename)


@pytest.mark.parametrize("filename", ["no_changelog_header.md", "changelog_header_no_separator.md", "changelog_header_no_newline.md"])
def test_failure(dagger_client, filename):
    try:
        get_changelog(filename)
        assert False
    except ChangelogParsingException as e:
        result_filepath = PATH_TO_RESULT_FILES / filename
        if not result_filepath.exists():
            expected_text = ""
        else:
            expected_text = result_filepath.read_text()
        diff = "\n".join(difflib.unified_diff(expected_text.splitlines(), str(e).splitlines()))
        if WRITE_TO_RESULT_FILE:
            result_file = open(result_filepath, "w")
            result_file.write(str(e))
            result_file.close()
        assert diff == ""
