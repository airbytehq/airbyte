#

# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import asyncio
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path
import traceback
from typing import Dict, List, Optional, Tuple

import aiofiles
import aiohttp
import requests
import yaml

INTEGRATION_TEST_WORKSPACE_ID = "112412bb-78aa-4ca6-aace-ae0b83be2215"  # name: integration-test-sandboxes
INTEGRATION_TEST_DEV_NULL_DESTINATION_ID = "a2654ecb-2bad-4f8e-baf0-d7e5085a1ed1"
INTEGRATION_TEST_DEV_NULL_DESTINATION_NAME = "dev_null"
REPO_ROOT = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode())
CONNECTORS_DIR = REPO_ROOT / Path("airbyte-integrations/connectors")
API_KEY_PATH = Path(os.getenv("AIRBYTE_API_KEY_PATH", ""))


try:
    with open(API_KEY_PATH, "r") as fp:
        API_KEY = fp.read()
except FileNotFoundError:
    raise FileNotFoundError("AIRBYTE_API_KEY_PATH is required but was not set.")
else:
    assert API_KEY, f"The API key is required but was not found at {API_KEY_PATH}."


async def create_source(source_name: str, config_path: Path, session: aiohttp.ClientSession):
    url = "https://api.airbyte.com/v1/sources"

    with open(config_path, "r") as fp:
        config = json.loads(fp.read())

    source_connection_name = f"{source_name}_{config_path.stem}"
    payload = {
        "name": source_connection_name,
        "workspaceId": INTEGRATION_TEST_WORKSPACE_ID,
        "configuration": {"sourceType": source_name, **config},
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {API_KEY}",
    }
    response = await session.post(url, data=json.dumps(payload), headers=headers)
    if not (200 <= response.status < 400):
        raise ValueError(f"{source_connection_name}: {await response.text()}")


def _is_eligible_connector(connector_dir: str) -> Tuple[bool, Optional[str]]:
    if connector_dir in DONE_SOURCES:
        return False, "done"

    if connector_dir.startswith("source-"):
        metadata_file = CONNECTORS_DIR / Path(connector_dir) / "metadata.yaml"
        try:
            with open(metadata_file, "r") as fp:
                metadata = yaml.load(fp, yaml.FullLoader)
        except FileNotFoundError:
            return False, "metadata.yml not found"
        if metadata["data"].get("connectorType") != "source" or "language:python" not in metadata["data"].get("tags"):
            return False, "not a python source"
        if "secrets" not in os.listdir(CONNECTORS_DIR / connector_dir):
            return False, "no secrets"
        return True, None
    else:
        return False, "not a source"


async def _create_python_source_connectors_with_sandboxes(session: aiohttp.ClientSession) -> Tuple[List, Dict, List]:
    skips = []
    sources = defaultdict(list)
    source_errors = []
    for connector_dir in sorted(os.listdir(CONNECTORS_DIR)):
        is_eligible, reason = _is_eligible_connector(connector_dir)
        if is_eligible:
            source_name = connector_dir.split("-", 1)[-1]
            for config_path in os.listdir(CONNECTORS_DIR / connector_dir / "secrets"):
                try:
                    source = await create_source(source_name, CONNECTORS_DIR / connector_dir / "secrets" / config_path, session)
                except Exception:
                    source_errors.append({"name": source_name, "config_path": config_path, "error": str(traceback.format_exc())})
                else:
                    sources[connector_dir].append(source)
        else:
            skips.append({"connector_name": connector_dir, "reason": reason})

    return skips, sources, source_errors


async def do_create_python_source_connectors_with_sandboxes() -> Tuple[List, Dict, List]:
    async with aiohttp.ClientSession() as session:
        return await _create_python_source_connectors_with_sandboxes(session)


def get_created_sources() -> List[Tuple[str, str]]:
    created = []
    url = f"https://api.airbyte.com/v1/sources?includeDeleted=false&workspaceIds={INTEGRATION_TEST_WORKSPACE_ID}&limit=100&offset=0"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {API_KEY}",
    }
    while url:
        response = requests.get(url, headers=headers)
        created.extend([(d["name"], d["sourceId"]) for d in response.json()["data"]])
        url = response.json()["next"]

    return created


def get_created_connections() -> List[Tuple[str, str]]:
    created = []
    base_url = f"https://api.airbyte.com/v1/connections?includeDeleted=false&workspaceIds={INTEGRATION_TEST_WORKSPACE_ID}&limit=100&offset="
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {API_KEY}",
    }
    offset = 0
    while True:
        url = base_url + str(offset)
        response = requests.get(url, headers=headers)
        data = response.json().get("data")
        if data:
            created.extend([(d["name"], d["connectionId"]) for d in data])
            offset += 100
        else:
            break
    return created


