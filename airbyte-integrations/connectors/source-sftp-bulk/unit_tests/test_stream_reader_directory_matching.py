# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import pytest
from source_sftp_bulk.stream_reader import SourceSFTPBulkStreamReader


class TestDirectoryMatching:
    """Test the _directory_could_match_globs method for various glob patterns"""

    @pytest.mark.parametrize(
        "dir_path,globs,root_folder,expected,description",
        [
            # Test glob: /*/folder/folder2/*
            ("/data", ["/*/folder/folder2/*"], "/", True, "Top-level dir matches first wildcard"),
            ("/logs", ["/*/folder/folder2/*"], "/", True, "Another top-level dir matches first wildcard"),
            ("/data/folder", ["/*/folder/folder2/*"], "/", True, "Matches /*/folder part"),
            ("/data/folder/folder2", ["/*/folder/folder2/*"], "/", True, "Matches /*/folder/folder2 - files here match"),
            ("/data/wrongname", ["/*/folder/folder2/*"], "/", False, "Second part doesn't match 'folder'"),
            ("/data/folder/wrongname", ["/*/folder/folder2/*"], "/", False, "Third part doesn't match 'folder2'"),
            (
                "/data/folder/folder2/subdir",
                ["/*/folder/folder2/*"],
                "/",
                False,
                "Too deep - glob only matches depth 4, not 5",
            ),
            # Test glob: ** (recursive wildcard)
            ("/any/path", ["**/*.csv"], "/", True, "Recursive wildcard matches any depth"),
            ("/deep/nested/path", ["**/*.csv"], "/", True, "Recursive wildcard matches deep paths"),
            # Test glob: /data/**/*.csv
            ("/data", ["/data/**/*.csv"], "/", True, "Prefix matches - could contain matching files"),
            ("/data/subdir", ["/data/**/*.csv"], "/", True, "Under /data with recursive wildcard"),
            ("/data/deep/nested", ["/data/**/*.csv"], "/", True, "Deep under /data with recursive wildcard"),
            ("/logs", ["/data/**/*.csv"], "/", False, "Different top-level dir doesn't match /data"),
            ("/logs/subdir", ["/data/**/*.csv"], "/", False, "Under different top-level dir"),
            # Test glob: *.csv (no directory component)
            ("/", ["*.csv"], "/", True, "Root folder matches glob with no directory"),
            ("/subdir", ["*.csv"], "/", False, "Subdirectory doesn't match glob with no directory"),
            # Test glob: /data/2024/*.csv
            ("/data", ["/data/2024/*.csv"], "/", True, "Prefix of /data/2024"),
            ("/data/2024", ["/data/2024/*.csv"], "/", True, "Exact match of directory part"),
            ("/data/2024/subdir", ["/data/2024/*.csv"], "/", False, "Too deep for single * at end"),
            ("/data/2023", ["/data/2024/*.csv"], "/", False, "Wrong year"),
            ("/logs", ["/data/2024/*.csv"], "/", False, "Different top-level directory"),
            # Test glob with wildcards in middle: /data/*/reports/*.csv
            ("/data", ["/data/*/reports/*.csv"], "/", True, "First part matches"),
            ("/data/2024", ["/data/*/reports/*.csv"], "/", True, "Matches /data/* part"),
            ("/data/2024/reports", ["/data/*/reports/*.csv"], "/", True, "Matches /data/*/reports part"),
            ("/data/2024/logs", ["/data/*/reports/*.csv"], "/", False, "Third part doesn't match 'reports'"),
            (
                "/data/2024/reports/subdir",
                ["/data/*/reports/*.csv"],
                "/",
                False,
                "Too deep for pattern",
            ),
            # Test multiple globs
            ("/data", ["/data/*.csv", "/logs/*.txt"], "/", True, "Matches first glob"),
            ("/logs", ["/data/*.csv", "/logs/*.txt"], "/", True, "Matches second glob"),
            ("/other", ["/data/*.csv", "/logs/*.txt"], "/", False, "Doesn't match any glob"),
            # Test with non-root folder_path
            ("/upload/data", ["/upload/data/*.csv"], "/upload", True, "Matches with non-root folder_path"),
            (
                "/upload/logs",
                ["/upload/data/*.csv"],
                "/upload",
                False,
                "Doesn't match with non-root folder_path",
            ),
        ],
    )
    def test_directory_could_match_globs(self, dir_path, globs, root_folder, expected, description):
        """Test directory matching logic against various glob patterns"""
        result = SourceSFTPBulkStreamReader._directory_could_match_globs(dir_path, globs, root_folder)
        assert result == expected, f"{description}: Expected {expected} for dir_path='{dir_path}', globs={globs}"

    @pytest.mark.parametrize(
        "dir_path,globs,root_folder",
        [
            # Edge cases
            ("", ["*.csv"], "/"),  # Empty directory path
            ("/", ["*.csv"], "/"),  # Root directory
            ("/data", [""], "/"),  # Empty glob
        ],
    )
    def test_directory_matching_edge_cases(self, dir_path, globs, root_folder):
        """Test edge cases don't crash"""
        # Should not raise exceptions
        result = SourceSFTPBulkStreamReader._directory_could_match_globs(dir_path, globs, root_folder)
        assert isinstance(result, bool)
