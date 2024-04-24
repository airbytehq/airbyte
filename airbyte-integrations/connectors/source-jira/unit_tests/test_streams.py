#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import re

import pendulum
import pytest
import requests
import responses
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.exceptions import ReadException
from conftest import find_stream
from requests.exceptions import HTTPError
from responses import matchers
from source_jira.source import SourceJira
from source_jira.streams import IssueComments, IssueFields, Issues, IssueWorklogs, Projects
from source_jira.utils import read_full_refresh


@responses.activate
def test_application_roles_stream_401_error(config, caplog):
    config["domain"] = "test_application_domain"
    responses.add(responses.GET, f"https://{config['domain']}/rest/api/3/applicationrole", status=401)

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("application_roles", config)

    with pytest.raises(
        ReadException,
        match="Request to https://test_application_domain/rest/api/3/applicationrole failed with status code 401 and error message None",
    ):
        [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]


@responses.activate
def test_application_roles_stream(config, application_roles_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/applicationrole",
        json=application_roles_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("application_roles", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_application_roles_stream_http_error(config, application_roles_response):
    responses.add(responses.GET, f"https://{config['domain']}/rest/api/3/applicationrole", json={"error": "not found"}, status=404)

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("application_roles", config)
    with pytest.raises(
        ReadException, match="Request to https://domain/rest/api/3/applicationrole failed with status code 404 and error message not found"
    ):
        [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]


@responses.activate
def test_boards_stream(config, boards_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board?maxResults=50",
        json=boards_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("boards", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    # assert len(responses.calls) == 1 # - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


@responses.activate
def test_board_stream_forbidden(config, boards_response, caplog):
    config["domain"] = "test_boards_domain"
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board?maxResults=50",
        json={"error": f"403 Client Error: Forbidden for url: https://{config['domain']}/rest/agile/1.0/board?maxResults=50"},
        status=403,
    )
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("boards", config)

    expected_url = "https://test_boards_domain/rest/agile/1.0/board?maxResults=50"
    escaped_url = re.escape(expected_url)

    with pytest.raises(
        ReadException,
        match=(
            f"Request to {escaped_url} failed with status code 403 and error message 403 Client Error: " f"Forbidden for url: {escaped_url}"
        ),
    ):
        [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]


@responses.activate
def test_dashboards_stream(config, dashboards_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/dashboard",
        json=dashboards_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("dashboards", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    # assert len(responses.calls) == 1 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


@responses.activate
def test_filters_stream(config, mock_filter_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("filters", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 1
    # assert len(responses.calls) == 1 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


@responses.activate
def test_groups_stream(config, groups_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/group/bulk?maxResults=50",
        json=groups_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("groups", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 4
    assert len(responses.calls) == 1


@responses.activate
def test_issues_fields_stream(config, mock_fields_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssueFields(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 5
    assert len(responses.calls) == 1


@responses.activate
def test_issues_field_configurations_stream(config, issues_field_configurations_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/fieldconfiguration?maxResults=50",
        json=issues_field_configurations_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_field_configurations", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_issues_link_types_stream(config, issues_link_types_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issueLinkType",
        json=issues_link_types_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_link_types", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_issues_navigator_settings_stream(config, issues_navigator_settings_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/settings/columns",
        json=issues_navigator_settings_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_navigator_settings", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_issue_notification_schemas_stream(config, issue_notification_schemas_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/notificationscheme?maxResults=50",
        json=issue_notification_schemas_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_notification_schemes", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_issue_properties_stream(config, issue_properties_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/priority/search?maxResults=50",
        json=issue_properties_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_priorities", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_issue_resolutions_stream(config, issue_resolutions_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/resolution/search?maxResults=50",
        json=issue_resolutions_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_resolutions", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_issue_security_schemes_stream(config, issue_security_schemes_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issuesecurityschemes",
        json=issue_security_schemes_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_security_schemes", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_issue_type_schemes_stream(config, issue_type_schemes_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issuetypescheme?maxResults=50",
        json=issue_type_schemes_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_type_schemes", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_jira_settings_stream(config, jira_settings_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/application-properties",
        json=jira_settings_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("jira_settings", config)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_board_issues_stream(config, mock_board_response, board_issues_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/1/issue?maxResults=50&fields=key&fields=created&fields=updated&jql=updated+%3E%3D+%272021%2F01%2F01+00%3A00%27",
        json=board_issues_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/2/issue?maxResults=50&fields=key&fields=created&fields=updated&jql=updated+%3E%3D+%272021%2F01%2F01+00%3A00%27",
        json={"errorMessages": ["This board has no columns with a mapped status."], "errors": {}},
        status=500,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/3/issue?maxResults=50&fields=key&fields=created&fields=updated&jql=updated+%3E%3D+%272021%2F01%2F01+00%3A00%27",
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
    records = [
        r
        for s in stream.stream_slices(sync_mode=SyncMode.incremental)
        for r in stream.read_records(sync_mode=SyncMode.incremental, stream_slice=s)
    ]
    assert len(records) == 1
    # assert len(responses.calls) == 2 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


@responses.activate
def test_projects_stream(config, mock_projects_responses):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Projects(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 1


@responses.activate
def test_projects_avatars_stream(config, mock_projects_responses, projects_avatars_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/1/avatars",
        json=projects_avatars_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("project_avatars", config)
    records = list(read_full_refresh(stream))
    assert len(records) == 2
    # assert len(responses.calls) == 2 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


@responses.activate
def test_projects_categories_stream(config, projects_categories_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/projectCategory",
        json=projects_categories_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("project_categories", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_screens_stream(config, mock_screen_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("screens", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    # assert len(responses.calls) == 1 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


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

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("screen_tabs", config)
    records = list(read_full_refresh(stream))
    assert len(records) == 3
    assert len(responses.calls) == 3


@responses.activate
def test_sprints_stream(config, mock_board_response, mock_sprints_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("sprints", config)
    records = list(read_full_refresh(stream))
    assert len(records) == 3
    # assert len(responses.calls) == 4 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


@responses.activate
def test_board_does_not_support_sprints(config, mock_board_response, sprints_response, caplog):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/1/sprint?maxResults=50",
        json=sprints_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/3/sprint?maxResults=50",
        json=sprints_response,
    )
    url = f"https://{config['domain']}/rest/agile/1.0/board/2/sprint?maxResults=50"
    error = {"errorMessages": ["The board does not support sprints"], "errors": {}}
    responses.add(responses.GET, url, json=error, status=400)
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
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
        f"https://{config['domain']}/rest/agile/1.0/sprint/2/issue?maxResults=50&fields=key&fields=status&fields=created&fields=updated&jql=updated+%3E%3D+%272021%2F01%2F01+00%3A00%27",
        json=sprints_issues_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("sprint_issues", config)
    records = list(read_full_refresh(stream))
    assert len(records) == 3
    # assert len(responses.calls) == 8 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


@responses.activate
def test_time_tracking_stream(config, time_tracking_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/configuration/timetracking/list",
        json=time_tracking_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("time_tracking", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_users_stream(config, mock_users_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("users", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 2
    # assert len(responses.calls) == 1 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


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

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("users_groups_detailed", config)
    records = list(read_full_refresh(stream))
    assert len(records) == 4
    # assert len(responses.calls) == 3 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


@responses.activate
def test_workflows_stream(config, workflows_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/workflow/search?maxResults=50",
        json=workflows_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("workflows", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_workflow_schemas_stream(config, workflow_schemas_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/workflowscheme?maxResults=50",
        json=workflow_schemas_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("workflow_schemes", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_workflow_statuses_stream(config, workflow_statuses_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/status",
        json=workflow_statuses_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("workflow_statuses", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_workflow_status_categories_stream(config, workflow_status_categories_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/statuscategory",
        json=workflow_status_categories_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("workflow_status_categories", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
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

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("avatars", config)
    records = list(read_full_refresh(stream))
    assert len(records) == 2
    assert len(responses.calls) == 3


@responses.activate
def test_avatars_stream_should_retry(config, caplog):
    for slice in ["issuetype", "project", "user"]:
        url = f"https://{config['domain']}/rest/api/3/avatar/{slice}/system"
        responses.add(method=responses.GET, url=url, json={"errorMessages": ["The error message"], "errors": {}}, status=400)

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("avatars", config)
    records = list(read_full_refresh(stream))
    assert len(records) == 0

    assert "The error message" in caplog.text


@responses.activate
def test_issues_stream(config, mock_projects_responses_additional_project, mock_issues_responses, caplog):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", []) + ["Project3"]}
    stream = Issues(**args)
    records = list(read_full_refresh(stream))
    assert len(records) == 1

    # check if only None values was filtered out from 'fields' field
    assert "empty_field" not in records[0]["fields"]
    assert "non_empty_field" in records[0]["fields"]

    assert len(responses.calls) == 3
    error_message = "Stream `issues`. An error occurred, details: [\"The value '3' does not exist for the field 'project'.\"]. Skipping for now. The user doesn't have permission to the project. Please grant the user to the project."
    assert error_message in caplog.messages


@pytest.mark.parametrize(
    "start_date, lookback_window, stream_state, expected_query",
    [
        (pendulum.parse("2023-09-09T00:00:00Z"), 0, None, None),
        (None, 10, {"updated": "2023-12-14T09:47:00"}, "updated >= '2023/12/14 09:37'"),
        (None, 0, {"updated": "2023-12-14T09:47:00"}, "updated >= '2023/12/14 09:47'"),
    ],
)
def test_issues_stream_jql_compare_date(config, start_date, lookback_window, stream_state, expected_query, caplog):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {
        "authenticator": authenticator,
        "domain": config["domain"],
        "projects": config.get("projects", []) + ["Project3"],
        "lookback_window_minutes": pendulum.duration(minutes=lookback_window),
    }
    stream = Issues(**args)
    assert stream.jql_compare_date(stream_state) == expected_query


@responses.activate
def test_issue_comments_stream(config, mock_projects_responses, mock_issues_responses, issue_comments_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/comment?maxResults=50",
        json=issue_comments_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssueComments(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 3


@responses.activate
def test_issue_custom_field_contexts_stream(config, mock_fields_response, mock_issue_custom_field_contexts_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_custom_field_contexts", config)
    records = list(read_full_refresh(stream))
    assert len(records) == 2
    # assert len(responses.calls) == 4 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


@responses.activate
def test_issue_property_keys_stream(config, issue_property_keys_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/properties?maxResults=50",
        json=issue_property_keys_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_property_keys", config)
    records = [
        r for r in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"issue_key": "TESTKEY13-1", "key": "TESTKEY13-1"})
    ]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_issue_property_keys_stream_not_found_skip(config, issue_property_keys_response):
    config["domain"] = "test_skip_properties"
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/properties?maxResults=50",
        json={"errorMessages": ["Issue does not exist or you do not have permission to see it."], "errors": {}},
        status=404,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_property_keys", config)
    records = [
        r for r in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"issue_key": "TESTKEY13-1", "key": "TESTKEY13-1"})
    ]
    assert len(records) == 0
    assert len(responses.calls) == 1


@responses.activate
def test_project_permissions_stream(config, mock_projects_responses, project_permissions_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/Project1/securitylevel",
        json=project_permissions_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
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
def test_project_email_stream(config, mock_projects_responses, mock_project_emails):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("project_email", config)
    records = list(read_full_refresh(stream))
    assert len(records) == 2
    # assert len(responses.calls) == 2 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


@responses.activate
def test_project_components_stream(config, mock_projects_responses, project_components_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/Project1/component?maxResults=50",
        json=project_components_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("project_components", config)
    records = list(read_full_refresh(stream))
    assert len(records) == 2
    # assert len(responses.calls) == 2 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


@responses.activate
def test_permissions_stream(config, permissions_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/permissions",
        json=permissions_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("permissions", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 1
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

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("labels", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 2


@responses.activate
def test_issue_worklogs_stream(config, mock_projects_responses, mock_issues_responses, issue_worklogs_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/worklog?maxResults=50",
        json=issue_worklogs_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssueWorklogs(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 1
    assert len(responses.calls) == 3


# @responses.activate
# def test_issue_watchers_stream(config, mock_projects_responses, mock_issues_responses, mock_issue_watchers_responses):
#     authenticator = SourceJira().get_authenticator(config=config)
#     args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
#     stream = find_stream("issue_watchers", config)
#     records = list(read_full_refresh(stream))
#
#     assert len(records) == 1
#     assert len(responses.calls) == 3


@responses.activate
def test_issue_votes_stream(config, mock_projects_responses, mock_issues_responses, issue_votes_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/votes",
        json=issue_votes_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_votes", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"key": "Project1"})]

    assert len(records) == 1
    assert len(responses.calls) == 3


@responses.activate
def test_issue_remote_links_stream(config, mock_projects_responses, mock_issues_responses, issue_remote_links_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/remotelink?maxResults=50",
        json=issue_remote_links_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("issue_remote_links", config)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"key": "Project1"})]

    assert len(records) == 2
    assert len(responses.calls) == 3


@responses.activate
def test_project_versions_stream(config, mock_projects_responses, projects_versions_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/Project1/version?maxResults=50",
        json=projects_versions_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("project_versions", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    # assert len(responses.calls) == 2 - should be uncommented once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513


# @pytest.mark.parametrize(
#     "stream, expected_records_number, expected_calls_number, log_message",
#     [
#         (
#             "issues",
#             2,
#             4,
#             "Stream `issues`. An error occurred, details: [\"The value '3' does not "
#             "exist for the field 'project'.\"]. Skipping for now. The user doesn't have "
#             "permission to the project. Please grant the user to the project.",
#         ),
#         (
#             "issue_custom_field_contexts",
#             2,
#             4,
#             "Stream `issue_custom_field_contexts`. An error occurred, details: ['Not found issue custom field context for issue fields issuetype2']. Skipping for now. ",
#         ),
#         (
#             "issue_custom_field_options",
#             1,
#             6,
#             "Stream `issue_custom_field_options`. An error occurred, details: ['Not found issue custom field options for issue fields issuetype3']. Skipping for now. ",
#         ),
#         (
#             "issue_watchers",
#             1,
#             6,
#             "Stream `issue_watchers`. An error occurred, details: ['Not found watchers for issue TESTKEY13-2']. Skipping for now. ",
#         ),
#         (
#             "project_email",
#             4,
#             4,
#             "Stream `project_email`. An error occurred, details: ['No access to emails for project 3']. Skipping for now. ",
#         ),
#     ],
# )
# @responses.activate
# def test_skip_slice(
#     config,
#     mock_projects_responses_additional_project,
#     mock_issues_responses,
#     mock_project_emails,
#     mock_issue_watchers_responses,
#     mock_issue_custom_field_contexts_response_error,
#     mock_issue_custom_field_options_response,
#     mock_fields_response,
#     caplog,
#     stream,
#     expected_records_number,
#     expected_calls_number,
#     log_message,
# ):
#     config["projects"] = config.get("projects", []) + ["Project3", "Project4"]
#     stream = find_stream(stream, config)
#     records = list(read_full_refresh(stream))
#     assert len(records) == expected_records_number
#
#     assert len(responses.calls) == expected_calls_number
#     assert log_message in caplog.messages