async def get_streams_for_source(connection_name: str, source_id: str, session: aiohttp.ClientSession):
    url = f"https://api.airbyte.com/v1/streams?sourceId={source_id}&ignoreCache=false"

    headers = {"accept": "application/json", "authorization": f"Bearer {API_KEY}"}

    response = await session.get(url, headers=headers)
    if not (200 <= response.status < 400):
        raise ValueError(f"{connection_name}: {await response.text()}")
    return await response.json()


async def _configure_streams(connection_name: str, source_id: str, session: aiohttp.ClientSession) -> List[Dict]:
    streams = await get_streams_for_source(connection_name, source_id, session)
    configured_streams = [
        {
            "name": s["streamName"],
            "syncMode": "incremental_append" if s["defaultCursorField"] else "full_refresh_overwrite",
            "cursorField": s["defaultCursorField"],
            "primaryKey": s["sourceDefinedPrimaryKey"],
        }
        for s in streams
    ]
    return configured_streams


async def create_connection(source_id: str, connection_name: str, session: aiohttp.ClientSession) -> Dict:
    url = "https://api.airbyte.com/v1/connections"
    streams = await _configure_streams(connection_name, source_id, session)
    payload = {
        "name": connection_name,
        "sourceId": source_id,
        "destinationId": INTEGRATION_TEST_DEV_NULL_DESTINATION_ID,
        "configurations": {
            "streams": streams,
        },
        "schedule": {
            "scheduleType": "cron",
            "cronExpression": "0 0 22 * * ?",  # daily at 10pm
        },
        "dataResidency": "us",
        "namespaceDefinition": "destination",
        "namespaceFormat": None,
        "nonBreakingSchemaUpdatesBehavior": "ignore",
        "status": "active",
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {API_KEY}",
    }
    response = await session.post(url, json=payload, headers=headers)
    if not (200 <= response.status < 400):
        raise ValueError(f"{connection_name}: {await response.text()}")
    return await response.json()


async def _create_connections(session: aiohttp.ClientSession) -> Tuple[List, List]:
    connections_created = []
    connection_errors = []
    tasks = []
    for source_name, source_id in get_created_sources():
        connection_name = f"{source_name}_{INTEGRATION_TEST_DEV_NULL_DESTINATION_NAME}"
        if connection_name in DONE_CONNECTIONS:
            print(f"Skipping {connection_name}; connection exists")
            continue
        print(f"Creating connection {connection_name}")
        tasks.append(asyncio.Task(create_connection(source_id, connection_name, session)))

    for task in await asyncio.gather(*tasks, return_exceptions=True):
        if isinstance(task, Exception):
            connection_errors.append(str(task))
        else:
            connections_created.append(task)

    return connections_created, connection_errors


async def do_create_connections():
    async with aiohttp.ClientSession() as session:
        connections_created, connection_errors = await _create_connections(session)
    return connections_created, connection_errors


if __name__ == "__main__":
    # First, run `VERSION=dev ci_credentials all write-to-storage`
    # for each python source config
    #    create a source in airbyte cloud                                    << Which workspace?
    #    create a connection in airbyte cloud using the dest created above   << naming convention? sync frequency?
    loop = asyncio.get_event_loop()
    DONE_SOURCES = {name for name, _ in get_created_sources()}
    with open("skipped_sources", "r") as fp:
        for line in fp:
            DONE_SOURCES.add(json.loads(line.strip())["connector_name"])

    # _skips, _sources, _source_errors = loop.run_until_complete(do_create_python_source_connectors_with_sandboxes())
    #
    # print("\n Created sources")
    # for _source in _sources:
    #     print(_source)
    #
    # print("\nSkipped:")
    # with open("skipped_sources", "w") as fp:
    #     for _skip in _skips:
    #         fp.write(f"{_skip}\n")
    #         print(_skip)
    #
    # print("\nSource creation errors:")
    # with open("source_creation_errors.jsonl", "w") as fp:
    #     for _source_error in _source_errors:
    #         json.dump(_source_error, fp)
    #         fp.write("\n")
    #         print(_source_error)

    DONE_CONNECTIONS = {name for name, _ in get_created_connections()}
    _connections_created, _connection_errors = loop.run_until_complete(do_create_connections())

    print("\n Created connections")
    for _connection in sorted(_connections_created, key=lambda x: x["name"]):
        print(_connection["name"])

    print("\n Connection creation errors")
    with open("connection_creation_errors.jsonl", "w") as fp:
        for _connection_error in _connection_errors:
            json.dump(_connection_error, fp)
            fp.write("\n")
            print(_connection_error)
