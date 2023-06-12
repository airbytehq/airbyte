#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

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

cases = [
    ([], set(FILEPATHS), set()),
    (["**"], set(FILEPATHS), set()),
    (["**/*.csv"], {"a.csv", "a/b.csv", "a/c.csv", "a/b/c.csv", "a/c/c.csv", "a/b/c/d.csv"}, set()),
    (["**/*.csv*"], {"a.csv", "a.csv.gz", "a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz", "a/b/c.csv", "a/b/c.csv.gz", "a/c/c.csv", "a/c/c.csv.gz", "a/b/c/d.csv", "a/b/c/d.csv.gz"}, set()),
    (["*"], {"a", "a.csv", "a.csv.gz", "a.jsonl"}, set()),
    (["*.csv"], {"a.csv"}, set()),
    (["*.csv*"], {"a.csv", "a.csv.gz"}, set()),

    (["*/*"], {"a/b", "a/b.csv", "a/b.csv.gz", "a/b.jsonl", "a/c", "a/c.csv", "a/c.csv.gz", "a/c.jsonl"}, set()),
    (["*/*.csv"], {"a/b.csv", "a/c.csv"}, set()),
    (["*/*.csv*"], {"a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz"}, set()),
    (["*/**"], {"a/b", "a/b.csv", "a/b.csv.gz", "a/b.jsonl", "a/c", "a/c.csv", "a/c.csv.gz", "a/c.jsonl", "a/b/c", "a/b/c.csv", "a/b/c.csv.gz", "a/b/c.jsonl", "a/c/c", "a/c/c.csv", "a/c/c.csv.gz", "a/c/c.jsonl", "a/b/c/d", "a/b/c/d.csv", "a/b/c/d.csv.gz", "a/b/c/d.jsonl"}, set()),
    (["a/*"], {"a/b", "a/b.csv", "a/b.csv.gz", "a/b.jsonl", "a/c", "a/c.csv", "a/c.csv.gz", "a/c.jsonl"}, {"a"}),
    (["a/*.csv"], {"a/b.csv", "a/c.csv"}, {"a"}),
    (["a/*.csv*"], {"a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz"}, {"a"}),
    (["a/b/*"], {"a/b/c", "a/b/c.csv", "a/b/c.csv.gz", "a/b/c.jsonl"}, {"a/b"}),
    (["a/b/*.csv"], {"a/b/c.csv"}, {"a/b"}),
    (["a/b/*.csv*"], {"a/b/c.csv", "a/b/c.csv.gz"}, {"a/b"}),
    (["a/*/*"], {"a/b/c", "a/b/c.csv", "a/b/c.csv.gz", "a/b/c.jsonl", "a/c/c", "a/c/c.csv", "a/c/c.csv.gz", "a/c/c.jsonl"}, {"a"}),
    (["a/*/*.csv"], {"a/b/c.csv", "a/c/c.csv"}, {"a"}),
    (["a/*/*.csv*"], {"a/b/c.csv", "a/b/c.csv.gz", "a/c/c.csv", "a/c/c.csv.gz"}, {"a"}),
    (["a/**/*"], {"a/b", "a/b.csv", "a/b.csv.gz", "a/b.jsonl", "a/c", "a/c.csv", "a/c.csv.gz", "a/c.jsonl", "a/b/c", "a/b/c.csv", "a/b/c.csv.gz", "a/b/c.jsonl", "a/c/c", "a/c/c.csv", "a/c/c.csv.gz", "a/c/c.jsonl", "a/b/c/d", "a/b/c/d.csv", "a/b/c/d.csv.gz", "a/b/c/d.jsonl"}, {"a"}),
    (["a/**/*.csv"], {"a/b.csv", "a/c.csv", "a/b/c.csv", "a/c/c.csv", "a/b/c/d.csv"}, {"a"}),
    (["a/**/*.csv*"], {"a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz", "a/b/c.csv", "a/b/c.csv.gz", "a/c/c.csv", "a/c/c.csv.gz", "a/b/c/d.csv", "a/b/c/d.csv.gz"}, {"a"}),
    (["**/*.csv", "**/*.gz"], {"a.csv", "a.csv.gz", "a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz", "a/b/c.csv", "a/b/c.csv.gz", "a/c/c.csv", "a/c/c.csv.gz", "a/b/c/d.csv", "a/b/c/d.csv.gz"}, set()),
    (["*.csv", "*.gz"], {"a.csv", "a.csv.gz"}, set()),
    (["a/*.csv", "a/*/*.csv"], {"a/b.csv", "a/c.csv", "a/b/c.csv", "a/c/c.csv"}, {"a"}),
    (["a/*.csv", "a/b/*.csv"], {"a/b.csv", "a/c.csv", "a/b/c.csv"}, {"a", "a/b"}),
]


@pytest.mark.parametrize(
    "globs,expected_matches,expected_path_prefixes",
    cases,
    ids=[",".join(c[0]) if c[0] else "no-globs" for c in cases],
)
def test_globs(globs, expected_matches, expected_path_prefixes):
    assert set([f.uri for f in reader.filter_files_by_globs(FILES, globs)]) == expected_matches
    assert set(reader.get_prefixes_from_globs(globs)) == expected_path_prefixes
