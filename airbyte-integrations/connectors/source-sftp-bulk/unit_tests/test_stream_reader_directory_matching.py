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


class TestPathNormalization:
    """Test the canonical path normalization used for file URIs and directory paths."""

    @pytest.mark.parametrize(
        "raw_path,expected",
        [
            ("//downloaded/client2", "/downloaded/client2"),
            ("/downloaded//client2/", "/downloaded/client2"),
            ("///a///b///", "/a/b"),
            ("/", "/"),
            ("//", "/"),
            ("", "/"),
            ("/downloaded/client2/Lacey Gaddis Report.csv", "/downloaded/client2/Lacey Gaddis Report.csv"),
        ],
    )
    def test_normalize_path(self, raw_path, expected):
        assert SourceSFTPBulkStreamReader._normalize_path(raw_path) == expected


class TestGlobNormalization:
    """Test glob pattern normalization in _normalize_glob."""

    @pytest.mark.parametrize(
        "glob_pattern,root_folder,expected,description",
        [
            # Root folder "/" with a relative glob is the intuitive configuration from the bug report.
            ("downloaded/client2/Lacey*", "/", "/downloaded/client2/Lacey*", "relative glob made absolute from root"),
            ("/downloaded/client2/Lacey*", "/", "/downloaded/client2/Lacey*", "absolute glob kept absolute"),
            ("//downloaded/client2/Lacey*", "/", "/downloaded/client2/Lacey*", "duplicate leading slash collapsed"),
            ("**", "/", "/**", "recursive wildcard made absolute"),
            ("**/Lacey*", "/", "/**/Lacey*", "recursive wildcard with suffix"),
            ("*.csv", "/", "/*.csv", "no-directory glob made absolute"),
            # Non-root folder: relative globs are joined to it, absolute globs are left alone.
            ("Lacey*", "/downloaded/client2", "/downloaded/client2/Lacey*", "relative glob joined to non-root folder"),
            ("data/*.csv", "/upload", "/upload/data/*.csv", "nested relative glob joined to non-root folder"),
            ("/absolute/*.csv", "/upload", "/absolute/*.csv", "absolute glob ignores non-root folder"),
            ("data//reports///*.csv", "/upload", "/upload/data/reports/*.csv", "repeated slashes collapsed throughout"),
        ],
    )
    def test_normalize_glob(self, glob_pattern, root_folder, expected, description):
        result = SourceSFTPBulkStreamReader._normalize_glob(glob_pattern, root_folder)
        assert result == expected, f"{description}: {glob_pattern!r} with root {root_folder!r}"


