#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timedelta

from github import Github
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


DAYS_TO_KEEP_ORPHANED_JOBS = 90
SLACK_CHANNEL_FOR_NOTIFICATIONS = "infra-alerts"


"""

This script is intended to be run in conjuction with cleanup-workflow-runs.py to keep GH actions clean.

The basic workflow is 

identify-dormant-workflows.py notifies of dormant workflows (workflows that have no runs newer than DAYS_TO_KEEP_ORPHANED_JOBS days) daily -> 
manually notifies infra team via slack ->
infra team checks with stakeholders to ensure dormant jobs can be deleted and then cleans up workflow runs manually ->
cleanup-workflows.py deletes old workflow runs (again older than DAYS_TO_KEEP_ORPHANED_JOBS) that have no associated workflow

We need to clean up the runs because even if a workflow is deleted, the runs linger in the UI. 
We don't want to delete workflow runs newer than 90 days on GH actions, even if the workflow doesn't exist.
it's possible that people might test things off the master branch and we don't want to delete their recent runs

"""

# Initiate the parser
parser = argparse.ArgumentParser()

# Add long and short argument
parser.add_argument("--pat", "-p", help="Set github personal access token")
parser.add_argument("--sat", "-s", help="Set slack api token. Optional. If not passed, will just print to console")


def main():
    # Read arguments from the command line
    args = parser.parse_args()

    # Check for user supplied PAT. If not supplied, assume we are running in actions
    # and pull from environment
    gh_token = None
    slack_token = None

    if args.pat:
        gh_token = args.pat
    else:
        gh_token = os.getenv("GITHUB_TOKEN")
    if not gh_token:
        raise Exception("Github personal access token not provided via args and not available in GITHUB_TOKEN variable")

    if args.sat:
        slack_token = args.sat
    else:
        slack_token = os.getenv("SLACK_TOKEN")

    g = Github(gh_token)

    git_url = subprocess.run(["git", "config", "--get", "remote.origin.url"], check=True, capture_output=True)

    # will match both forms (git and https url) of github e.g.
    # git@github.com:airbytehq/airbyte.git
    # https://github.com/airbytehq/airbyte.git

    git_url_regex = re.compile(r"(?:git@|https://)github\.com[:/](.*?)(\.git|$)")
    re_match = git_url_regex.match(git_url.stdout.decode("utf-8"))

    repo_name = re_match.group(1)

    repo = g.get_repo(repo_name)
    workflows = repo.get_workflows()

    runs_to_delete = []

    for workflow in workflows:
        runs = workflow.get_runs()
        for run in runs:
            # check and see if a workflow exists but is not actively being triggered/run
            if os.path.exists(workflow.path) and run.updated_at < datetime.now() - timedelta(days=DAYS_TO_KEEP_ORPHANED_JOBS):
                message = (
                    "The Github Workflow '"
                    + workflow.name
                    + "' exists in "
                    + repo_name
                    + " but has no run newer than 90 days old. URL: "
                    + workflow.html_url
                )
                print(message)

                if slack_token:
                    print("Sending Slack notification...")
                    client = WebClient(slack_token)

                    try:
                        response = client.chat_postMessage(channel=SLACK_CHANNEL_FOR_NOTIFICATIONS, text=message)
                    except SlackApiError as e:
                        print(e, "\n\n")
                        raise Exception("Error calling the Slack API")
            break


if __name__ == "__main__":
    main()
