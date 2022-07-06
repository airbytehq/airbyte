#!/usr/bin/env python3
#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
import sys
import requests
import subprocess

REPO_API = "https://api.github.com/repos/airbytehq/airbyte"
TEST_COMMAND = ".github/workflows/test-command.yml"
MAX_RUNNING_MASTER_WORKFLOWS = 5


GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("GITHUB_TOKEN not set...")
    sys.exit(1)

response = requests.get(
    REPO_API + "/actions/workflows",
    headers={"Authorization": "Bearer " + GITHUB_TOKEN})
response.raise_for_status()
response_json = response.json()

for workflow in response_json["workflows"]:
    if workflow["path"] == TEST_COMMAND:
        workflow_id = workflow["id"]

print(workflow_id)

response = requests.get(
    REPO_API + f"/actions/workflows/{workflow_id}/runs?branch=master&status=in_progress",
    headers={"Authorization": "Bearer " + GITHUB_TOKEN})

response_json = response.json()
total_count = response_json["total_count"]

print(total_count)

process = subprocess.run(
    ["./gradlew", "integrationTest", "--dry-run"], check=True, capture_output=True, universal_newlines=True)

def get_connector_names(output):
    names = []
    lines = output.splitlines()
    for line in lines:
        if "integrationTest SKIPPED" in line:
            res = line.split(":")
            if res[1] == "airbyte-integrations" and res[2] == "connectors":
                names.append(res[3])
    return names


names = get_connector_names(process.stdout)

for name in names:
    print(REPO_API + f"/actions/workflows/{workflow_id}/dispatches")
    """
    response = requests.post(
        REPO_API + f"/actions/workflows/{workflow_id}/dispatches",
        headers={"Authorization": "Bearer " + GITHUB_TOKEN},
        json={"ref": "master", "inputs": {"connector": name}})
    """
