#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import os
import random
import string
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock

import pytest
from destination_surrealdb import DestinationSurrealDB, surrealdb_connect
from destination_surrealdb.destination import (
    CONFIG_SURREALDB_DATABASE,
    CONFIG_SURREALDB_NAMESPACE,
    CONFIG_SURREALDB_PASSWORD,
    CONFIG_SURREALDB_TOKEN,
    CONFIG_SURREALDB_USERNAME,
)

from airbyte_cdk.models import (
    Status,
    Type,
)
from airbyte_cdk.models.airbyte_protocol_serializers import AirbyteMessageSerializer, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.sql.secrets import SecretString


CONFIG_PATH = "integration_tests/config.json"
# Should contain a valid SurrealDB connection config
# - surrealdb_url
# - surrealdb_username and surrealdb_password, or surrealdb_token
# - surrealdb_namespace (optional)
# - surrealdb_database (optional)
SECRETS_CONFIG_PATH = "secrets/config.json"


def pytest_generate_tests(metafunc):
    if "config" not in metafunc.fixturenames:
        return

    configs: list[str] = []
    # Check if surreal command is available
    try:
        result = subprocess.run(["surreal", "--version"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            configs.append("local_file_config")
        else:
            print(f"Skipping local SurrealDB tests because 'surreal' command not found or failed. Error: {result.stderr}")
    except FileNotFoundError:
        print("Skipping local SurrealDB tests because 'surreal' command not found.")

    if Path(SECRETS_CONFIG_PATH).is_file():
        configs.append("surrealdb_config")
    else:
        print(f"Skipping remote SurrealDB tests because config file not found at: {SECRETS_CONFIG_PATH}")

    # for test_name in ["test_check_succeeds", "test_write"]:
    metafunc.parametrize("config", configs, indirect=True)


@pytest.fixture(scope="module")
def test_namespace_name() -> str:
    letters = string.ascii_lowercase
    rand_string = "".join(random.choice(letters) for _ in range(6))
    return f"test_db_{rand_string}"


@pytest.fixture(scope="module")
def test_database_name() -> str:
    letters = string.ascii_lowercase
    rand_string = "".join(random.choice(letters) for _ in range(6))
    return f"test_db_{rand_string}"


@pytest.fixture
def config(request, test_namespace_name: str, test_database_name: str) -> Generator[Any, Any, Any]:
    if request.param == "local_file_config":
        process = None
        tmp_dir = tempfile.TemporaryDirectory()
        try:
            db_dir_path = os.path.join(str(tmp_dir.name), "test.surrealdb")
            os.makedirs(db_dir_path, exist_ok=True)
            cmd = [
                "surreal",
                "start",
                "--allow-all",
                "--user",
                "root",
                "--pass",
                "root",
                "--log",
                "trace",  # Or "debug" for more verbose logs if needed
                "--bind",
                "0.0.0.0:8000",
                f"rocksdb://{db_dir_path}",
            ]

            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

            # Wait for server to initialize.
            # A more robust check (e.g., trying to connect) could be added if necessary.
            time.sleep(3)

            if process.poll() is not None:
                # pylint: disable=C0301
                stderr_output = process.stderr.read().decode() if process.stderr else "No stderr output."
                raise RuntimeError(
                    f"Failed to start SurrealDB server. Exit code: {process.returncode}. "
                    f"Command: {' '.join(cmd)}. Stderr: {stderr_output}"
                )

            yield_config = {
                "surrealdb_url": "ws://localhost:8000",
                CONFIG_SURREALDB_USERNAME: SecretString("root"),
                CONFIG_SURREALDB_PASSWORD: SecretString("root"),
                CONFIG_SURREALDB_NAMESPACE: test_namespace_name,
                CONFIG_SURREALDB_DATABASE: test_database_name,
            }
            yield yield_config
        finally:
            # Ensure process is terminated
            # and all resources are cleaned up
            if process:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                if process.stderr:
                    process.stderr.close()
            tmp_dir.cleanup()

    elif request.param == "surrealdb_config":
        config_dict = json.loads(Path(SECRETS_CONFIG_PATH).read_text(encoding="utf-8"))
        # Prevent accidentally printing username, password, and token if `config_dict` is printed.
        if CONFIG_SURREALDB_TOKEN in config_dict:
            config_dict[CONFIG_SURREALDB_TOKEN] = SecretString(config_dict[CONFIG_SURREALDB_TOKEN])
        if CONFIG_SURREALDB_USERNAME in config_dict:
            config_dict[CONFIG_SURREALDB_USERNAME] = SecretString(config_dict[CONFIG_SURREALDB_USERNAME])
        if CONFIG_SURREALDB_PASSWORD in config_dict:
            config_dict[CONFIG_SURREALDB_PASSWORD] = SecretString(config_dict[CONFIG_SURREALDB_PASSWORD])
        yield config_dict

    else:
        raise ValueError(f"Unknown config type: {request.param}")


def test_check_succeeds(
    config: dict[str, str],
    request,
):
    destination = DestinationSurrealDB()
    status = destination.check(logger=MagicMock(), config=config)
    assert status.status == Status.SUCCEEDED, status.message


def test_write(
    config: dict[str, str],
    request,
):
    destination = DestinationSurrealDB()
    messages = Path("integration_tests/messages.jsonl").read_text(encoding="utf-8").splitlines()
    messages = [AirbyteMessageSerializer.load(json.loads(message)) for message in messages]
    configured_catalog = json.loads(Path("integration_tests/configured_catalog.json").read_text(encoding="utf-8"))
    configured_catalog = ConfiguredAirbyteCatalogSerializer.load(configured_catalog)
    wrote = destination.write(config=config, configured_catalog=configured_catalog, input_messages=messages)
    for m in wrote:
        assert m.type == Type.STATE
    sdb = surrealdb_connect(config)
    # Note that we don't check for existence of namespace and database here
    # because they are required for the destination to work
    sdb.use(config["surrealdb_namespace"], config["surrealdb_database"])
    outcome = sdb.select("airbyte_acceptance_table")
    # log the outcome
    print(outcome)
    assert len(outcome) == 1
    assert outcome[0]["_airbyte_extracted_at"] != datetime.fromtimestamp(1664705198575 / 1000, timezone.utc)
    assert isinstance(outcome[0]["_airbyte_extracted_at"], datetime)
    assert outcome[0]["column1"] == "test"
    assert outcome[0]["column2"] == 222
    assert outcome[0]["column3"] == datetime.fromisoformat("2022-06-20T18:56:18Z")
    assert outcome[0]["column4"] == 33.33
    assert outcome[0]["column5"] == [1, 2, None]