class TestGetMatchingFilesGlobScenarios:
    """
    End-to-end glob matching over a mocked SFTP tree, covering the acceptance criteria
    from the bug report. The tree mirrors the reported layout:

        /downloaded/client2/Lacey Gaddis Report.csv   (target, 2026-10-28)
        /downloaded/client2/other_report.csv          (unrelated CSV)
        /downloaded/client2/archive.gz                (unrelated gz)
        /downloaded/client2/old_Lacey.csv             (old file, before start_date)
    """

    import datetime as _dt
    import logging as _logging
    from unittest.mock import MagicMock as _MagicMock

    LACEY_MTIME = int(_dt.datetime(2026, 10, 28, 21, 55, 47).timestamp())
    OLD_MTIME = int(_dt.datetime(2026, 9, 1, 0, 0, 0).timestamp())

    DIR_MODE = 16877  # stat.S_ISDIR true
    FILE_MODE = 33188  # regular file

    def _match(self, folder_path, globs, start_date=None):
        import logging
        from unittest.mock import MagicMock, patch

        import paramiko
        from source_sftp_bulk.spec import SourceSFTPBulkSpec

        files_per_directory = {
            "/": [MagicMock(filename="downloaded", st_mode=self.DIR_MODE, st_mtime=self.LACEY_MTIME)],
            "/downloaded": [MagicMock(filename="client2", st_mode=self.DIR_MODE, st_mtime=self.LACEY_MTIME)],
            "/downloaded/client2": [
                MagicMock(filename="Lacey Gaddis Report.csv", st_mode=self.FILE_MODE, st_mtime=self.LACEY_MTIME),
                MagicMock(filename="other_report.csv", st_mode=self.FILE_MODE, st_mtime=self.LACEY_MTIME),
                MagicMock(filename="archive.gz", st_mode=self.FILE_MODE, st_mtime=self.LACEY_MTIME),
                MagicMock(filename="old_Lacey.csv", st_mode=self.FILE_MODE, st_mtime=self.OLD_MTIME),
            ],
        }

        fake_client = MagicMock()
        fake_client.from_transport = MagicMock(return_value=fake_client)
        fake_client.listdir_iter = MagicMock(side_effect=lambda path: files_per_directory.get(path, []))

        config_kwargs = dict(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
        )
        if start_date:
            config_kwargs["start_date"] = start_date

        with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
            reader = SourceSFTPBulkStreamReader()
            reader.config = SourceSFTPBulkSpec(**config_kwargs)
            reader._config.folder_path = folder_path
            files = list(reader.get_matching_files(globs=globs, prefix=None, logger=logging.Logger("")))
        return sorted(f.uri for f in files)

    TARGET = "/downloaded/client2/Lacey Gaddis Report.csv"

    def test_root_with_relative_glob_matches_target(self):
        """Acceptance #1: root '/' + 'downloaded/client2/Lacey*' matches the target."""
        uris = self._match("/", ["downloaded/client2/Lacey*"])
        assert uris == [self.TARGET]

    def test_nested_folder_with_simple_glob_matches_target(self):
        """Acceptance #2: folder '/downloaded/client2' + 'Lacey*' matches the target."""
        uris = self._match("/downloaded/client2", ["Lacey*"])
        assert uris == [self.TARGET]

    def test_recursive_glob_matches_target(self):
        """Acceptance #3: '**/Lacey*' behavior documented and tested."""
        uris = self._match("/downloaded/client2", ["**/Lacey*"])
        # Both the current-day target and the old Lacey file match the glob;
        # start_date filtering is exercised separately.
        assert self.TARGET in uris

    def test_specific_glob_excludes_unrelated_files(self):
        """Acceptance #4: a specific glob excludes unrelated CSV and .gz files."""
        uris = self._match("/", ["downloaded/client2/Lacey*"])
        assert all("other_report.csv" not in u and "archive.gz" not in u for u in uris)

    def test_spaces_in_filename_match_without_encoding(self):
        """Acceptance #5: spaces in filenames work without URL-encoding the glob."""
        uris = self._match("/", ["downloaded/client2/Lacey Gaddis*"])
        assert uris == [self.TARGET]

    @pytest.mark.parametrize(
        "glob",
        [
            "downloaded/client2/Lacey*",
            "/downloaded/client2/Lacey*",
            "//downloaded/client2/Lacey*",
            "downloaded//client2/Lacey*",
        ],
    )
    def test_slash_variants_all_match(self, glob):
        """Acceptance #6: leading/repeated/trailing slashes normalize consistently."""
        uris = self._match("/", [glob])
        assert uris == [self.TARGET]

    def test_start_date_excludes_old_file(self):
        """Acceptance #7: files newer than start_date are eligible; older files excluded."""
        uris = self._match(
            "/downloaded/client2",
            ["**/Lacey*"],
            start_date="2026-10-01T00:00:00.000000Z",
        )
        assert self.TARGET in uris
        assert all("old_Lacey.csv" not in u for u in uris)

    def test_uris_have_single_leading_slash(self):
        """Matched file URIs are normalized (no '//' artifact)."""
        uris = self._match("/", ["downloaded/client2/Lacey*"])
        assert all(not u.startswith("//") for u in uris)
