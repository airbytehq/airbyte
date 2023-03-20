#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import argparse
import json
import logging
import os
import subprocess
import tempfile

from definitions import GA_DEFINITIONS
from jinja2 import Environment, FileSystemLoader

from create_prs import is_airbyte_connector

# SET THESE BEFORE USING THE SCRIPT
MODULE_NAME = "fail_on_extra_columns"
GITHUB_PROJECT_NAME = "column-selection-sources"
COMMON_ISSUE_LABELS = ["area/connectors", "team/connectors-python", "type/enhancement", "column-selection-sources"]
ISSUE_TITLE = "Add undeclared columns to spec"

# Don't need to set these
TEMPLATES_FOLDER = "./templates/"

logging.basicConfig(level=logging.DEBUG)
environment = Environment(loader=FileSystemLoader(TEMPLATES_FOLDER))

parser = argparse.ArgumentParser(
    description="Create issues for a list of connectors from a template."
)
parser.add_argument("-d", "--dry", default=True)


def get_issue_content(source_definition):
    issue_title = f"Source {source_definition['name']}: {ISSUE_TITLE}"

    template = environment.get_template(f"{MODULE_NAME}/issue.md.j2")
    issue_body = template.render(connector_name=source_definition["name"], release_stage=source_definition["releaseStage"])
    file_definition, issue_body_path = tempfile.mkstemp()

    with os.fdopen(file_definition, "w") as tmp:
        tmp.write(issue_body)

    return {"title": issue_title, "body_file": issue_body_path, "labels": COMMON_ISSUE_LABELS}


def create_issue(source_definition, dry_run=True):
    issue_content = get_issue_content(source_definition)
    list_command_arguments = ["gh", "issue", "list", "--state", "open", "--search", f"'{issue_content['title']}'", "--json", "url"]

    create_command_arguments = [
        "gh",
        "issue",
        "create",
        "--title",
        issue_content["title"],
        "--body-file",
        issue_content["body_file"],
        "--project",
        GITHUB_PROJECT_NAME,
    ]
    for label in issue_content["labels"]:
        create_command_arguments += ["--label", label]

    list_existing_issue_process = subprocess.Popen(list_command_arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = list_existing_issue_process.communicate()
    existing_issues = json.loads(stdout.decode())
    already_created = len(existing_issues) > 0
    if already_created:
        logging.warning(f"An issue was already created for this definition: {existing_issues[0]}")
    if not already_created:
        if not dry_run:
            process = subprocess.Popen(create_command_arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stderr:
                logging.error(stderr.decode())
            else:
                created_issue_url = stdout.decode()
                logging.info(f"Created issue for {source_definition['name']}: {created_issue_url}")
        else:
            logging.info(f"[DRY RUN]: {' '.join(create_command_arguments)}")
    os.remove(issue_content["body_file"])


if __name__ == "__main__":
    args = parser.parse_args()
    dry_run = False if args.dry == "False" or args.dry == "false" else True
    for definition in GA_DEFINITIONS:  # TODO make configurable. GA_DEFINITIONS, ALL DEFINITIONS, read from a list, etc
        if is_airbyte_connector(definition):
            create_issue(definition, dry_run=dry_run)
        else:
            logging.error(f"Couldn't create PR for non-airbyte connector: {definition.get('dockerRepository')}")
