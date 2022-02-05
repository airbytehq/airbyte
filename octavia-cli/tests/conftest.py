#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import pytest
from octavia_cli.init.commands import DIRECTORIES_TO_CREATE as OCTAVIA_PROJECT_DIRECTORIES


@pytest.fixture
def octavia_project_directory(tmpdir):
    for directory in OCTAVIA_PROJECT_DIRECTORIES:
        tmpdir.mkdir(directory)
    return tmpdir
