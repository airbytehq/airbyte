#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os

import responses
from pytest import fixture
from responses import matchers
from source_jira.streams import Projects


@fixture
def config():
    return {
        "api_token": "token",
        "domain": "domain",
        "email": "email@email.com",
        "start_date": "2021-01-01T00:00:00Z",
        "projects": ["Project1"]
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
    Projects.use_cache = False
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/search?maxResults=50&expand=description%2Clead",
        json=projects_response,
    )


@fixture
def mock_issues_responses(config, issues_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/search",
        match=[matchers.query_param_matcher({"maxResults": 50, "fields": '*all', "jql": "project in (1)"})],
        json=issues_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/search",
        match=[matchers.query_param_matcher({"maxResults": 50, "fields": '*all', "jql": "project in (2)"})],
        json={},
    )
