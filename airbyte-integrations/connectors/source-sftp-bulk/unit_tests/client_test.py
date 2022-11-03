#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_sftp_bulk.client import SFTPClient


def test_get_files_matching_pattern_match():
    files = [
        {
            "filepath": "test.csv",
            "last_modified": "2021-01-01 00:00:00",
        },
        {
            "filepath": "test2.csv",
            "last_modified": "2021-01-01 00:00:00",
        },
    ]

    result = SFTPClient.get_files_matching_pattern(files, "test.csv")
    assert result == [
        {
            "filepath": "test.csv",
            "last_modified": "2021-01-01 00:00:00",
        }
    ]


def test_get_files_matching_pattern_no_match():
    files = [
        {
            "filepath": "test.csv",
            "last_modified": "2021-01-01 00:00:00",
        },
        {
            "filepath": "test2.csv",
            "last_modified": "2021-01-01 00:00:00",
        },
    ]

    result = SFTPClient.get_files_matching_pattern(files, "test3.csv")
    assert result == []


def test_get_files_matching_pattern_regex_match():
    files = [
        {
            "filepath": "test.csv",
            "last_modified": "2021-01-01 00:00:00",
        },
        {
            "filepath": "test2.csv",
            "last_modified": "2021-01-01 00:00:00",
        },
    ]

    result = SFTPClient.get_files_matching_pattern(files, "test.*")
    assert result == [
        {
            "filepath": "test.csv",
            "last_modified": "2021-01-01 00:00:00",
        },
        {
            "filepath": "test2.csv",
            "last_modified": "2021-01-01 00:00:00",
        },
    ]
