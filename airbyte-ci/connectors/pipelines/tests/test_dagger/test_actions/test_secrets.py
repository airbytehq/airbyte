#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json

import pytest
from pipelines.dagger.actions import secrets

pytestmark = [
    pytest.mark.anyio,
]


async def test_load_from_local_directory_not_exists(mocker, tmp_path):
    context = mocker.MagicMock()
    context.connector.code_directory = tmp_path
    result = await secrets.load_from_local(context)
    assert result == {}
    context.logger.warning.assert_called_with(f"Local secrets directory {tmp_path / 'secrets'} does not exist, no secrets will be loaded.")


async def test_load_from_local_empty_directory(mocker, tmp_path):
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    context = mocker.MagicMock()
    context.connector.code_directory = tmp_path

    result = await secrets.load_from_local(context)

    assert result == {}
    context.logger.warning.assert_called_with(f"Local secrets directory {secrets_dir} is empty, no secrets will be loaded.")


async def test_load_from_local_with_secrets(mocker, tmp_path, dagger_client):
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()

    first_dummy_config = json.dumps({"dummy": "config_a"})
    second_dummy_config = json.dumps({"dummy": "config_b"})
    (secrets_dir / "dummy_config_a.json").write_text(first_dummy_config)
    (secrets_dir / "dummy_config_b.json").write_text(second_dummy_config)

    context = mocker.MagicMock()
    context.dagger_client = dagger_client
    context.connector.code_directory = tmp_path

    result = await secrets.load_from_local(context)
    assert len(result) == 2, "All secrets should be loaded from the local secrets directory"
    assert (
        await result["dummy_config_a.json"].plaintext() == first_dummy_config
    ), "The content of dummy_config_a.json should be loaded as a secret"
    assert (
        await result["dummy_config_b.json"].plaintext() == second_dummy_config
    ), "The content of dummy_config_b.json should be loaded as a secret"
