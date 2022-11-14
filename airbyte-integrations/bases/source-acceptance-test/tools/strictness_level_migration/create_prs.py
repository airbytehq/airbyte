#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import argparse
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

from config_migration import migrate_configuration
from create_issues import COMMON_ISSUE_LABELS as COMMON_PR_LABELS
from create_issues import GITHUB_PROJECT_NAME
from definitions import GA_DEFINITIONS
from git import Repo
from jinja2 import Environment, FileSystemLoader

CONNECTORS_DIRECTORY = "../../../../connectors"
REPO_ROOT = "../../../../../"
AIRBYTE_REPO = Repo(REPO_ROOT)
environment = Environment(loader=FileSystemLoader("./templates/"))
PR_TEMPLATE = environment.get_template("pr.md.j2")

parser = argparse.ArgumentParser(description="Create PRs for migration of GA connectors to high test strictness level in SAT")
parser.add_argument("-d", "--dry", default=True)


logging.basicConfig(level=logging.DEBUG)


def migrate_acceptance_test_config(connector_name):
    acceptance_test_config_path = Path(CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-config.yml"
    return migrate_configuration(acceptance_test_config_path)


def checkout_new_branch(connector_name):
    AIRBYTE_REPO.heads.master.checkout()
    new_branch_name = f"{connector_name}/sat/migrate-to-high-test-strictness-level"
    new_branch = AIRBYTE_REPO.create_head(new_branch_name)
    new_branch.checkout()
    return new_branch


def commit_push_migrated_config(config_path, connector_name, new_branch, dry_run):
    process = subprocess.Popen(["pre-commit", "run", "--files", config_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()
    relative_config_path = f"airbyte-integrations/connectors/{connector_name}/acceptance-test-config.yml"
    AIRBYTE_REPO.git.add(relative_config_path)
    AIRBYTE_REPO.git.commit(m=f"Migrated config for {connector_name}")
    logging.info(f"Committed migrated config on {new_branch}")
    if not dry_run:
        AIRBYTE_REPO.git.push("--set-upstream", "origin", new_branch)
        logging.info(f"Pushed branch {new_branch} to origin")


def get_pr_content(definition):
    pr_title = f"Source {definition['name']}: enable `high` test strictness level in SAT"

    pr_body = PR_TEMPLATE.render(connector_name=definition["name"], release_stage=definition["releaseStage"])
    file_definition, pr_body_path = tempfile.mkstemp()

    with os.fdopen(file_definition, "w") as tmp:
        tmp.write(pr_body)

    return {"title": pr_title, "body_file": pr_body_path, "labels": COMMON_PR_LABELS}


def open_pr(definition, new_branch, dry_run):
    pr_content = get_pr_content(definition)
    list_command_arguments = ["gh", "pr", "list", "--state", "open", "--head", new_branch.name, "--json", "url"]
    create_command_arguments = [
        "gh",
        "pr",
        "create",
        "--draft",
        "--title",
        pr_content["title"],
        "--body-file",
        pr_content["body_file"],
        "--project",
        GITHUB_PROJECT_NAME,
    ]
    for label in pr_content["labels"]:
        create_command_arguments += ["--label", label]
    list_existing_pr_process = subprocess.Popen(list_command_arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = list_existing_pr_process.communicate()
    existing_prs = json.loads(stdout.decode())
    already_created = len(existing_prs) > 0
    if already_created:
        logging.warning(f"A PR was already created for this definition: {existing_prs[0]}")
    if not already_created:
        if not dry_run:
            process = subprocess.Popen(create_command_arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stderr:
                logging.error(stderr.decode())
            else:
                created_pr_url = stdout.decode()
                logging.info(f"Created PR for {definition['name']}: {created_pr_url}")
        else:
            logging.info(f"[DRY RUN]: {' '.join(create_command_arguments)}")
    os.remove(pr_content["body_file"])


def add_test_comment(definition, new_branch, dry_run):
    connector_name = definition["dockerRepository"].replace("airbyte/", "")
    comment = f"/test connector=connectors/{connector_name}"
    comment_command_arguments = ["gh", "pr", "comment", new_branch.name, "--body", comment]
    if not dry_run:
        process = subprocess.Popen(comment_command_arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = process.communicate()
        if stderr:
            logging.error(stderr.decode())
        else:
            logging.info("Added test comment")
    else:
        logging.info(f"[DRY RUN]: {' '.join(comment_command_arguments)}")


def migrate_config_on_new_branch(definition, dry_run):
    AIRBYTE_REPO.heads.master.checkout()
    connector_name = definition["dockerRepository"].replace("airbyte/", "")
    new_branch = checkout_new_branch(connector_name)
    config_path = migrate_acceptance_test_config(connector_name)
    commit_push_migrated_config(config_path, connector_name, new_branch, dry_run)
    return new_branch


def migrate_definition_and_open_pr(definition, dry_run):
    original_branch = AIRBYTE_REPO.active_branch
    new_branch = migrate_config_on_new_branch(definition, dry_run)
    open_pr(definition, new_branch, dry_run)
    add_test_comment(definition, new_branch, dry_run)
    original_branch.checkout()
    AIRBYTE_REPO.git.branch(D=new_branch)
    logging.info(f"Deleted branch {new_branch}")


if __name__ == "__main__":
    args = parser.parse_args()
    dry_run = False if args.dry == "False" or args.dry == "false" else True
    for definition in GA_DEFINITIONS[:1]:
        migrate_definition_and_open_pr(definition, dry_run=dry_run)
