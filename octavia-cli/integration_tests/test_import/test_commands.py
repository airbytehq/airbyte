#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import glob
import os
import shutil
from distutils.dir_util import copy_tree
from pathlib import Path
from unittest import mock

import pytest
from click.testing import CliRunner
from octavia_cli._import.commands import source as octavia_import_source
from octavia_cli.apply.commands import apply as octavia_apply
from octavia_cli.apply.resources import factory as resource_factory

pytestmark = pytest.mark.integration
click_runner = CliRunner()


@pytest.fixture(scope="module")
def context_object(api_client, workspace_id):
    return {"TELEMETRY_CLIENT": mock.MagicMock(), "PROJECT_IS_INITIALIZED": True, "API_CLIENT": api_client, "WORKSPACE_ID": workspace_id}


@pytest.fixture(scope="module")
def initialized_project_directory(context_object):

    cwd = os.getcwd()
    dir_path = f"{os.path.dirname(__file__)}/octavia_test_project"
    copy_tree(f"{os.path.dirname(__file__)}/octavia_project_to_migrate", dir_path)
    os.chdir(dir_path)
    click_runner.invoke(octavia_apply, obj=context_object)
    for f in glob.glob("./**/*.yaml", recursive=True):
        os.remove(f)
    yield dir_path
    os.chdir(cwd)
    shutil.rmtree(dir_path)


def test_import_source(initialized_project_directory, context_object):
    click_runner.invoke(octavia_import_source, "poke_to_import", obj=context_object)
    expected_poke_configuration_path = Path(os.path.join(initialized_project_directory, "sources", "poke_to_import", "configuration.yaml"))
    expected_poke_state_path = Path(
        os.path.join(initialized_project_directory, "sources", "poke_to_import", f"state_{context_object['WORKSPACE_ID']}.yaml")
    )
    assert expected_poke_configuration_path.is_file() and expected_poke_state_path.is_file()
    source = resource_factory(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], expected_poke_configuration_path)
    assert source.was_created
    try:
        assert source.state.path in str(expected_poke_state_path)
    finally:
        source.api_instance.delete_source(source.get_payload)
