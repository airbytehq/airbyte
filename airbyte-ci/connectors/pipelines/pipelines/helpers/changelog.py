#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import re
from dataclasses import dataclass
from operator import attrgetter
from typing import Set, Tuple

import semver

from pipelines.helpers.github import AIRBYTE_GITHUB_REPO


class ChangelogParsingException(Exception):
    pass


@dataclass(frozen=True)
class ChangelogEntry:
    date: datetime.date
    version: semver.Version
    pr_number: int | str
    comment: str

    def to_markdown(self, github_repo: str = AIRBYTE_GITHUB_REPO) -> str:
        return f'| {self.version} | {self.date.strftime("%Y-%m-%d")} | [{self.pr_number}](https://github.com/{github_repo}/pull/{self.pr_number}) | {self.comment} |'

    def __str__(self) -> str:
        return f'version={self.version}, data={self.date.strftime("%Y-%m-%d")}, pr_number={self.pr_number}, comment={self.comment}'

    def __repr__(self) -> str:
        return "ChangelogEntry: " + self.__str__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ChangelogEntry):
            return False
        entry_matches = (
            self.date == other.date
            and self.version == other.version
            and str(self.pr_number) == str(other.pr_number)
            and self.comment == other.comment
        )
        return entry_matches

    def __ne__(self, other: object) -> bool:
        return not (self.__eq__(other))

    def __hash__(self) -> int:
        return self.__str__().__hash__()


def parse_markdown(markdown_lines: list[str], github_repo: str) -> Tuple[int, Set[ChangelogEntry]]:
    """This parses the markdown to find the changelog table, and then populates entries with the existing entries"""
    changelog_entry_re = (
        "^\\| *(?P<version>[0-9]+\\.[0-9+]+\\.[0-9]+?) *\\| *"
        + "(?P<day>[0-9]{4}-[0-9]{2}-[0-9]{2}) *\\| *"
        + "\\[?(?P<pr_number1>[0-9]+)\\]? ?\\(https://github.com/"
        + github_repo
        + "/pull/(?P<pr_number2>[0-9]+)\\) *\\| *"
        + "(?P<comment>[^ ].*[^ ]) *\\| *$"
    )
    changelog_header_line_index = -1
    changelog_line_enumerator = enumerate(markdown_lines)
    for line_index, line in changelog_line_enumerator:
        if re.search(r"\| *Version *\| *Date *\| *Pull Request *\| *Subject *\|", line):
            changelog_header_line_index = line_index
            break
    if changelog_header_line_index == -1:
        raise ChangelogParsingException("Could not find the changelog section table in the documentation file.")
    if markdown_lines[changelog_header_line_index - 1] != "":
        raise ChangelogParsingException(
            "Found changelog section table in the documentation file at line but there is not blank line before it."
        )
    if not re.search(r"(\|[- :]*){4}\|", next(changelog_line_enumerator)[1]):
        raise ChangelogParsingException("The changelog table in the documentation file is missing the header delimiter.")
    changelog_entries_start_line_index = changelog_header_line_index + 2

    # parse next line to see if it needs to be cut
    entries = set()
    for line_index, line in changelog_line_enumerator:
        changelog_entry_regexp = re.search(changelog_entry_re, line)
        if not changelog_entry_regexp or changelog_entry_regexp.group("pr_number1") != changelog_entry_regexp.group("pr_number2"):
            break
        entry_version = semver.VersionInfo.parse(changelog_entry_regexp.group("version"))
        entry_date = datetime.datetime.strptime(changelog_entry_regexp.group("day"), "%Y-%m-%d").date()
        entry_pr_number = int(changelog_entry_regexp.group("pr_number1"))
        entry_comment = changelog_entry_regexp.group("comment")
        changelog_entry = ChangelogEntry(entry_date, entry_version, entry_pr_number, entry_comment)
        entries.add(changelog_entry)

    return changelog_entries_start_line_index, entries


class Changelog:
    def __init__(self, markdown: str, github_repo: str = AIRBYTE_GITHUB_REPO) -> None:
        self.original_markdown_lines = markdown.splitlines()
        self.changelog_entries_start_line_index, self.original_entries = parse_markdown(self.original_markdown_lines, github_repo)
        self.new_entries: Set[ChangelogEntry] = set()
        self.github_repo = github_repo

    def add_entry(self, version: semver.Version, date: datetime.date, pull_request_number: int | str, comment: str) -> None:
        self.new_entries.add(ChangelogEntry(date, version, pull_request_number, comment))

    def to_markdown(self) -> str:
        """
        Generates the complete markdown content for the changelog,
        including both original and new entries, sorted by version, date, pull request number, and comment.
        """
        all_entries = set(self.original_entries.union(self.new_entries))
        sorted_entries = sorted(
            sorted(
                all_entries,
                key=attrgetter("date"),
                reverse=True,
            ),
            key=attrgetter("version"),
            reverse=True,
        )
        new_lines = (
            self.original_markdown_lines[: self.changelog_entries_start_line_index]
            + [line.to_markdown(self.github_repo) for line in sorted_entries]
            + self.original_markdown_lines[(self.changelog_entries_start_line_index + len(self.original_entries)) :]
        )
        return "\n".join(new_lines) + "\n"
