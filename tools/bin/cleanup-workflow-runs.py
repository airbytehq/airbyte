import argparse
import os
import subprocess
import re
from datetime import datetime, timedelta
from github import Github

DAYS_TO_KEEP_ORPHANED_JOBS = 90


'''

This script is intended to be run in conjuction with identify-dormant-workflows.py to keep GH actions clean.

The basic workflow is 

identify-dormant-workflows.py notifies of dormant workflows (workflows that have no runs newer than DAYS_TO_KEEP_ORPHANED_JOBS days) daily -> 
manually notifies infra team via slack ->
infra team checks with stakeholders to ensure dormant jobs can be deleted and then cleans up workflow runs manually ->
cleanup-workflows.py deletes old workflow runs (again older than DAYS_TO_KEEP_ORPHANED_JOBS) that have no associated workflow

We need to clean up the runs because even if a workflow is deleted, the runs linger in the UI. 
We don't want to delete workflow runs newer than 90 days on GH actions, even if the workflow doesn't exist.
it's possible that people might test things off the master branch and we don't want to delete their recent runs

'''

# Initiate the parser
parser = argparse.ArgumentParser()

# Add long and short argument
parser.add_argument("--pat", "-p", help="Set github personal access token")
parser.add_argument("--delete", "-d", action='store', nargs='*', help="By default, the script will only print runs that will be deleted. Pass --delete to actually delete them")

def main():
    # Read arguments from the command line
    args = parser.parse_args()
    # Check for user supplied PAT. If not supplied, assume we are running in actions
    # and pull from environment

    token = None

    if args.pat:
        token = args.pat
    else:
        token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise Exception("Github personal access token not provided via args and not available in GITHUB_TOKEN variable")

    g = Github(token)

    git_url = subprocess.run(["git", "config", "--get", "remote.origin.url"], check=True, capture_output=True)  

    # will match both forms (git and https url) of github e.g.
    # git@github.com:airbytehq/airbyte.git
    # https://github.com/airbytehq/airbyte.git

    git_url_regex = re.compile(r'(?:git@|https://)github\.com[:/](.*?)(\.git|$)') 
    re_match = git_url_regex.match(git_url.stdout.decode("utf-8"))

    repo = g.get_repo(re_match.group(1))
    workflows = repo.get_workflows()

    runs_to_delete = []

    for workflow in workflows:
        if not os.path.exists(workflow.path): # it's not in the current branch 
            runs = workflow.get_runs()
            for run in runs:
                if run.updated_at > datetime.now() - timedelta(days=DAYS_TO_KEEP_ORPHANED_JOBS): 
                    break # don't clean up if it has a run newer than 90 days
                if args.delete is not None:
                    print("Deleting run id " + str(run.id))
                    run.delete()
                else:
                    runs_to_delete.append((workflow.name, run.id, run.created_at.strftime("%m/%d/%Y, %H:%M:%S")))
                
    if args.delete is None:
        print("[DRY RUN] A total of " + str(len(runs_to_delete)) + " runs would be deleted: ")
        for run in runs_to_delete:
            print(run)


if __name__ == '__main__':
    main()
