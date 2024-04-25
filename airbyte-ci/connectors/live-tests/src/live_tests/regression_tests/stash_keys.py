# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import List, Set

import pytest
from live_tests.commons.models import ConnectionObjects
from live_tests.regression_tests.report import Report

AIRBYTE_API_KEY = pytest.StashKey[str]()
AUTO_SELECT_CONNECTION = pytest.StashKey[bool]()
CONNECTION_ID = pytest.StashKey[str]()
CONNECTION_OBJECTS = pytest.StashKey[ConnectionObjects]()
CONNECTION_URL = pytest.StashKey[str | None]()
CONNECTOR_IMAGE = pytest.StashKey[str]()
CONTROL_VERSION = pytest.StashKey[str]()
DAGGER_LOG_PATH = pytest.StashKey[Path]()
DUCKDB_PATH = pytest.StashKey[Path]()
HTTP_DUMP_CACHE_VOLUMES = pytest.StashKey[List]()
IS_PERMITTED_BOOL = pytest.StashKey[bool]()
PR_URL = pytest.StashKey[str]()
REPORT = pytest.StashKey[Report]()
RETRIEVAL_REASONS = pytest.StashKey[str]()
SELECTED_STREAMS = pytest.StashKey[Set[str]]()
SESSION_START_TIMESTAMP = pytest.StashKey[int]()
SHOULD_READ_WITH_STATE = pytest.StashKey[bool]()
TARGET_VERSION = pytest.StashKey[str]()
TEST_ARTIFACT_DIRECTORY = pytest.StashKey[Path]()
USER = pytest.StashKey[str]()
WORKSPACE_ID = pytest.StashKey[str]()
