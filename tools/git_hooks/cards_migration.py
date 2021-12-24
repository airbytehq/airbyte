#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import os

import requests

BASIC_URL = "https://api.github.com"
AUTHORIZATION = {"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"}
SOURCE_PROJECT_ID = ...
TARGET_PROJECT_ID = ...
TEAM_ID = ...
COLUMN_FIELD_ID = ...
TEAM_FIELD_ID = ...
MAPPING = ...


def get_columns_by_project_id(project_id):
    return requests.get(f"{BASIC_URL}/projects/{project_id}/columns", headers=AUTHORIZATION).json()


def get_organization_columns_by_project_id(project_id):
    query = """
                query Columns($project_id: ID!){
                    node(id: $project_id) {
                      ... on ProjectNext {
                        fields(first: 20) {
                          nodes {
                            id
                            name
                            settings
                          }
                        }
                      }
                    }
                  }
            """
    variables = {'project_id': project_id}
    columns = requests.post(f"{BASIC_URL}/graphql", headers=AUTHORIZATION, json={'query': query, 'variables': variables})
    return json.loads(columns.json()["data"]["node"]["fields"]["nodes"][2]["settings"])["options"]


def map_columns_by_id(source_columns, target_columns):
    mapping = {}

    for source_column in source_columns:
        for target_column in target_columns:
            if MAPPING[source_column["name"]] == target_column["name"]:
                mapping[source_column["id"]] = target_column["id"]
    return mapping


def update_field_options(item_id, field_id, value):
    query = """ mutation UpdateFieldOptions($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ID!){
                        updateProjectNextItemField(
                          input: {
                            projectId: $projectId
                            itemId: $itemId
                            fieldId: $fieldId
                            value: $value
                         }
                       ) {
                         projectNextItem {
                           id
                         }
                       }
                     } """
    variables = {"projectId": TARGET_PROJECT_ID, "itemId": item_id, "fieldId": field_id, "value": value}
    requests.post(f"{BASIC_URL}/graphql", headers=AUTHORIZATION, json={'query': query, 'variables': variables})


def link_issue(issue_id, target_column_id, only_link=False):
    query = """ mutation Columns($projectId: ID!, $contentId: ID!){
                 addProjectNextItem(input: {projectId: $projectId contentId: $contentId}) {
                  projectNextItem {
                    id
                  }
                 }
                } """
    variables = {"projectId": TARGET_PROJECT_ID, "contentId": issue_id}
    add_issue = requests.post(f"{BASIC_URL}/graphql", headers=AUTHORIZATION, json={'query': query, 'variables': variables}).json()

    new_issue_id = add_issue["data"]["addProjectNextItem"]["projectNextItem"]["id"]

    if not only_link:
        if target_column_id:
            update_field_options(new_issue_id, COLUMN_FIELD_ID, target_column_id)

        update_field_options(new_issue_id, TEAM_FIELD_ID, TEAM_ID)


def get_issue_number(content_url):
    return content_url.rsplit('/', 1)[-1]


def migrate_issue_to_board(source_columns, ids_mapping):
    if OWNER_REPO == "airbytehq/airbyte":
        for source_column in source_columns:
            cards = requests.get(f"{BASIC_URL}/projects/columns/{source_column['id']}/cards", headers=AUTHORIZATION).json()

            for card in cards:
                issue_link = card["content_url"] if "content_url" in card else card["note"]
                issue_number = get_issue_number(issue_link)
                issue = requests.get(f"{BASIC_URL}/repos/{OWNER_REPO}/issues/{issue_number}", headers=AUTHORIZATION).json()

                link_issue(issue["node_id"], ids_mapping.get(source_column['id']))
    else:
        issues = requests.get(f"{BASIC_URL}/repos/{OWNER_REPO}/issues", headers=AUTHORIZATION).json()

        for issue in issues:
            link_issue(issue["node_id"], None, only_link=True)


def link_issue_to_new_board():
    source_columns = get_columns_by_project_id(SOURCE_PROJECT_ID)
    target_columns = get_organization_columns_by_project_id(TARGET_PROJECT_ID)

    ids_mapping = map_columns_by_id(source_columns, target_columns)

    migrate_issue_to_board(source_columns, ids_mapping)


if __name__ == "__main__":
    OWNER_REPOS = ["airbytehq/airbyte", "airbytehq/oncall"]
    for OWNER_REPO in OWNER_REPOS:
        link_issue_to_new_board()
