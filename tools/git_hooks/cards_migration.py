#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import os

import requests

BASIC_URL = "https://api.github.com"
AUTHORIZATION = {"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"}
OWNER_REPO = "airbytehq/airbyte"
BOARD_TYPE = "Python"


def get_columns_by_project_id(project_id):
    return requests.get(f"{BASIC_URL}/projects/{project_id}/columns", headers=AUTHORIZATION)


def get_name_mapping(board_type):
    if board_type == "Python" or board_type == "Java":
        return {
            "Done": "Done",
            "In Review (Airbyte)": "Airbyte Review",
            "In Review(internal)": "Internal Review",
            "Implementation in progress": "Implementation in progress",
            "On hold": "On hold",
            "Ready for implementation(prioritized)": "Ready for implementation",
            "Backlog (scoped)": "Ready for implementation",
            "Prioritized for scoping": "Ready for implementation",
            "Backlog (unscoped)": "Need scoping",
            "Backlog": "Need scoping"
        }
    elif board_type == "Java":
        return {
            "Done": "Done",
            "In Review (Airbyte)": "Airbyte Review",
            "In Review(internal)": "Internal Review",
            "Implementation in progress": "Implementation in progress",
            "On hold": "On hold",
            "Ready for implementation (prioritized)": "Ready for implementation",
            "Backlog (scoped)": "Ready for implementation",
            "Prioritized for scoping": "Ready for implementation",
            "Backlog (unscoped)": "Need scoping",
            "Backlog": "Need scoping"
        }


def map_columns(source_columns, target_columns):
    # python_mapping = {"First": "First", "Second": "Second"}
    name_mapping = get_name_mapping(BOARD_TYPE)
    mapping = {}
    for source_column in source_columns:
        for target_column in target_columns:
            if name_mapping[source_column["name"]] == target_column["name"]:
                mapping[source_column["id"]] = target_column["id"]

    return mapping


def create_card_to_issue(issue_id, id_mapping, source_column_id, card_note):
    data = {"content_id": int(issue_id), "content_type": "Issue", "note": card_note}
    requests.post(f"{BASIC_URL}/projects/columns/{id_mapping[source_column_id]}/cards", headers=AUTHORIZATION,
                  data=json.dumps(data))


def get_issue_number(content_url):
    return content_url.rsplit('/', 1)[-1]


def migrate_bard_to_board(source_columns, id_mapping):
    for source_column in source_columns:
        cards = requests.get(f"{BASIC_URL}/projects/columns/{source_column['id']}/cards", headers=AUTHORIZATION).json()

        for card in cards:
            issue_number = get_issue_number(card['content_url'])
            issue = requests.get(f"{BASIC_URL}/repos/{OWNER_REPO}/issues/{issue_number}", headers=AUTHORIZATION).json()

            create_card_to_issue(issue["id"], id_mapping, source_column['id'], card["note"])


def link_issue_to_new_card(source_project_id, target_project_id):
    source_columns = get_columns_by_project_id(source_project_id).json()
    target_columns = get_columns_by_project_id(target_project_id).json()

    id_mapping = map_columns(source_columns, target_columns)

    migrate_bard_to_board(source_columns, id_mapping)


if __name__ == "__main__":
    orgs = requests.get(f"{BASIC_URL}/orgs/airbytehq/projects", headers=AUTHORIZATION).json()
    print(orgs)
    repos = requests.get(f"{BASIC_URL}/repos/airbytehq/airbyte/projects", headers=AUTHORIZATION).json()
    print(repos)
