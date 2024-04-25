#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
from pathlib import Path

import responses
from pytest import fixture
from responses import matchers
from source_jira.source import SourceJira

ENV_REQUEST_CACHE_PATH = "REQUEST_CACHE_PATH"
os.environ["REQUEST_CACHE_PATH"] = ENV_REQUEST_CACHE_PATH


def delete_cache_files(cache_directory):
    directory_path = Path(cache_directory)
    if directory_path.exists() and directory_path.is_dir():
        for file_path in directory_path.glob("*.sqlite"):
            file_path.unlink()


@fixture(autouse=True)
def clear_cache_before_each_test():
    # The problem: Once the first request is cached, we will keep getting the cached result no matter what setup we prepared for a particular test.
    # Solution: We must delete the cache before each test because for the same URL, we want to define multiple responses and status codes.
    delete_cache_files(os.getenv(ENV_REQUEST_CACHE_PATH))
    yield


@fixture
def config():
    return {
        "api_token": "token",
        "domain": "domain",
        "email": "email@email.com",
        "start_date": "2021-01-01T00:00:00Z",
        "projects": ["Project1"],
    }


def load_file(fn):
    return open(os.path.join(os.path.dirname(__file__), "responses", fn)).read()


@fixture
def application_roles_response():
    return json.loads(load_file("application_role.json"))


@fixture
def boards_response():
    return json.loads(load_file("board.json"))


@fixture
def dashboards_response():
    return json.loads(load_file("dashboard.json"))


@fixture
def filters_response():
    return json.loads(load_file("filter.json"))


@fixture
def groups_response():
    return json.loads(load_file("groups.json"))


@fixture
def issue_fields_response():
    return json.loads(load_file("issue_fields.json"))


@fixture
def issues_field_configurations_response():
    return json.loads(load_file("issues_field_configurations.json"))


@fixture
def issues_link_types_response():
    return json.loads(load_file("issues_link_types.json"))


@fixture
def issues_navigator_settings_response():
    return json.loads(load_file("issues_navigator_settings.json"))


@fixture
def issue_notification_schemas_response():
    return json.loads(load_file("issue_notification_schemas.json"))


@fixture
def issue_properties_response():
    return json.loads(load_file("issue_properties.json"))


@fixture
def issue_resolutions_response():
    return json.loads(load_file("issue_resolutions.json"))


@fixture
def issue_security_schemes_response():
    return json.loads(load_file("issue_security_schemes.json"))


@fixture
def issue_type_schemes_response():
    return json.loads(load_file("issue_type.json"))


@fixture
def jira_settings_response():
    return json.loads(load_file("jira_settings.json"))


@fixture
def board_issues_response():
    return json.loads(load_file("board_issues.json"))


@fixture
def filter_sharing_response():
    return json.loads(load_file("filter_sharing.json"))


@fixture
def projects_response():
    return json.loads(load_file("projects.json"))


@fixture
def projects_avatars_response():
    return json.loads(load_file("projects_avatars.json"))


@fixture
def projects_categories_response():
    return json.loads(load_file("projects_categories.json"))


@fixture
def screens_response():
    return json.loads(load_file("screens.json"))


@fixture
def screen_tabs_response():
    return json.loads(load_file("screen_tabs.json"))


@fixture
def screen_tab_fields_response():
    return json.loads(load_file("screen_tab_fields.json"))


@fixture
def sprints_response():
    return json.loads(load_file("sprints.json"))


@fixture
def sprints_issues_response():
    return json.loads(load_file("sprint_issues.json"))


@fixture
def time_tracking_response():
    return json.loads(load_file("time_tracking.json"))


@fixture
def users_response():
    return json.loads(load_file("users.json"))


@fixture
def users_groups_detailed_response():
    return json.loads(load_file("users_groups_detailed.json"))


@fixture
def workflows_response():
    return json.loads(load_file("workflows.json"))


@fixture
def workflow_schemas_response():
    return json.loads(load_file("workflow_schemas.json"))


@fixture
def workflow_statuses_response():
    return json.loads(load_file("workflow_statuses.json"))


@fixture
def workflow_status_categories_response():
    return json.loads(load_file("workflow_status_categories.json"))


@fixture
def avatars_response():
    return json.loads(load_file("avatars.json"))


@fixture
def issues_response():
    return json.loads(load_file("issues.json"))


@fixture
def issue_comments_response():
    return json.loads(load_file("issue_comments.json"))


@fixture
def issue_custom_field_contexts_response():
    return json.loads(load_file("issue_custom_field_contexts.json"))


@fixture
def issue_custom_field_options_response():
    return json.loads(load_file("issue_custom_field_options.json"))


@fixture
def issue_property_keys_response():
    return json.loads(load_file("issue_property_keys.json"))


@fixture
def project_permissions_response():
    return json.loads(load_file("project_permissions.json"))


@fixture
def project_email_response():
    return json.loads(load_file("project_email.json"))


@fixture
def project_components_response():
    return json.loads(load_file("project_components.json"))


@fixture
def permissions_response():
    return json.loads(load_file("permissions.json"))


@fixture
def labels_response():
    return json.loads(load_file("labels.json"))


@fixture
def issue_worklogs_response():
    return json.loads(load_file("issue_worklogs.json"))


