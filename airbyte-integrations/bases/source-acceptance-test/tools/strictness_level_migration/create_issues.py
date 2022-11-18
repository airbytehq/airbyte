#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import argparse
import json
import logging
import os
import subprocess
import tempfile

from definitions import GA_DEFINITIONS
from jinja2 import Environment, FileSystemLoader

TEMPLATES_FOLDER = "./templates/"
COMMON_ISSUE_LABELS = ["area/connectors", "team/connectors-python", "type/enhancement", "test-strictness-level"]
GITHUB_PROJECT_NAME = "SAT-high-test-strictness-level"

logging.basicConfig(level=logging.DEBUG)
environment = Environment(loader=FileSystemLoader(TEMPLATES_FOLDER))

parser = argparse.ArgumentParser(description="Create issues for migration of GA connectors to high test strictness level in SAT")
parser.add_argument("-d", "--dry", default=True)


def get_issue_content(source_definition):
    issue_title = f"Source {source_definition['name']}: enable `high` test strictness level in SAT"

    template = environment.get_template("issue.md.j2")
    issue_body = template.render(connector_name=source_definition["name"], release_stage=source_definition["releaseStage"])
    file_definition, issue_body_path = tempfile.mkstemp()

    with os.fdopen(file_definition, "w") as tmp:
        # do stuff with temp file
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
    for definition in GA_DEFINITIONS:
        create_issue(definition, dry_run=dry_run)
