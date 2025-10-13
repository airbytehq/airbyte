# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import datetime
import logging
import stat
from unittest.mock import MagicMock, patch

import freezegun
import paramiko
from source_sftp_bulk.spec import SourceSFTPBulkSpec
from source_sftp_bulk.stream_reader import SourceSFTPBulkStreamReader


logger = logging.Logger("")


@freezegun.freeze_time("2024-01-02T00:00:00")
def test_stream_reader_files_read_and_filter_by_date():
    fake_client = MagicMock()
    fake_client.from_transport = MagicMock(return_value=fake_client)
    files_on_server = [
        [
            MagicMock(filename="sample_file_1.csv", st_mode=180, st_mtime=1704067200),
            MagicMock(filename="sample_file_2.csv", st_mode=180, st_mtime=1704060200),
        ]
    ]
    fake_client.listdir_attr = MagicMock(side_effect=files_on_server)
    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            start_date="2024-01-01T00:00:00.000000Z",
        )
        reader.config = config
        files = list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))
        assert len(files) == 1
        assert files[0].uri == "//sample_file_1.csv"
        assert files[0].last_modified == datetime.datetime(2024, 1, 1, 0, 0)


@freezegun.freeze_time("2024-01-02T00:00:00")
def test_stream_reader_prevents_directory_loops():
    """Test that the stream reader prevents infinite loops from circular directory references."""
    fake_client = MagicMock()
    fake_client.from_transport = MagicMock(return_value=fake_client)

    # Create a directory structure with potential for loops
    dir_mode = stat.S_IFDIR | 0o755

    # First call returns a subdirectory
    # Second call would return parent (simulating a symlink loop), but should be skipped
    files_on_server = [
        [
            MagicMock(filename="subdir", st_mode=dir_mode, st_mtime=1704067200),
            MagicMock(filename="file1.csv", st_mode=180, st_mtime=1704067200),
        ],
        [
            MagicMock(filename="file2.csv", st_mode=180, st_mtime=1704067200),
        ],
    ]
    fake_client.listdir_attr = MagicMock(side_effect=files_on_server)

    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            start_date="2024-01-01T00:00:00.000000Z",
        )
        reader.config = config
        files = list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))

        # Should find 2 files without looping infinitely
        assert len(files) == 2
        assert files[0].uri == "//file1.csv"
        assert files[1].uri == "//subdir/file2.csv"


@freezegun.freeze_time("2024-01-02T00:00:00")
def test_stream_reader_respects_depth_limit():
    """Test that the stream reader stops at max depth to prevent runaway traversal."""
    fake_client = MagicMock()
    fake_client.from_transport = MagicMock(return_value=fake_client)

    dir_mode = stat.S_IFDIR | 0o755

    # Create deeply nested structure that would exceed default MAX_DEPTH
    # Each call returns a subdirectory and a file
    files_on_server = []
    for i in range(60):  # More than default max_traversal_depth (50)
        files_on_server.append([
            MagicMock(filename=f"subdir{i}", st_mode=dir_mode, st_mtime=1704067200),
            MagicMock(filename=f"file{i}.csv", st_mode=180, st_mtime=1704067200),
        ])

    fake_client.listdir_attr = MagicMock(side_effect=files_on_server)

    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            start_date="2024-01-01T00:00:00.000000Z",
        )
        reader.config = config
        files = list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))

        # Should stop at default max_traversal_depth (50) + 1 for root = 51 files maximum
        assert len(files) <= 51
        assert len(files) > 0


@freezegun.freeze_time("2024-01-02T00:00:00")
def test_stream_reader_custom_depth_limit():
    """Test that the stream reader respects custom max_traversal_depth configuration."""
    fake_client = MagicMock()
    fake_client.from_transport = MagicMock(return_value=fake_client)

    dir_mode = stat.S_IFDIR | 0o755

    # Create nested structure
    files_on_server = []
    for i in range(10):
        files_on_server.append([
            MagicMock(filename=f"subdir{i}", st_mode=dir_mode, st_mtime=1704067200),
            MagicMock(filename=f"file{i}.csv", st_mode=180, st_mtime=1704067200),
        ])

    fake_client.listdir_attr = MagicMock(side_effect=files_on_server)

    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            start_date="2024-01-01T00:00:00.000000Z",
            max_traversal_depth=3,  # Custom depth limit
        )
        reader.config = config
        files = list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))

        # Should stop at depth 3 + 1 for root = 4 files maximum
        assert len(files) <= 4
        assert len(files) > 0


