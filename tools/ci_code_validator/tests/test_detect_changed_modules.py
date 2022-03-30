#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import List, Set

import pytest
from ci_changes_detection.main import list_changed_modules
from ci_sonar_qube import ROOT_DIR


@pytest.mark.parametrize(
    "changed_files,changed_modules",
    [
        (["path/to/file1", "file2.txt", "path/to/file3.txt"], []),
        (
                [
                    "airbyte-integrations/connectors/source-asana/source_asana/streams.py",
                    "airbyte-integrations/connectors/source-asana/source_asana/source.py",
                    "airbyte-integrations/connectors/source-braintree/integration_tests/abnormal_state.json",
                ],
                [
                    {"folder": str(ROOT_DIR / "airbyte-integrations/connectors/source-asana"), "lang": "py",
                     "module": "connectors/source-asana"},
                    {"folder": str(ROOT_DIR / "airbyte-integrations/connectors/source-braintree"), "lang": "py",
                     "module": "connectors/source-braintree"},
                ],
        ),
        (
                [
                    "airbyte-integrations/connectors/destination-mongodb/build.gradle",
                    "airbyte-integrations/connectors/destination-mongodb/src/main/java/io/airbyte/integrations/destination/mongodb/MongodbDestination.java",
                    "airbyte-integrations/connectors/destination-s3/Dockerfile",
                ],
                [
                    {"folder": str(ROOT_DIR / "airbyte-integrations/connectors/destination-mongodb"), "lang": "java",
                     "module": "connectors/destination-mongodb"},
                    {"folder": str(ROOT_DIR / "airbyte-integrations/connectors/destination-s3"), "lang": "java",
                     "module": "connectors/destination-s3"},
                ],
        ),
        (
                [
                    "airbyte-integrations/connectors/source-s3/Dockerfile",
                    "airbyte-integrations/connectors/destination-s3/Dockerfile",
                    "tools/ci_code_validator"
                ],
                [
                    {"folder": str(ROOT_DIR / "airbyte-integrations/connectors/source-s3"), "lang": "py",
                     "module": "connectors/source-s3"},
                    {"folder": str(ROOT_DIR / "airbyte-integrations/connectors/destination-s3"), "lang": "java",
                     "module": "connectors/destination-s3"},
                ],
        ),
        (
                [
                    "airbyte-integrations/connectors/source-s3/Dockerfile",
                    "airbyte-integrations/connectors/destination-s3/Dockerfile",
                    "tools/ci_code_validator"
                ],
                [
                    {"folder": str(ROOT_DIR / "airbyte-integrations/connectors/source-s3"), "lang": "py",
                     "module": "connectors/source-s3"},
                    {"folder": str(ROOT_DIR / "airbyte-integrations/connectors/destination-s3"), "lang": "java",
                     "module": "connectors/destination-s3"},
                ],
        ),

    ],
    ids=["incorrect_files", "py_modules_only", "java_modules_only", "mix_modules", "absolute_paths"],
)
def test_list_changed_modules(changed_files: List[str], changed_modules: Set[str]) -> None:
    calculated_changed_modules = list_changed_modules(changed_files)

    assert calculated_changed_modules == changed_modules
