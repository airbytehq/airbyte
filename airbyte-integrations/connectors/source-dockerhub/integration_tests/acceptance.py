#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import os
import pathlib
import shutil

import pytest

pytest_plugins = ("source_acceptance_test.plugin",)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This source doesn't have any secrets, so this copies the sample_files config into secrets/ for acceptance tests"""
    src_folder = pathlib.Path(__file__).parent.parent.resolve()
    os.makedirs(f"{src_folder}/secrets", exist_ok=True)
    shutil.copy(f"{src_folder}/sample_files/config.json", f"{src_folder}/secrets/")