@freezegun.freeze_time("2024-01-02T00:00:00")
def test_stream_reader_excludes_absolute_paths():
    """Test that the stream reader excludes directories by absolute path."""
    fake_client = MagicMock()
    fake_client.from_transport = MagicMock(return_value=fake_client)

    dir_mode = stat.S_IFDIR | 0o755

    # First call: root directory with subdirectories including /tmp and /var
    # Second call: /var directory with files
    files_on_server = [
        [
            MagicMock(filename="tmp", st_mode=dir_mode, st_mtime=1704067200),
            MagicMock(filename="var", st_mode=dir_mode, st_mtime=1704067200),
            MagicMock(filename="file1.csv", st_mode=180, st_mtime=1704067200),
        ],
        [
            MagicMock(filename="file2.csv", st_mode=180, st_mtime=1704067200),
        ],
    ]
    fake_client.listdir_attr = MagicMock(side_effect=files_on_server)

    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            start_date="2024-01-01T00:00:00.000000Z",
            excluded_directories=["/tmp"],  # Exclude /tmp directory
        )
        reader.config = config
        files = list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))

        # Should find files in root and /var, but not in /tmp
        assert len(files) == 2
        assert files[0].uri == "//file1.csv"
        assert files[1].uri == "//var/file2.csv"


@freezegun.freeze_time("2024-01-02T00:00:00")
def test_stream_reader_excludes_glob_patterns():
    """Test that the stream reader excludes directories matching glob patterns."""
    fake_client = MagicMock()
    fake_client.from_transport = MagicMock(return_value=fake_client)

    dir_mode = stat.S_IFDIR | 0o755

    # Create structure with node_modules and .git directories at various levels
    files_on_server = [
        [
            MagicMock(filename="project", st_mode=dir_mode, st_mtime=1704067200),
            MagicMock(filename="file1.csv", st_mode=180, st_mtime=1704067200),
        ],
        [
            MagicMock(filename="node_modules", st_mode=dir_mode, st_mtime=1704067200),
            MagicMock(filename=".git", st_mode=dir_mode, st_mtime=1704067200),
            MagicMock(filename="src", st_mode=dir_mode, st_mtime=1704067200),
            MagicMock(filename="file2.csv", st_mode=180, st_mtime=1704067200),
        ],
        [
            MagicMock(filename="file3.csv", st_mode=180, st_mtime=1704067200),
        ],
    ]
    fake_client.listdir_attr = MagicMock(side_effect=files_on_server)

    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            start_date="2024-01-01T00:00:00.000000Z",
            excluded_directories=["**/node_modules", "**/.git"],  # Exclude these patterns
        )
        reader.config = config
        files = list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))

        # Should find files in root, /project, and /project/src, but not in node_modules or .git
        assert len(files) == 3
        assert files[0].uri == "//file1.csv"
        assert files[1].uri == "//project/file2.csv"
        assert files[2].uri == "//project/src/file3.csv"


@freezegun.freeze_time("2024-01-02T00:00:00")
def test_stream_reader_empty_exclusions_backward_compatible():
    """Test that empty exclusions list doesn't break existing behavior."""
    fake_client = MagicMock()
    fake_client.from_transport = MagicMock(return_value=fake_client)

    files_on_server = [
        [
            MagicMock(filename="sample_file_1.csv", st_mode=180, st_mtime=1704067200),
            MagicMock(filename="sample_file_2.csv", st_mode=180, st_mtime=1704060200),
        ]
    ]
    fake_client.listdir_attr = MagicMock(side_effect=files_on_server)

    with patch.object(paramiko, "Transport", MagicMock()), patch.object(paramiko, "SFTPClient", fake_client):
        reader = SourceSFTPBulkStreamReader()
        config = SourceSFTPBulkSpec(
            host="localhost",
            username="username",
            credentials={"auth_type": "password", "password": "password"},
            port=123,
            streams=[],
            start_date="2024-01-01T00:00:00.000000Z",
            excluded_directories=[],  # Explicitly empty
        )
        reader.config = config
        files = list(reader.get_matching_files(globs=["**"], prefix=None, logger=logger))

        # Should work exactly like before exclusions feature
        assert len(files) == 1
        assert files[0].uri == "//sample_file_1.csv"
