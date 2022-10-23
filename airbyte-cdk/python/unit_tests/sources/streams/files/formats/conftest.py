#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import os
import random
import shutil
import tempfile
from typing import Any

TMP_FOLDER = os.path.join(tempfile.gettempdir(), str(random.getrandbits(64)))

shutil.rmtree(TMP_FOLDER, ignore_errors=True)
os.makedirs(TMP_FOLDER, exist_ok=True)


def pytest_generate_tests(metafunc: Any) -> None:
    if "file_info" in metafunc.fixturenames:
        cases = metafunc.cls.cached_cases()
        metafunc.parametrize("file_info", cases.values(), ids=cases.keys())


def pytest_sessionfinish(session: Any, exitstatus: Any) -> None:
    """whole test run finishes."""
    shutil.rmtree(TMP_FOLDER, ignore_errors=True)
