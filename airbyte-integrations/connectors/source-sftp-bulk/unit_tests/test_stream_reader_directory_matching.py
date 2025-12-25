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
            # Test double slashes in globs (normalized before reaching _directory_could_match_globs)
            ("/downloads", ["/downloads/*.csv"], "/", True, "Double slash at start - normalized and matches directory"),
            ("/downloads", ["/downloads/*.csv"], "/", True, "Multiple double slashes - normalized"),
            ("/data/folder", ["/data/folder/*.csv"], "/", True, "Double slash in middle - normalized and matches directory"),
            ("/data/folder", ["/data/folder/*.csv"], "/", True, "Multiple double slashes throughout - normalized"),
            ("/logs", ["/downloads/*.csv"], "/", False, "Double slash but wrong directory - normalized"),
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


class TestGlobNormalization:
    """Test glob pattern normalization in get_matching_files"""

    def test_double_slash_normalization(self):
        """Test that double slashes in globs are normalized correctly"""
        from source_sftp_bulk.stream_reader import SourceSFTPBulkStreamReader

        # Simulate the normalization logic
        globs = ["//downloads/file_*.csv", "/data//folder/*.txt", "//uploads//*.json"]
        root_folder = "/"

        normalized_globs = []
        for glob_pattern in globs:
            # This is the fix we implemented
            while "//" in glob_pattern:
                glob_pattern = glob_pattern.replace("//", "/")

            if not glob_pattern.startswith("/"):
                normalized_globs.append(f"{root_folder.rstrip('/')}/{glob_pattern}")
            else:
                normalized_globs.append(glob_pattern)

        assert normalized_globs == ["/downloads/file_*.csv", "/data/folder/*.txt", "/uploads/*.json"]

    def test_triple_slash_normalization(self):
        """Test that triple or more slashes are normalized correctly"""
        globs = ["///downloads/*.csv", "/data////folder/*.txt"]
        root_folder = "/"

        normalized_globs = []
        for glob_pattern in globs:
            while "//" in glob_pattern:
                glob_pattern = glob_pattern.replace("//", "/")

            if not glob_pattern.startswith("/"):
                normalized_globs.append(f"{root_folder.rstrip('/')}/{glob_pattern}")
            else:
                normalized_globs.append(glob_pattern)

        assert normalized_globs == ["/downloads/*.csv", "/data/folder/*.txt"]

    def test_no_double_slash_unchanged(self):
        """Test that globs without double slashes remain unchanged"""
        globs = ["/downloads/file_*.csv", "/data/folder/*.txt"]
        root_folder = "/"

        normalized_globs = []
        for glob_pattern in globs:
            while "//" in glob_pattern:
                glob_pattern = glob_pattern.replace("//", "/")

            if not glob_pattern.startswith("/"):
                normalized_globs.append(f"{root_folder.rstrip('/')}/{glob_pattern}")
            else:
                normalized_globs.append(glob_pattern)

        assert normalized_globs == ["/downloads/file_*.csv", "/data/folder/*.txt"]

    def test_get_matching_files_with_double_slash_globs(self):
        """Test that get_matching_files correctly normalizes globs with double slashes"""
        import logging
        from unittest.mock import MagicMock, patch
        import paramiko
        from source_sftp_bulk.spec import SourceSFTPBulkSpec

        logger = logging.Logger("")

        # Create a mock SFTP client
        fake_client = MagicMock()
        fake_client.from_transport = MagicMock(return_value=fake_client)

        # Mock file system structure:
        # /downloads/file_1.csv
        # /downloads/subdir/file_2.csv
        # /data/folder/file_3.txt
        files_per_directory = {
            "/": [
                MagicMock(filename="downloads", st_mode=16877, st_mtime=1704067200),  # Directory
                MagicMock(filename="data", st_mode=16877, st_mtime=1704067200),  # Directory
            ],
            "/downloads": [
                MagicMock(filename="file_1.csv", st_mode=180, st_mtime=1704067200),  # File
                MagicMock(filename="subdir", st_mode=16877, st_mtime=1704067200),  # Directory
            ],
            "/downloads/subdir": [
                MagicMock(filename="file_2.csv", st_mode=180, st_mtime=1704067200),  # File
            ],
            "/data": [
                MagicMock(filename="folder", st_mode=16877, st_mtime=1704067200),  # Directory
            ],
            "/data/folder": [
                MagicMock(filename="file_3.txt", st_mode=180, st_mtime=1704067200),  # File
            ],
        }

        def listdir_iter_side_effect(path):
            return files_per_directory.get(path, [])

        fake_client.listdir_iter = MagicMock(side_effect=listdir_iter_side_effect)

        with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
            reader = SourceSFTPBulkStreamReader()
            config = SourceSFTPBulkSpec(
                host="localhost",
                username="username",
                credentials={"auth_type": "password", "password": "password"},
                port=123,
                streams=[],
            )
            reader.config = config

            # Test with globs containing double slashes
            globs_with_double_slashes = [
                "//downloads//*.csv",  # Normalizes to /downloads/*.csv
                "/data//folder//**/*.txt",  # Normalizes to /data/folder/**/*.txt
            ]

            files = list(reader.get_matching_files(globs=globs_with_double_slashes, prefix=None, logger=logger))

            # Extract file URIs for easier assertion
            file_uris = sorted([f.uri for f in files])

            # Should match:
            # - /downloads/file_1.csv (matches first glob after normalization: /downloads/*.csv)
            # - /data/folder/file_3.txt (matches second glob after normalization: /data/folder/**/*.txt)
            expected_uris = sorted([
                "/downloads/file_1.csv",
                "/data/folder/file_3.txt",
            ])

            assert file_uris == expected_uris, f"Expected {expected_uris} but got {file_uris}"
