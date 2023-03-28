#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import argparse
import json
import logging
import os
import subprocess
import tempfile

import utils
from definitions import BETA_DEFINITIONS, GA_DEFINITIONS, get_airbyte_connector_name_from_definition, is_airbyte_connector
from jinja2 import Environment, FileSystemLoader

# SET THESE BEFORE USING THE SCRIPT
MODULE_NAME = "fail_on_extra_columns"
GITHUB_PROJECT_NAME = None
COMMON_ISSUE_LABELS = ["area/connectors", "team/connectors-python", "type/enhancement", "column-selection-sources"]
ISSUE_TITLE = "Add undeclared columns to spec"

# Don't need to set these
TEMPLATES_FOLDER = "./templates/"

logging.basicConfig(level=logging.DEBUG)
environment = Environment(loader=FileSystemLoader(TEMPLATES_FOLDER))

parser = argparse.ArgumentParser(description="Create issues for a list of connectors from a template.")
parser.add_argument("-d", "--dry", action=argparse.BooleanOptionalAction, default=True)
parser.add_argument("--connectors", nargs="*")
parser.add_argument("--allow_alpha", action=argparse.BooleanOptionalAction, default=False)


def get_issue_content(source_definition):
    issue_title = f"Source {source_definition['name']}: {ISSUE_TITLE}"

    template = environment.get_template(f"{MODULE_NAME}/issue.md.j2")

    test_failure_logs = ""
    with open(f"templates/{MODULE_NAME}/output/{get_airbyte_connector_name_from_definition(definition)}", "r") as f:
        for line in f:
            test_failure_logs += line

    issue_body = template.render(
        connector_name=source_definition["name"], release_stage=source_definition["releaseStage"], test_failure_logs=test_failure_logs
    )  # TODO: how to make whatever needs to be rendered configurable
    file_definition, issue_body_path = tempfile.mkstemp()

    with os.fdopen(file_definition, "w") as tmp:
        tmp.write(issue_body)

    return {"title": issue_title, "body_file": issue_body_path, "labels": COMMON_ISSUE_LABELS, "project": GITHUB_PROJECT_NAME}


def existing_issues(issue_content):
    list_command_arguments = ["gh", "issue", "list", "--state", "open", "--search", f"'{issue_content['title']}'", "--json", "url"]
    list_existing_issue_process = subprocess.Popen(list_command_arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = list_existing_issue_process.communicate()
    existing_issues = json.loads(stdout.decode())
    return existing_issues


def create_command(issue_content):
    create_command_arguments = [
        "gh",
        "issue",
        "create",
        "--title",
        issue_content["title"],
        "--body-file",
        issue_content["body_file"],
    ]
    if GITHUB_PROJECT_NAME:
        create_command_arguments += ["--project", issue_content["project"]]
    for label in issue_content["labels"]:
        create_command_arguments += ["--label", label]
    return create_command


def create_issue(source_definition, dry_run=True):
    issue_content = get_issue_content(source_definition)

    if len(existing_issues(issue_content)) > 0:
        logging.warning(f"An issue was already created for this definition: {existing_issues[0]}")
    else:
        if not dry_run:
            process = subprocess.Popen(create_command(issue_content), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stderr:
                logging.error(stderr.decode())
            else:
                created_issue_url = stdout.decode()
                logging.info(f"Created issue for {source_definition['name']}: {created_issue_url}")
        else:
            logging.info(f"[DRY RUN]: {' '.join(create_command(issue_content))}")
    os.remove(issue_content["body_file"])


if __name__ == "__main__":
    args = parser.parse_args()
    definitions = utils.get_definitions_from_args(args)

    for definition in definitions:
        if not is_airbyte_connector(definition):
            logging.error(f"Couldn't create PR for non-airbyte connector: {definition.get('dockerRepository')}")
        if not args.allow_alpha and definition not in BETA_DEFINITIONS + GA_DEFINITIONS:
            logging.info(f"Won't create an issue for non beta/GA connector {get_airbyte_connector_name_from_definition(definition)}")
        else:
            create_issue(definition, dry_run=args.dry)
