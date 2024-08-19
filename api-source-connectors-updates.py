# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import argparse
import os
import re
import subprocess
from datetime import datetime, timedelta

from github import Github

DAYS_TO_KEEP_ORPHANED_JOBS = 90

"""
This script is intended to be run in conjunction with identify-dormant-workflows.py to keep GitHub actions clean.

The basic workflow is:

1. identify-dormant-workflows.py notifies of dormant workflows (workflows that have no runs newer than DAYS_TO_KEEP_ORPHANED_JOBS days) daily.
2. Manually notify the infra team via Slack.
3. Infra team checks with stakeholders to ensure dormant jobs can be deleted and then cleans up workflow runs manually.
4. cleanup-workflows.py deletes old workflow runs (older than DAYS_TO_KEEP_ORPHANED_JOBS) that have no associated workflow.

We need to clean up the runs because even if a workflow is deleted, the runs linger in the UI. 
We don't want to delete workflow runs newer than 90 days on GitHub actions, even if the workflow doesn't exist.
It's possible that people might test things off the master branch and we don't want to delete their recent runs.
"""

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--pat", "-p", help="Set GitHub personal access token")
    parser.add_argument(
        "--delete",
        "-d",
        action="store_true",
        help="By default, the script will only print runs that will be deleted. Pass --delete to actually delete them",
    )
    return parser.parse_args()

def get_github_token(args):
    """Retrieve GitHub token from arguments or environment variables."""
    token = args.pat or os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GitHub personal access token not provided via args and not available in GITHUB_TOKEN variable")
    return token

def get_repository(github_instance):
    """Retrieve the GitHub repository using the git remote URL."""
    git_url = subprocess.run(["git", "config", "--get", "remote.origin.url"], check=True, capture_output=True)
    git_url_regex = re.compile(r"(?:git@|https://)github\.com[:/](.*?)(\.git|$)")
    re_match = git_url_regex.match(git_url.stdout.decode("utf-8"))

    if not re_match:
        raise ValueError("Failed to parse the git URL. Ensure that it's a valid GitHub repository URL.")
    
    repo_name = re_match.group(1)
    return github_instance.get_repo(repo_name)

def collect_runs_to_delete(repo, args):
    """Collect workflow runs that should be deleted."""
    workflows = repo.get_workflows()
    runs_to_delete = []

    for workflow in workflows:
        if not os.path.exists(workflow.path):  # Workflow is not in the current branch
            runs_to_delete += collect_runs_for_workflow(workflow, args)

    return runs_to_delete

def collect_runs_for_workflow(workflow, args):
    """Collect runs for a specific workflow that should be deleted."""
    runs_to_delete = []
    runs = workflow.get_runs()
    
    for run in runs:
        if run.updated_at > datetime.now() - timedelta(days=DAYS_TO_KEEP_ORPHANED_JOBS):
            break  # Don't clean up if it has a run newer than 90 days

        if args.delete:
            delete_run(run)
        else:
            runs_to_delete.append((workflow.name, run.id, run.created_at.strftime("%m/%d/%Y, %H:%M:%S")))

    return runs_to_delete

def delete_run(run):
    """Delete a specific workflow run."""
    print("Deleting run id " + str(run.id))
    run._requester.requestJson("DELETE", run.url)  # Normally use run.delete(), but it's not yet in PyPI

def main():
    """Main function to execute the cleanup process."""
    args = parse_arguments()
    token = get_github_token(args)
    github_instance = Github(token)
    
    repo = get_repository(github_instance)
    runs_to_delete = collect_runs_to_delete(repo, args)
    
    if not args.delete:
        print("[DRY RUN] A total of " + str(len(runs_to_delete)) + " runs would be deleted: ")
        for run in runs_to_delete:
            print(run)

if __name__ == "__main__":
    main()