@fixture
def issue_watchers_response():
    return json.loads(load_file("issue_watchers.json"))


@fixture
def issue_votes_response():
    return json.loads(load_file("issue_votes.json"))


@fixture
def issue_remote_links_response():
    return json.loads(load_file("issue_remote_links.json"))


@fixture
def projects_versions_response():
    return json.loads(load_file("projects_versions.json"))


@fixture
def mock_projects_responses(config, projects_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/search?maxResults=50&expand=description%2Clead&status=live&status=archived&status=deleted",
        json=projects_response,
    )


@fixture
def mock_projects_responses_additional_project(config, projects_response):
    projects_response["values"] += [{"id": "3", "key": "Project3"}, {"id": "4", "key": "Project4"}]
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/search?maxResults=50&expand=description%2Clead&status=live&status=archived&status=deleted",
        json=projects_response,
    )


@fixture
def mock_issues_responses_with_date_filter(config, issues_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/search",
        match=[
            matchers.query_param_matcher(
                {
                    "maxResults": 50,
                    "fields": "*all",
                    "jql": "updated >= '2021/01/01 00:00' and project in (1) ORDER BY updated asc",
                    "expand": "renderedFields,transitions,changelog",
                }
            )
        ],
        json=issues_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/search",
        match=[
            matchers.query_param_matcher(
                {
                    "maxResults": 50,
                    "fields": "*all",
                    "jql": "updated >= '2021/01/01 00:00' and project in (2) ORDER BY updated asc",
                    "expand": "renderedFields,transitions,changelog",
                }
            )
        ],
        json={},
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/search",
        match=[
            matchers.query_param_matcher(
                {
                    "maxResults": 50,
                    "fields": "*all",
                    "jql": "updated >= '2021/01/01 00:00' and project in (3) ORDER BY updated asc",
                    "expand": "renderedFields,transitions,changelog",
                }
            )
        ],
        json={"errorMessages": ["The value '3' does not exist for the field 'project'."]},
        status=400,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/search",
        match=[
            matchers.query_param_matcher(
                {
                    "maxResults": 50,
                    "fields": "*all",
                    "jql": "updated >= '2021/01/01 00:00' and project in (4) ORDER BY updated asc",
                    "expand": "renderedFields,transitions,changelog",
                }
            )
        ],
        json={
            "issues": [
                {
                    "key": "TESTKEY13-2",
                    "fields": {
                        "project": {
                            "id": "10016",
                            "key": "TESTKEY13",
                        },
                        "created": "2022-06-09T16:29:31.871-0700",
                        "updated": "2022-12-08T02:22:18.889-0800",
                    },
                }
            ]
        },
    )


@fixture
def mock_project_emails(config, project_email_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/1/email",
        json=project_email_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/2/email",
        json=project_email_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/3/email",
        json={"errorMessages": ["No access to emails for project 3"]},
        status=403,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/4/email",
        json=project_email_response,
    )


@fixture
def mock_issue_watchers_responses(config, issue_watchers_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/watchers",
        json=issue_watchers_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-2/watchers",
        json={"errorMessages": ["Not found watchers for issue TESTKEY13-2"]},
        status=404,
    )


@fixture
def mock_issue_custom_field_contexts_response(config, issue_custom_field_contexts_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/field/issuetype/context?maxResults=50",
        json=issue_custom_field_contexts_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/field/issuetype2/context?maxResults=50",
        json={},
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/field/issuetype3/context?maxResults=50",
        json={},
    )


@fixture
def mock_issue_custom_field_contexts_response_error(config, issue_custom_field_contexts_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/field/issuetype/context?maxResults=50",
        json=issue_custom_field_contexts_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/field/issuetype2/context?maxResults=50",
        json={"errorMessages": ["Not found issue custom field context for issue fields issuetype2"]},
        status=404,
    )
    responses.add(responses.GET, f"https://{config['domain']}/rest/api/3/field/issuetype3/context?maxResults=50", json={})


@fixture
def mock_issue_custom_field_options_response(config, issue_custom_field_options_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/field/issuetype/context/10130/option?maxResults=50",
        json=issue_custom_field_options_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/field/issuetype/context/10129/option?maxResults=50",
        json={"errorMessages": ["Not found issue custom field options for issue fields issuetype3"]},
        status=404,
    )


@fixture
def mock_fields_response(config, issue_fields_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/field",
        json=issue_fields_response,
    )


@fixture
def mock_users_response(config, users_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/users/search?maxResults=50",
        json=users_response,
    )


@fixture
def mock_board_response(config, boards_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board?maxResults=50",
        json=boards_response,
    )


@fixture
def mock_screen_response(config, screens_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/screens?maxResults=50",
        json=screens_response,
    )


@fixture
def mock_filter_response(config, filters_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/filter/search?maxResults=50&expand=description%2Cowner%2Cjql%2CviewUrl%2CsearchUrl%2Cfavourite%2CfavouritedCount%2CsharePermissions%2CisWritable%2Csubscriptions",
        json=filters_response,
    )


@fixture
def mock_sprints_response(config, sprints_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/1/sprint?maxResults=50",
        json=sprints_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/2/sprint?maxResults=50",
        json=sprints_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/3/sprint?maxResults=50",
        json=sprints_response,
    )


def find_stream(stream_name, config):
    for stream in SourceJira().streams(config=config):
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")
