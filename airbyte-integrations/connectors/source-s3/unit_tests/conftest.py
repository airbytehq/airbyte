#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import os
import shutil
import tempfile

TMP_FOLDER = os.path.join(tempfile.gettempdir(), "test_generated")


shutil.rmtree(TMP_FOLDER, ignore_errors=True)
os.makedirs(TMP_FOLDER, exist_ok=True)


def pytest_generate_tests(metafunc):
    if "file_info" in metafunc.fixturenames:
        cases = metafunc.cls.cached_cases()
        metafunc.parametrize("file_info", cases.values(), ids=cases.keys())


def pytest_sessionfinish(session, exitstatus):
    """whole test run finishes."""
    # shutil.rmtree(TMP_FOLDER, ignore_errors=True)
