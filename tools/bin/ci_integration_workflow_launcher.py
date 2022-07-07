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
import uuid
from urllib.parse import parse_qsl, urljoin, urlparse

import requests

ORGANIZATION = "airbytehq"
REPOSITORY = "airbyte"
LOGGING_FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
API_URL = "https://api.github.com"
BRANCH = "grubberr/14450-connector-integration-tests"
WORKFLOW_PATH = ".github/workflows/test-command.yml"
RUN_ID_REGEX = re.compile(r"UUID ([0-9a-f-]+)")


GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    logging.error("GITHUB_TOKEN not set...")
    sys.exit(1)


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


def get_connector_names():
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


def get_job_run_uuid(jobs):
    if jobs and len(jobs[0]["steps"]) >= 2:
        return jobs[0]["steps"][1]["name"]


def get_job_start_aws(jobs):
    if (
        len(jobs) >= 2
        and len(jobs[1]["steps"]) >= 3
        and jobs[1]["steps"][2]["name"] == "Start AWS Runner"
        and jobs[1]["steps"][2]["conclusion"] == "failure"
    ):
        return True


def search_workflow_runs(owner, repo, workflow_id, run_uuids):
    run_uuids = set(run_uuids)
    now = datetime.datetime.utcnow()
    res = set()
    for workflow_run in iter_workflow_runs(owner, repo):

        if not run_uuids:
            break

        created_at = datetime.datetime.strptime(workflow_run["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        period = now - created_at
        if period.days >= 1:
            break

        if workflow_run["workflow_id"] != workflow_id:
            continue
        if workflow_run["head_branch"] != BRANCH:
            continue

        response_json = get_response_json(workflow_run["jobs_url"])
        job_run_uuid_label = get_job_run_uuid(response_json["jobs"])
        if not job_run_uuid_label:
            continue

        run_uuid = None
        m = re.match(RUN_ID_REGEX, job_run_uuid_label)
        if m:
            run_uuid = m.groups()[0]

        if not run_uuid:
            continue

        if run_uuid in run_uuids:
            run_uuids.remove(run_uuid)
            if get_job_start_aws(response_json["jobs"]):
                res.add(run_uuid)
    return res


def main():
    workflow_id = get_workflow_id(ORGANIZATION, REPOSITORY, WORKFLOW_PATH)
    if not workflow_id:
        logging.error(f"Cannot find workflow path '{WORKFLOW_PATH}'")
        sys.exit(1)

    connector_names = get_connector_names()
    run_uuid_to_name = {}
    for connector_name in connector_names:
        run_uuid = workflow_dispatch(ORGANIZATION, REPOSITORY, workflow_id, connector_name)
        logging.info(f"Dispatch workflow for connector {connector_name}, UUID: {run_uuid}")
        run_uuid_to_name[run_uuid] = connector_name

    res = search_workflow_runs(ORGANIZATION, REPOSITORY, workflow_id, run_uuid_to_name.keys())
    for run_uuid in res:
        connector_name = run_uuid_to_name[run_uuid]
        run_uuid = workflow_dispatch(ORGANIZATION, REPOSITORY, workflow_id, connector_name)
        logging.info(f"Re-dispatch workflow for connector {connector_name}, UUID: {run_uuid}")


if __name__ == "__main__":
    logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)
    main()
