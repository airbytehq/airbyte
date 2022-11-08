#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os

import pytest
import yaml
from octavia_cli.apply import yaml_loaders


def test_env_var_replacer(mocker):
    mocker.patch.object(yaml_loaders, "os")
    mock_node = mocker.Mock()
    assert yaml_loaders.env_var_replacer(mocker.Mock(), mock_node) == yaml_loaders.os.path.expandvars.return_value
    yaml_loaders.os.path.expandvars.assert_called_with(mock_node.value)


@pytest.fixture
def test_env_vars():
    old_environ = dict(os.environ)
    secret_env_vars = {"MY_SECRET_PASSWORD": "🤫", "ANOTHER_SECRET_VALUE": "🔒"}
    os.environ.update(secret_env_vars)
    yield secret_env_vars
    os.environ.clear()
    os.environ.update(old_environ)


def test_env_var_loader(test_env_vars):
    assert yaml_loaders.EnvVarLoader.yaml_implicit_resolvers[None] == [("!environment_variable", yaml_loaders.ENV_VAR_MATCHER_PATTERN)]
    assert yaml_loaders.EnvVarLoader.yaml_constructors["!environment_variable"] == yaml_loaders.env_var_replacer
    test_yaml = "my_secret_password: ${MY_SECRET_PASSWORD}\nanother_secret_value: ${ANOTHER_SECRET_VALUE}"
    deserialized = yaml.load(test_yaml, yaml_loaders.EnvVarLoader)
    assert deserialized == {
        "my_secret_password": test_env_vars["MY_SECRET_PASSWORD"],
        "another_secret_value": test_env_vars["ANOTHER_SECRET_VALUE"],
    }
