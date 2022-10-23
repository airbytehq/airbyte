#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any

from airbyte_cdk.sources.streams.files.test_framework import generate_sample_files


def pytest_sessionstart(session: Any) -> None:
    """run before tests start"""
    generate_sample_files()
