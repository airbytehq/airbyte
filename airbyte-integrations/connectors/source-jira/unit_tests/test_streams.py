#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import responses
from conftest import _YAML_FILE_PATH, find_stream, read_full_refresh

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


@responses.activate
def test_application_roles_stream_401_error(config, caplog):
    config["domain"] = "test_application_domain"
    responses.add(responses.GET, f"https://{config['domain']}/rest/api/3/applicationrole", status=401)

    stream = find_stream("application_roles", config)

    with pytest.raises(
        AirbyteTracedException,
        match="Unauthorized. Please ensure you are authenticated correctly.",
    ):
        list(read_full_refresh(stream))


@responses.activate
def test_application_roles_stream(config, application_roles_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/applicationrole",
        json=application_roles_response,
    )

    stream = find_stream("application_roles", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_application_roles_stream_http_error(config, application_roles_response):
    responses.add(responses.GET, f"https://{config['domain']}/rest/api/3/applicationrole", json={"error": "not found"}, status=404)

    stream = find_stream("application_roles", config)
    with pytest.raises(AirbyteTracedException, match="Not found. The requested resource was not found on the server"):
        list(read_full_refresh(stream))


@responses.activate
def test_boards_stream(config, boards_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board?maxResults=50",
        json=boards_response,
    )

    stream = find_stream("boards", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_board_stream_forbidden(config, boards_response, caplog):
    config["domain"] = "test_boards_domain"
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board?maxResults=50",
        json={"error": f"403 Client Error: Forbidden for url: https://{config['domain']}/rest/agile/1.0/board?maxResults=50"},
        status=403,
    )
    stream = find_stream("boards", config)

    with pytest.raises(AirbyteTracedException, match="Forbidden. You don't have permission to access this resource."):
        list(read_full_refresh(stream))


@responses.activate
def test_dashboards_stream(config, dashboards_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/dashboard",
        json=dashboards_response,
    )

    stream = find_stream("dashboards", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_filters_stream(config, mock_filter_response):
    stream = find_stream("filters", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_groups_stream(config, groups_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/group/bulk?maxResults=50",
        json=groups_response,
    )

    stream = find_stream("groups", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 4
    assert len(responses.calls) == 1


@responses.activate
def test_issues_fields_stream(config, mock_fields_response):
    stream = find_stream("issue_fields", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 6
    assert len(responses.calls) == 1


@responses.activate
def test_issues_field_configurations_stream(config, issues_field_configurations_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/fieldconfiguration?maxResults=50",
        json=issues_field_configurations_response,
    )

    stream = find_stream("issue_field_configurations", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_issues_link_types_stream(config, issues_link_types_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issueLinkType",
        json=issues_link_types_response,
    )

    stream = find_stream("issue_link_types", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_issues_navigator_settings_stream(config, issues_navigator_settings_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/settings/columns",
        json=issues_navigator_settings_response,
    )

    stream = find_stream("issue_navigator_settings", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_issue_notification_schemas_stream(config, issue_notification_schemas_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/notificationscheme?maxResults=50",
        json=issue_notification_schemas_response,
    )

    stream = find_stream("issue_notification_schemes", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_issue_properties_stream(config, issue_properties_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/priority/search?maxResults=50",
        json=issue_properties_response,
    )

    stream = find_stream("issue_priorities", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_issue_resolutions_stream(config, issue_resolutions_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/resolution/search?maxResults=50",
        json=issue_resolutions_response,
    )

    stream = find_stream("issue_resolutions", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_issue_security_schemes_stream(config, issue_security_schemes_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issuesecurityschemes",
        json=issue_security_schemes_response,
    )

    stream = find_stream("issue_security_schemes", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_issue_type_schemes_stream(config, issue_type_schemes_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issuetypescheme?maxResults=50",
        json=issue_type_schemes_response,
    )

    stream = find_stream("issue_type_schemes", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_jira_settings_stream(config, jira_settings_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/application-properties",
        json=jira_settings_response,
    )

    stream = find_stream("jira_settings", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_board_issues_stream(config, mock_board_response, board_issues_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/1/issue?maxResults=50&fields=key&fields=created&fields=updated&jql=updated+%3E%3D+1609459200000",
        json=board_issues_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/2/issue?maxResults=50&fields=key&fields=created&fields=updated&jql=updated+%3E%3D+1609459200000",
        json={"errorMessages": ["This board has no columns with a mapped status."], "errors": {}},
        status=500,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/3/issue?maxResults=50&fields=key&fields=created&fields=updated&jql=updated+%3E%3D+1609459200000",
        json={},
    )

    stream = find_stream("board_issues", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 1
    assert len(responses.calls) == 4


@responses.activate
def test_filter_sharing_stream(config, mock_filter_response, filter_sharing_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/filter/1/permission",
        json=filter_sharing_response,
    )

    stream = find_stream("filter_sharing", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 1
    assert len(responses.calls) == 2


@responses.activate
def test_projects_stream(config, mock_projects_responses):
    stream = find_stream("projects", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_projects_avatars_stream(config, mock_non_deleted_projects_responses, projects_avatars_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/1/avatars",
        json=projects_avatars_response,
    )

    stream = find_stream("project_avatars", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 2


@responses.activate
def test_projects_categories_stream(config, projects_categories_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/projectCategory",
        json=projects_categories_response,
    )

    stream = find_stream("project_categories", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_screens_stream(config, mock_screen_response):
    stream = find_stream("screens", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_screen_tabs_stream(config, mock_screen_response, screen_tabs_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/screens/1/tabs",
        json=screen_tabs_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/screens/2/tabs",
        json={},
    )

    stream = find_stream("screen_tabs", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 3


@responses.activate
def test_sprints_stream(config, mock_board_response, mock_sprints_response):
    output = read(
        YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(_YAML_FILE_PATH)),
        config,
        CatalogBuilder().with_stream("sprints", SyncMode.full_refresh).build(),
    )

    assert len(output.records) == 3
    assert len(responses.calls) == 4


@responses.activate
def test_board_does_not_support_sprints(config, mock_board_response, sprints_response, caplog):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/1/sprint?maxResults=50",
        json=sprints_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/2/sprint?maxResults=50",
        json={"errorMessages": ["The board does not support sprints"], "errors": {}},
        status=400,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/3/sprint?maxResults=50",
        json=sprints_response,
    )
    stream = find_stream("sprints", config)
    records = list(read_full_refresh(stream))
    assert len(records) == 2

    assert (
        "The board does not support sprints. The board does not have a sprint board. if it's a team-managed one, "
        "does it have sprints enabled under project settings? If it's a company-managed one,"
        " check that it has at least one Scrum board associated with it."
    ) in caplog.text


@responses.activate
def test_sprint_issues_stream(config, mock_board_response, mock_fields_response, mock_sprints_response, sprints_issues_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/sprint/2/issue?maxResults=50&fields=key&fields=status&fields=created&fields=updated&jql=updated+%3E%3D+1609459200000",
        json=sprints_issues_response,
    )

    output = read(
        YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(_YAML_FILE_PATH)),
        config,
        CatalogBuilder().with_stream("sprint_issues", SyncMode.full_refresh).build(),
    )

    assert len(output.records) == 3
    assert len(responses.calls) == 8


@responses.activate
def test_time_tracking_stream(config, time_tracking_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/configuration/timetracking/list",
        json=time_tracking_response,
    )

    stream = find_stream("time_tracking", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_users_stream(config, mock_users_response):
    stream = find_stream("users", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_users_groups_detailed_stream(config, mock_users_response, users_groups_detailed_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/user?accountId=1&expand=groups%2CapplicationRoles",
        json=users_groups_detailed_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/user?accountId=2&expand=groups%2CapplicationRoles",
        json=users_groups_detailed_response,
    )

    stream = find_stream("users_groups_detailed", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 4
    assert len(responses.calls) == 3


@responses.activate
def test_workflows_stream(config, workflows_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/workflow/search?maxResults=50",
        json=workflows_response,
    )

    stream = find_stream("workflows", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_workflow_schemas_stream(config, workflow_schemas_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/workflowscheme?maxResults=50",
        json=workflow_schemas_response,
    )

    stream = find_stream("workflow_schemes", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_workflow_statuses_stream(config, workflow_statuses_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/status",
        json=workflow_statuses_response,
    )

    stream = find_stream("workflow_statuses", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_workflow_status_categories_stream(config, workflow_status_categories_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/statuscategory",
        json=workflow_status_categories_response,
    )

    stream = find_stream("workflow_status_categories", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_avatars_stream(config, avatars_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/avatar/issuetype/system",
        json=avatars_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/avatar/project/system",
        json={},
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/avatar/user/system",
        json={},
    )

    stream = find_stream("avatars", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 3


@responses.activate
def test_avatars_stream_should_retry(config, caplog):
    for slice in ["issuetype", "project", "user"]:
        responses.add(
            responses.GET,
            f"https://{config['domain']}/rest/api/3/avatar/{slice}/system",
            json={"errorMessages": ["The error message"], "errors": {}},
            status=400,
        )

    stream = find_stream("avatars", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 0
    assert "Bad request. Please check your request parameters" in caplog.text


@responses.activate
def test_declarative_issues_stream(config, mock_projects_responses_additional_project, mock_issues_responses_with_date_filter, caplog):
    stream = find_stream("issues", {**config, "projects": config["projects"] + ["Project3"]})
    records = list(read_full_refresh(stream))
    assert len(records) == 1

    # check if only None values was filtered out from 'fields' field
    assert "empty_field" not in records[0]["fields"]
    assert "non_empty_field" in records[0]["fields"]

    assert len(responses.calls) == 3
    assert "The user doesn't have permission to the project. Please grant the user to the project." in caplog.messages


@responses.activate
def test_python_issue_comments_stream(config, mock_projects_responses, mock_issues_responses_with_date_filter, issue_comments_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/10627/comment?maxResults=50",
        json=issue_comments_response,
    )

    stream = find_stream("issue_comments", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 3


@responses.activate
def test_issue_custom_field_contexts_stream(config, mock_fields_response, mock_issue_custom_field_contexts_response):
    stream = find_stream("issue_custom_field_contexts", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 4


@responses.activate
def test_project_permissions_stream(config, mock_non_deleted_projects_responses, project_permissions_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/Project1/securitylevel",
        json=project_permissions_response,
    )

    stream = find_stream("project_permission_schemes", config)
    records = list(read_full_refresh(stream))
    expected_records = [
        {
            "description": "Only the reporter and internal staff can see this issue.",
            "id": "100000",
            "name": "Reporter Only",
            "projectId": "Project1",
            "self": "https://your-domain.atlassian.net/rest/api/3/securitylevel/100000",
        },
        {
            "description": "Only internal staff can see this issue.",
            "id": "100001",
            "name": "Staff Only",
            "projectId": "Project1",
            "self": "https://your-domain.atlassian.net/rest/api/3/securitylevel/100001",
        },
    ]
    assert len(records) == 2
    for rec, exp in zip(records, expected_records):
        assert dict(rec) == exp, f"Failed at {rec} vs {exp}"


@responses.activate
def test_project_email_stream(config, mock_non_deleted_projects_responses, mock_project_emails):
    output = read(
        YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(_YAML_FILE_PATH)),
        config,
        CatalogBuilder().with_stream("project_email", SyncMode.full_refresh).build(),
    )

    assert len(output.records) == 2
    assert len(responses.calls) == 2


@responses.activate
def test_project_components_stream(config, mock_non_deleted_projects_responses, project_components_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/Project1/component?maxResults=50",
        json=project_components_response,
    )

    output = read(
        YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(_YAML_FILE_PATH)),
        config,
        CatalogBuilder().with_stream("project_components", SyncMode.full_refresh).build(),
    )

    assert len(output.records) == 2
    assert len(responses.calls) == 2


@responses.activate
def test_permissions_stream(config, permissions_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/permissions",
        json=permissions_response,
    )

    output = read(
        YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(_YAML_FILE_PATH)),
        config,
        CatalogBuilder().with_stream("permissions", SyncMode.full_refresh).build(),
    )

    assert len(output.records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_labels_stream(config, labels_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/label?maxResults=50",
        json=labels_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/label?maxResults=50&startAt=2",
        json={},
    )

    output = read(
        YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(_YAML_FILE_PATH)),
        config,
        CatalogBuilder().with_stream("labels", SyncMode.full_refresh).build(),
    )

    assert len(output.records) == 2
    assert len(responses.calls) == 2


@responses.activate
def test_issue_worklogs_stream(config, mock_projects_responses, mock_issues_responses_with_date_filter, issue_worklogs_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/10627/worklog?maxResults=50",
        json=issue_worklogs_response,
    )

    stream = find_stream("issue_worklogs", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 1
    assert len(responses.calls) == 3


@responses.activate
def test_issue_watchers_stream(config, mock_projects_responses, mock_issues_responses_with_date_filter, issue_votes_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/watchers",
        json=issue_votes_response,
    )

    stream = find_stream("issue_watchers", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 1
    assert len(responses.calls) == 3


@responses.activate
def test_issue_votes_stream_slice(config, mock_projects_responses, mock_issues_responses_with_date_filter, issue_votes_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/votes",
        json=issue_votes_response,
    )

    stream = find_stream("issue_votes", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 1
    assert len(responses.calls) == 3


@responses.activate
def test_issue_remote_links_stream_(config, mock_projects_responses, mock_issues_responses_with_date_filter, issue_remote_links_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/remotelink",
        json=issue_remote_links_response,
    )

    stream = find_stream("issue_remote_links", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 3


@responses.activate
def test_project_versions_stream(config, mock_non_deleted_projects_responses, projects_versions_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/Project1/version?maxResults=50",
        json=projects_versions_response,
    )

    stream = find_stream("project_versions", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 2


@pytest.mark.parametrize(
    "stream, expected_records_number, expected_calls_number, log_message",
    [
        ("issues", 2, 4, "The user doesn't have permission to the project. Please grant the user to the project."),
        (
            "issue_custom_field_contexts",
            2,
            4,
            "Not found. The requested resource was not found on the server.",
            # "Stream `issue_custom_field_contexts`. An error occurred, details: ['Not found issue custom field context for issue fields issuetype2']. Skipping for now. ",
        ),
        (
            "issue_custom_field_options",
            1,
            6,
            "Not found. The requested resource was not found on the server.",
            # "Stream `issue_custom_field_options`. An error occurred, details: ['Not found issue custom field options for issue fields issuetype3']. Skipping for now. ",
        ),
        (
            "issue_watchers",
            1,
            6,
            "Not found. The requested resource was not found on the server.",
            # "Stream `issue_watchers`. An error occurred, details: ['Not found watchers for issue TESTKEY13-2']. Skipping for now. ",
        ),
        (
            "project_email",
            4,
            4,
            "Forbidden. You don't have permission to access this resource.",
            # "Stream `project_email`. An error occurred, details: ['No access to emails for project 3']. Skipping for now. ",
        ),
    ],
)
@responses.activate
def test_skip_slice(
    config,
    mock_projects_responses_additional_project,
    mock_non_deleted_projects_responses,
    mock_issues_responses_with_date_filter,
    mock_project_emails,
    mock_issue_watchers_responses,
    mock_issue_custom_field_contexts_response_error,
    mock_issue_custom_field_options_response,
    mock_fields_response,
    caplog,
    stream,
    expected_records_number,
    expected_calls_number,
    log_message,
):
    config["projects"] = config.get("projects", []) + ["Project3", "Project4"]
    output = read(
        YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(_YAML_FILE_PATH)),
        config,
        CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build(),
    )
    assert len(output.records) == expected_records_number

    assert len(responses.calls) == expected_calls_number
    assert log_message in caplog.messages
