# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from pathlib import Path

import pytest
from live_tests.commons.evaluation_modes import TestEvaluationMode
from live_tests.commons.models import ConnectionObjects
from live_tests.report import Report

AIRBYTE_API_KEY = pytest.StashKey[str]()
AUTO_SELECT_CONNECTION = pytest.StashKey[bool]()
CONNECTION_ID = pytest.StashKey[str]()
CONNECTION_OBJECTS = pytest.StashKey[ConnectionObjects]()
CONNECTION_URL = pytest.StashKey[str | None]()
CONNECTOR_IMAGE = pytest.StashKey[str]()
CONTROL_VERSION = pytest.StashKey[str]()
DAGGER_LOG_PATH = pytest.StashKey[Path]()
DUCKDB_PATH = pytest.StashKey[Path]()
HTTP_DUMP_CACHE_VOLUMES = pytest.StashKey[list]()
RUN_IN_AIRBYTE_CI = pytest.StashKey[bool]()  # Running in airbyte-ci, locally or in GhA
IS_PRODUCTION_CI = pytest.StashKey[bool]()  # Running in airbyte-ci in GhA
IS_PERMITTED_BOOL = pytest.StashKey[bool]()
PR_URL = pytest.StashKey[str]()
REPORT = pytest.StashKey[Report]()
RETRIEVAL_REASONS = pytest.StashKey[str]()
SELECTED_STREAMS = pytest.StashKey[set[str]]()
SESSION_RUN_ID = pytest.StashKey[str]()
SHOULD_READ_WITH_STATE = pytest.StashKey[bool]()
TARGET_VERSION = pytest.StashKey[str]()
TEST_ARTIFACT_DIRECTORY = pytest.StashKey[Path]()
USER = pytest.StashKey[str]()
WORKSPACE_ID = pytest.StashKey[str]()
TEST_EVALUATION_MODE = pytest.StashKey[TestEvaluationMode]
