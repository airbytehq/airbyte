import argparse
import os
import subprocess
import re
import json
from datetime import datetime, timedelta
from github import Github
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

DAYS_TO_KEEP_ORPHANED_JOBS = 90
SLACK_CHANNEL_FOR_NOTIFICATIONS = "infra-alerts"

# Initiate the parser
parser = argparse.ArgumentParser()

# Add long and short argument
parser.add_argument("--pat", "-p", help="Set github personal access token")
parser.add_argument("--sat", "-s", help="Set slack api token")

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
        gh_token = os.getenv('GITHUB_TOKEN')
    if not gh_token:
        raise Exception("Github personal access token not provided via args and not available in GITHUB_TOKEN variable")
    
    if args.sat:
        slack_token = args.sat
    else:
        slack_token = os.getenv('SLACK_TOKEN')
    if not slack_token:
        raise Exception("Slack app token not provided via args and not available in SLACK_TOKEN variable")

    g = Github(gh_token)

    git_url = subprocess.run(["git", "config", "--get", "remote.origin.url"], check=True, capture_output=True)  
    git_url_regex = re.compile(r'(?:git@|https://)github\.com[:/](.*?)(\.git|$)')
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
                message = "The Github Workflow '" + workflow.name + "' exists in " + repo_name + " but has no run newer than 90 days old. URL: " + workflow.html_url
                print("Sending Slack notification...")
                client = WebClient(slack_token)

                try:  response = client.chat_postMessage(channel = SLACK_CHANNEL_FOR_NOTIFICATIONS, text = message)
                except SlackApiError as e:  
                    print(e, '\n\n')
                    raise Exception("Error calling the Slack API")
            break

if __name__ == '__main__':
    main()
