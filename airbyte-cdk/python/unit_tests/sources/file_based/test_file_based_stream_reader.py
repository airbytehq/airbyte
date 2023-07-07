#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Set

import pytest
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from unit_tests.sources.file_based.helpers import make_remote_files

reader = AbstractFileBasedStreamReader

"""
The rules are:

- All files at top-level: /*
- All files at top-level of mydir: mydir/*
- All files anywhere under mydir: mydir/**/*
- All files in any directory: **/*
- All files in any directory that end in .csv: **/*.csv
- All files in any directory that have a .csv extension: **/*.csv*
"""

FILEPATHS = [
    "a", "a.csv", "a.csv.gz", "a.jsonl",
    "a/b", "a/b.csv", "a/b.csv.gz", "a/b.jsonl",
    "a/c", "a/c.csv", "a/c.csv.gz", "a/c.jsonl",
    "a/b/c", "a/b/c.csv", "a/b/c.csv.gz", "a/b/c.jsonl",
    "a/c/c", "a/c/c.csv", "a/c/c.csv.gz", "a/c/c.jsonl",
    "a/b/c/d", "a/b/c/d.csv", "a/b/c/d.csv.gz", "a/b/c/d.jsonl"
]
FILES = make_remote_files(FILEPATHS)


@pytest.mark.parametrize(
    "globs,expected_matches,expected_path_prefixes",
    [
        pytest.param([], set(), set(), id="no-globs"),
        pytest.param([""], set(), set(), id="empty-string"),
        pytest.param(["**"], set(FILEPATHS), set(), id="**"),
        pytest.param(["**/*.csv"], {"a.csv", "a/b.csv", "a/c.csv", "a/b/c.csv", "a/c/c.csv", "a/b/c/d.csv"}, set(), id="**/*.csv"),
        pytest.param(["**/*.csv*"],
                     {"a.csv", "a.csv.gz", "a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz", "a/b/c.csv", "a/b/c.csv.gz", "a/c/c.csv",
                      "a/c/c.csv.gz", "a/b/c/d.csv", "a/b/c/d.csv.gz"}, set(), id="**/*.csv*"),
        pytest.param(["*"], {"a", "a.csv", "a.csv.gz", "a.jsonl"}, set(), id="*"),
        pytest.param(["*.csv"], {"a.csv"}, set(), id="*.csv"),
        pytest.param(["*.csv*"], {"a.csv", "a.csv.gz"}, set(), id="*.csv*"),
        pytest.param(["*/*"], {"a/b", "a/b.csv", "a/b.csv.gz", "a/b.jsonl", "a/c", "a/c.csv", "a/c.csv.gz", "a/c.jsonl"}, set(), id="*/*"),
        pytest.param(["*/*.csv"], {"a/b.csv", "a/c.csv"}, set(), id="*/*.csv"),
        pytest.param(["*/*.csv*"], {"a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz"}, set(), id="*/*.csv*"),
        pytest.param(["*/**"],
                     {"a/b", "a/b.csv", "a/b.csv.gz", "a/b.jsonl", "a/c", "a/c.csv", "a/c.csv.gz", "a/c.jsonl", "a/b/c", "a/b/c.csv",
                      "a/b/c.csv.gz", "a/b/c.jsonl", "a/c/c", "a/c/c.csv", "a/c/c.csv.gz", "a/c/c.jsonl", "a/b/c/d", "a/b/c/d.csv",
                      "a/b/c/d.csv.gz", "a/b/c/d.jsonl"}, set(), id="*/**"),
        pytest.param(["a/*"], {"a/b", "a/b.csv", "a/b.csv.gz", "a/b.jsonl", "a/c", "a/c.csv", "a/c.csv.gz", "a/c.jsonl"}, {"a"}, id="a/*"),
        pytest.param(["a/*.csv"], {"a/b.csv", "a/c.csv"}, {"a"}, id="a/*.csv"),
        pytest.param(["a/*.csv*"], {"a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz"}, {"a"}, id="a/*.csv*"),
        pytest.param(["a/b/*"], {"a/b/c", "a/b/c.csv", "a/b/c.csv.gz", "a/b/c.jsonl"}, {"a/b"}, id="a/b/*"),
        pytest.param(["a/b/*.csv"], {"a/b/c.csv"}, {"a/b"}, id="a/b/*.csv"),
        pytest.param(["a/b/*.csv*"], {"a/b/c.csv", "a/b/c.csv.gz"}, {"a/b"}, id="a/b/*.csv*"),
        pytest.param(["a/*/*"], {"a/b/c", "a/b/c.csv", "a/b/c.csv.gz", "a/b/c.jsonl", "a/c/c", "a/c/c.csv", "a/c/c.csv.gz", "a/c/c.jsonl"},
                     {"a"}, id="a/*/*"),
        pytest.param(["a/*/*.csv"], {"a/b/c.csv", "a/c/c.csv"}, {"a"}, id="a/*/*.csv"),
        pytest.param(["a/*/*.csv*"], {"a/b/c.csv", "a/b/c.csv.gz", "a/c/c.csv", "a/c/c.csv.gz"}, {"a"}, id="a/*/*.csv*"),
        pytest.param(["a/**/*"],
                     {"a/b", "a/b.csv", "a/b.csv.gz", "a/b.jsonl", "a/c", "a/c.csv", "a/c.csv.gz", "a/c.jsonl", "a/b/c", "a/b/c.csv",
                      "a/b/c.csv.gz", "a/b/c.jsonl", "a/c/c", "a/c/c.csv", "a/c/c.csv.gz", "a/c/c.jsonl", "a/b/c/d", "a/b/c/d.csv",
                      "a/b/c/d.csv.gz", "a/b/c/d.jsonl"}, {"a"}, id="a/**/*"),
        pytest.param(["a/**/*.csv"], {"a/b.csv", "a/c.csv", "a/b/c.csv", "a/c/c.csv", "a/b/c/d.csv"}, {"a"}, id="a/**/*.csv"),
        pytest.param(["a/**/*.csv*"],
                     {"a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz", "a/b/c.csv", "a/b/c.csv.gz", "a/c/c.csv", "a/c/c.csv.gz",
                      "a/b/c/d.csv", "a/b/c/d.csv.gz"}, {"a"}, id="a/**/*.csv*"),
        pytest.param(["**/*.csv", "**/*.gz"],
                     {"a.csv", "a.csv.gz", "a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz", "a/b/c.csv", "a/b/c.csv.gz", "a/c/c.csv",
                      "a/c/c.csv.gz", "a/b/c/d.csv", "a/b/c/d.csv.gz"}, set(), id="**/*.csv,**/*.gz"),
        pytest.param(["*.csv", "*.gz"], {"a.csv", "a.csv.gz"}, set(), id="*.csv,*.gz"),
        pytest.param(["a/*.csv", "a/*/*.csv"], {"a/b.csv", "a/c.csv", "a/b/c.csv", "a/c/c.csv"}, {"a"}, id="a/*.csv,a/*/*.csv"),
        pytest.param(["a/*.csv", "a/b/*.csv"], {"a/b.csv", "a/c.csv", "a/b/c.csv"}, {"a", "a/b"}, id="a/*.csv,a/b/*.csv"),
    ],
)
def test_globs_and_prefixes_from_globs(globs: List[str], expected_matches: Set[str], expected_path_prefixes: Set[str]) -> None:
    assert set([f.uri for f in reader.filter_files_by_globs(FILES, globs)]) == expected_matches
    assert set(reader.get_prefixes_from_globs(globs)) == expected_path_prefixes
