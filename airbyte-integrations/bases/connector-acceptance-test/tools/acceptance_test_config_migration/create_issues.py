#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import argparse
import json
import logging
import os
import subprocess
import tempfile
from typing import Any, Dict, Optional, Text

import definitions
import utils
from jinja2 import Environment, FileSystemLoader

# Update this line before running the script
from migrations.strictness_level_migration import config

logging.basicConfig(level=logging.DEBUG)
environment = Environment(loader=FileSystemLoader(utils.MIGRATIONS_FOLDER))

parser = argparse.ArgumentParser(description="Create issues for a list of connectors from a template.")
utils.add_dry_param(parser)
utils.add_connectors_param(parser)
utils.add_allow_beta_param(parser)
utils.add_allow_alpha_param(parser)


def get_test_failure_logs(definition):
    test_failure_logs = ""
    if config.MODULE_NAME == "fail_on_extra_columns":
        connector_technical_name = definitions.get_airbyte_connector_name_from_definition(definition)

        try:
            with open(f"{utils.MIGRATIONS_FOLDER}/{config.MODULE_NAME}/test_failure_logs/{connector_technical_name}", "r") as f:
                for line in f:
                    test_failure_logs += line
        except FileNotFoundError:
            logging.warning(f"Skipping creating an issue for {definition['name']} -- could not find an output file for it.")
            return

    return test_failure_logs


def get_issue_content(source_definition) -> Optional[Dict[Text, Any]]:
    issue_title = f"Source {source_definition['name']}: {config.ISSUE_TITLE}"

    template = environment.get_template(f"{config.MODULE_NAME}/issue.md.j2")

    # TODO: Make list of variables to render, and how to render them, configurable
    issue_body = template.render(
        connector_name=source_definition["name"],
        release_stage=source_definition["releaseStage"],
        test_failure_logs=get_test_failure_logs(source_definition),
    )
    file_definition, issue_body_path = tempfile.mkstemp()

    with os.fdopen(file_definition, "w") as tmp:
        tmp.write(issue_body)

    return {"title": issue_title, "body_file": issue_body_path, "labels": config.COMMON_ISSUE_LABELS, "project": config.GITHUB_PROJECT_NAME}


def get_existing_issues(issue_content):
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
    if config.GITHUB_PROJECT_NAME:
        create_command_arguments += ["--project", issue_content["project"]]
    for label in issue_content["labels"]:
        create_command_arguments += ["--label", label]
    return create_command_arguments


def create_issue(source_definition, dry_run=True):
    issue_content = get_issue_content(source_definition)
    if not issue_content:
        return

    existing_issues = get_existing_issues(issue_content)
    if existing_issues:
        logging.warning(f"An issue was already created for {source_definition['name']}: {existing_issues[0]}")
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
    for definition in utils.get_valid_definitions_from_args(args):
        create_issue(definition, dry_run=args.dry)
