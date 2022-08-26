import argparse
import os
import subprocess
import re
from datetime import datetime, timedelta
from github import Github

DAYS_TO_KEEP_ORPHANED_JOBS = 90

# Initiate the parser
parser = argparse.ArgumentParser()

# Add long and short argument
parser.add_argument("--pat", "-p", help="Set github personal access token")
parser.add_argument("--dry", "-d", default=True, help="Dry run, prints which runs will be purged. True by default. Pass False to run the deletion.")

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
    git_url_regex = re.compile(r'(?:git@|https://)github\.com[:/](.*?)(\.git|$)')
    re_match = git_url_regex.match(git_url.stdout.decode("utf-8"))

    repo = g.get_repo(re_match.group(1))
    workflows = repo.get_workflows()

    runs_to_delete = []

    for workflow in workflows:
         # it's not in the current branch and it hasn't been touched in 90 days
        if not os.path.exists(workflow.path) and workflow.updated_at < datetime.now() - timedelta(days=DAYS_TO_KEEP_ORPHANED_JOBS):
            runs = workflow.get_runs()
            for run in runs:
                if not args.dry:
                    print("Deleting run id " + str(run.id))
                    run.delete()
                else:
                    runs_to_delete.append((workflow.name, run.id, run.created_at.strftime("%m/%d/%Y, %H:%M:%S")))
                
    if args.dry:
        print("[DRY RUN] A total of " + str(len(runs_to_delete)) + " runs would be deleted: ")
        for run in runs_to_delete:
            print(run)


if __name__ == '__main__':
    main()
