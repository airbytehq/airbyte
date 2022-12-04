#!/usr/bin/env python3
#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
import os
import re
import subprocess
import sys
import time
import uuid
from functools import lru_cache
from urllib.parse import parse_qsl, urljoin, urlparse

import requests
import yaml

ORGANIZATION = "airbytehq"
REPOSITORY = "airbyte"
LOGGING_FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
API_URL = "https://api.github.com"
BRANCH = "master"
WORKFLOW_PATH = ".github/workflows/test-command.yml"
RUN_UUID_REGEX = re.compile("^UUID ([0-9a-f-]+)$")
SLEEP = 1200
SOURCE_DEFINITIONS = "airbyte-config/init/src/main/resources/seed/source_definitions.yaml"
DESTINATION_DEFINITIONS = "./airbyte-config/init/src/main/resources/seed/destination_definitions.yaml"
STAGES = ["alpha", "beta", "generally_available"]


GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    logging.error("GITHUB_TOKEN not set...")
    sys.exit(1)


def check_start_aws_runner_failed(jobs):
    """
    !!! WARNING !!! WARNING !!! WARNING !!!
    !!! WARNING !!! WARNING !!! WARNING !!!
    !!! WARNING !!! WARNING !!! WARNING !!!

    If workflow {WORKFLOW_PATH} structure will change in future
    there is a chance that we would need to update this function too.
    """
    return (
        len(jobs) >= 2
        and len(jobs[1]["steps"]) >= 3
        and jobs[1]["steps"][2]["name"] == "Start AWS Runner"
        and jobs[1]["steps"][2]["conclusion"] == "failure"
    )


def get_run_uuid(jobs):
    """
    This function relies on assumption that the first step of the first job

    - name: UUID ${{ github.event.inputs.uuid }}
      run: true
    """
    if jobs and len(jobs[0]["steps"]) >= 2:
        name = jobs[0]["steps"][1]["name"]
        m = re.match(RUN_UUID_REGEX, name)
        if m:
            return m.groups()[0]


def get_response(url_or_path, params=None):
    url = urljoin(API_URL, url_or_path)
    response = requests.get(url, params=params, headers={"Authorization": "Bearer " + GITHUB_TOKEN})
    response.raise_for_status()
    return response


def get_response_json(url_or_path, params=None):
    response = get_response(url_or_path, params=params)
    return response.json()


def get_workflow_id(owner, repo, path):
    response_json = get_response_json(f"/repos/{owner}/{repo}/actions/workflows")
    for workflow in response_json["workflows"]:
        if workflow["path"] == path:
            return workflow["id"]


def workflow_dispatch(owner, repo, workflow_id, connector):
    run_uuid = str(uuid.uuid4())
    url = urljoin(API_URL, f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches")
    response = requests.post(
        url, headers={"Authorization": "Bearer " + GITHUB_TOKEN}, json={"ref": BRANCH, "inputs": {"connector": connector, "uuid": run_uuid}}
    )
    response.raise_for_status()
    return run_uuid


@lru_cache
def get_gradlew_integrations():
    process = subprocess.run(["./gradlew", "integrationTest", "--dry-run"], check=True, capture_output=True, universal_newlines=True)
    res = []
    for line in process.stdout.splitlines():
        parts = line.split(":")
        if (
            len(parts) >= 4
            and parts[1] == "airbyte-integrations"
            and parts[2] in ["connectors", "bases"]
            and parts[-1] == "integrationTest SKIPPED"
        ):
            res.append(parts[3])
    return res


@lru_cache
def get_definitions(definition_type):
    assert definition_type in ["source", "destination"]
    filename = SOURCE_DEFINITIONS
    if definition_type == "destination":
        filename = DESTINATION_DEFINITIONS
    with open(filename) as fp:
        return yaml.safe_load(fp)


def normalize_stage(stage):
    stage = stage.lower()
    if stage == "ga":
        stage = "generally_available"
    return stage


def get_integrations(names):
    res = set()
    for name in names:
        parts = name.split(":")
        if len(parts) == 2:
            definition_type, stage = parts
            stage = normalize_stage(stage)
            if stage == "all":
                for integration in get_gradlew_integrations():
                    if integration.startswith(definition_type + "-"):
                        res.add(integration)
            elif stage in STAGES:
                for definition in get_definitions(definition_type):
                    if definition.get("releaseStage", "alpha") == stage:
                        res.add(definition["dockerRepository"].partition("/")[2])
            else:
                logging.warning(f"unknown stage: '{stage}'")
        else:
            integration = parts[0]
            airbyte_integrations = get_gradlew_integrations()
            if integration in airbyte_integrations:
                res.add(integration)
            else:
                logging.warning(f"integration not found: {integration}")
    return res


def iter_workflow_runs(owner, repo, per_page=100):
    path = f"/repos/{owner}/{repo}/actions/runs"
    page = None
    while True:
        params = {"per_page": per_page}
        if page:
            params["page"] = page
        response = get_response(path, params=params)
        response_json = response.json()
        for workflow_run in response_json["workflow_runs"]:
            yield workflow_run
        if "next" not in response.links:
            break
        page = dict(parse_qsl(urlparse(response.links["next"]["url"]).query))["page"]


def search_failed_workflow_runs(owner, repo, workflow_id, run_uuids):
    run_uuids = set(run_uuids)
    now = datetime.datetime.utcnow()
    res = set()
    for workflow_run in iter_workflow_runs(owner, repo):
        if not run_uuids:
            break

        created_at = datetime.datetime.strptime(workflow_run["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        period = now - created_at
        if period.seconds > 10800:
            break

        if workflow_run["workflow_id"] != workflow_id:
            continue
        if workflow_run["head_branch"] != BRANCH:
            continue
        if workflow_run["conclusion"] != "failure":
            continue

        response_json = get_response_json(workflow_run["jobs_url"])
        run_uuid = get_run_uuid(response_json["jobs"])
        if not run_uuid:
            continue

        if run_uuid in run_uuids:
            run_uuids.remove(run_uuid)
            if check_start_aws_runner_failed(response_json["jobs"]):
                res.add(run_uuid)
    return res


def main():
    workflow_id = get_workflow_id(ORGANIZATION, REPOSITORY, WORKFLOW_PATH)
    if not workflow_id:
        logging.error(f"Cannot find workflow path '{WORKFLOW_PATH}'")
        sys.exit(1)

    integration_names = get_integrations(sys.argv[1:])
    run_uuid_to_name = {}
    for integration_name in integration_names:
        run_uuid = workflow_dispatch(ORGANIZATION, REPOSITORY, workflow_id, integration_name)
        logging.info(f"Dispatch workflow for connector {integration_name}, UUID: {run_uuid}")
        run_uuid_to_name[run_uuid] = integration_name
        # to avoid overloading system
        time.sleep(1)

    logging.info(f"Sleeping {SLEEP} seconds")
    time.sleep(SLEEP)

    run_uuids = search_failed_workflow_runs(ORGANIZATION, REPOSITORY, workflow_id, run_uuid_to_name.keys())
    for run_uuid in run_uuids:
        integration_name = run_uuid_to_name[run_uuid]
        run_uuid = workflow_dispatch(ORGANIZATION, REPOSITORY, workflow_id, integration_name)
        logging.info(f"Re-dispatch workflow for connector {integration_name}, UUID: {run_uuid}")


if __name__ == "__main__":
    logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)
    main()
