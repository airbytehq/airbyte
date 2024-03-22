#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pendulum
import pytest
import requests
import responses
from airbyte_cdk.models import SyncMode
from requests.exceptions import HTTPError
from responses import matchers
from source_jira.source import SourceJira
from source_jira.streams import (
    ApplicationRoles,
    Avatars,
    BoardIssues,
    Boards,
    Dashboards,
    Filters,
    FilterSharing,
    Groups,
    IssueComments,
    IssueCustomFieldContexts,
    IssueCustomFieldOptions,
    IssueFieldConfigurations,
    IssueFields,
    IssueLinkTypes,
    IssueNavigatorSettings,
    IssueNotificationSchemes,
    IssuePriorities,
    IssuePropertyKeys,
    IssueRemoteLinks,
    IssueResolutions,
    Issues,
    IssueSecuritySchemes,
    IssueTypeSchemes,
    IssueVotes,
    IssueWatchers,
    IssueWorklogs,
    JiraSettings,
    Labels,
    Permissions,
    ProjectAvatars,
    ProjectCategories,
    ProjectComponents,
    ProjectEmail,
    ProjectPermissionSchemes,
    Projects,
    ProjectVersions,
    Screens,
    ScreenTabs,
    SprintIssues,
    Sprints,
    TimeTracking,
    Users,
    UsersGroupsDetailed,
    Workflows,
    WorkflowSchemes,
    WorkflowStatusCategories,
    WorkflowStatuses,
)
from source_jira.utils import read_full_refresh


@responses.activate
def test_application_roles_stream_401_error(config, caplog):
    config["domain"] = "test_application_domain"
    responses.add(responses.GET, f"https://{config['domain']}/rest/api/3/applicationrole?maxResults=50", status=401)

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ApplicationRoles(**args)

    is_available, reason = stream.check_availability(logger=logging.Logger, source=SourceJira())

    assert is_available is False

    assert reason == (
        "Unable to read application_roles stream. The endpoint https://test_application_domain/rest/api/3/applicationrole?maxResults=50 returned 401: Unauthorized. Invalid creds were provided, please check your api token, domain and/or email.. Please visit https://docs.airbyte.com/integrations/sources/jira to learn more.  "
    )


@responses.activate
def test_application_roles_stream(config, application_roles_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/applicationrole?maxResults=50",
        json=application_roles_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ApplicationRoles(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_application_roles_stream_http_error(config, application_roles_response):
    responses.add(
        responses.GET, f"https://{config['domain']}/rest/api/3/applicationrole?maxResults=50", json={"error": "not found"}, status=404
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ApplicationRoles(**args)
    with pytest.raises(HTTPError):
        [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]


@responses.activate
def test_boards_stream(config, mock_board_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Boards(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
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
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Boards(**args)
    is_available, reason = stream.check_availability(logger=logging.Logger, source=SourceJira())

    assert is_available is False

    assert reason == (
        "Unable to read boards stream. The endpoint "
        "https://test_boards_domain/rest/agile/1.0/board?maxResults=50 returned 403: "
        "Forbidden. Please check the 'READ' permission(Scopes for Connect apps) "
        "and/or the user has Jira Software rights and access.. Please visit "
        "https://docs.airbyte.com/integrations/sources/jira to learn more.  "
        "403 Client Error: Forbidden for url: "
        "https://test_boards_domain/rest/agile/1.0/board?maxResults=50"
    )


@responses.activate
def test_dashboards_stream(config, dashboards_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/dashboard?maxResults=50",
        json=dashboards_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Dashboards(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_filters_stream(config, mock_filter_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Filters(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_groups_stream(config, groups_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/group/bulk?maxResults=50",
        json=groups_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Groups(**args)

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
    stream = IssueFieldConfigurations(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_issues_link_types_stream(config, issues_link_types_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issueLinkType?maxResults=50",
        json=issues_link_types_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssueLinkTypes(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_issues_navigator_settings_stream(config, issues_navigator_settings_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/settings/columns?maxResults=50",
        json=issues_navigator_settings_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssueNavigatorSettings(**args)

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
    stream = IssueNotificationSchemes(**args)

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
    stream = IssuePriorities(**args)

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
    stream = IssueResolutions(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_issue_security_schemes_stream(config, issue_security_schemes_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issuesecurityschemes?maxResults=50",
        json=issue_security_schemes_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssueSecuritySchemes(**args)

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
    stream = IssueTypeSchemes(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_jira_settings_stream(config, jira_settings_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/application-properties?maxResults=50",
        json=jira_settings_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = JiraSettings(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_board_issues_stream(config, mock_board_response, board_issues_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/1/issue?maxResults=50&fields=key&fields=created&fields=updated",
        json=board_issues_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/2/issue?maxResults=50&fields=key&fields=created&fields=updated",
        json={"errorMessages": ["This board has no columns with a mapped status."], "errors": {}},
        status=500,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/3/issue?maxResults=50&fields=key&fields=created&fields=updated",
        json={},
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = BoardIssues(**args)
    records = list(read_full_refresh(stream))
    assert len(records) == 1
    assert len(responses.calls) == 4


def test_stream_updated_state(config):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = BoardIssues(**args)

    current_stream_state = {"22": {"updated": "2023-10-01T00:00:00Z"}}
    latest_record = {"boardId": 22, "updated": "2023-09-01T00:00:00Z"}

    assert {"22": {"updated": "2023-10-01T00:00:00Z"}} == stream.get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)


@responses.activate
def test_filter_sharing_stream(config, mock_filter_response, filter_sharing_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/filter/1/permission?maxResults=50",
        json=filter_sharing_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = FilterSharing(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 1
    assert len(responses.calls) == 2


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
        f"https://{config['domain']}/rest/api/3/project/Project1/avatars?maxResults=50",
        json=projects_avatars_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ProjectAvatars(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 2


@responses.activate
def test_projects_categories_stream(config, projects_categories_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/projectCategory?maxResults=50",
        json=projects_categories_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ProjectCategories(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_screens_stream(config, mock_screen_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Screens(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_screen_tabs_stream(config, mock_screen_response, screen_tabs_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/screens/1/tabs?maxResults=50",
        json=screen_tabs_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/screens/2/tabs?maxResults=50",
        json={},
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ScreenTabs(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    assert len(responses.calls) == 3


@responses.activate
def test_sprints_stream(config, mock_board_response, mock_sprints_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Sprints(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
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
        f"https://{config['domain']}/rest/agile/1.0/board/3/sprint?maxResults=50",
        json=sprints_response,
    )
    url = f"https://{config['domain']}/rest/agile/1.0/board/2/sprint?maxResults=50"
    error = {"errorMessages": ["The board does not support sprints"], "errors": {}}
    responses.add(responses.GET, url, json=error, status=400)
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Sprints(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
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
        f"https://{config['domain']}/rest/agile/1.0/sprint/2/issue?maxResults=50&fields=key&fields=status&fields=created&fields=updated",
        json=sprints_issues_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = SprintIssues(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 3
    assert len(responses.calls) == 8


@responses.activate
def test_time_tracking_stream(config, time_tracking_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/configuration/timetracking/list?maxResults=50",
        json=time_tracking_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = TimeTracking(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_users_stream(config, mock_users_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Users(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_users_groups_detailed_stream(config, mock_users_response, users_groups_detailed_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/user?maxResults=50&accountId=1&expand=groups%2CapplicationRoles",
        json=users_groups_detailed_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/user?maxResults=50&accountId=2&expand=groups%2CapplicationRoles",
        json=users_groups_detailed_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = UsersGroupsDetailed(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 4
    assert len(responses.calls) == 3


@responses.activate
def test_workflows_stream(config, workflows_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/workflow/search?maxResults=50",
        json=workflows_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Workflows(**args)
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
    stream = WorkflowSchemes(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_workflow_statuses_stream(config, workflow_statuses_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/status?maxResults=50",
        json=workflow_statuses_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = WorkflowStatuses(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_workflow_status_categories_stream(config, workflow_status_categories_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/statuscategory?maxResults=50",
        json=workflow_status_categories_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = WorkflowStatusCategories(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_avatars_stream(config, avatars_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/avatar/issuetype/system?maxResults=50",
        json=avatars_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Avatars(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"avatar_type": "issuetype"})]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_avatars_stream_should_retry(config, caplog):
    url = f"https://{config['domain']}/rest/api/3/avatar/issuetype/system?maxResults=50"
    responses.add(method=responses.GET, url=url, json={"errorMessages": ["The error message"], "errors": {}}, status=400)

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Avatars(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"avatar_type": "issuetype"})]
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
        (None, 0, {"updated": "2023-12-14T09:47:00"}, "updated >= '2023/12/14 09:47'")
    ]
)
def test_issues_stream_jql_compare_date(config, start_date, lookback_window, stream_state, expected_query, caplog):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", []) + ["Project3"],
            "lookback_window_minutes": pendulum.duration(minutes=lookback_window)}
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
    stream = IssueCustomFieldContexts(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 4


@responses.activate
def test_issue_property_keys_stream(config, issue_property_keys_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/properties?maxResults=50",
        json=issue_property_keys_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssuePropertyKeys(**args)
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
    stream = IssuePropertyKeys(**args)
    records = [
        r for r in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"issue_key": "TESTKEY13-1", "key": "TESTKEY13-1"})
    ]
    assert len(records) == 0
    assert len(responses.calls) == 1


@responses.activate
def test_project_permissions_stream(config, mock_projects_responses, project_permissions_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/Project1/securitylevel?maxResults=50",
        json=project_permissions_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ProjectPermissionSchemes(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"key": "Project1"})]
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
    assert records == expected_records


@responses.activate
def test_project_email_stream(config, mock_projects_responses, mock_project_emails):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ProjectEmail(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 2


@responses.activate
def test_project_components_stream(config, mock_projects_responses, project_components_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/Project1/component?maxResults=50",
        json=project_components_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ProjectComponents(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"key": "Project1"})]
    assert len(records) == 2
    assert len(responses.calls) == 2


@responses.activate
def test_permissions_stream(config, permissions_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/permissions?maxResults=50",
        json=permissions_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Permissions(**args)
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
    stream = Labels(**args)
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


@responses.activate
def test_issue_watchers_stream(config, mock_projects_responses, mock_issues_responses, mock_issue_watchers_responses):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssueWatchers(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 1
    assert len(responses.calls) == 3


@responses.activate
def test_issue_votes_stream(config, mock_projects_responses, mock_issues_responses, issue_votes_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/votes?maxResults=50",
        json=issue_votes_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssueVotes(**args)
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
    stream = IssueRemoteLinks(**args)
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
    stream = ProjectVersions(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"key": "Project1"})]

    assert len(records) == 2
    assert len(responses.calls) == 2


@pytest.mark.parametrize(
    "stream, expected_records_number, expected_calls_number, log_message",
    [
        (
            Issues,
            2,
            4,
            "Stream `issues`. An error occurred, details: [\"The value '3' does not "
            "exist for the field 'project'.\"]. Skipping for now. The user doesn't have "
            "permission to the project. Please grant the user to the project.",
        ),
        (
            IssueCustomFieldContexts,
            2,
            4,
            "Stream `issue_custom_field_contexts`. An error occurred, details: ['Not found issue custom field context for issue fields issuetype2']. Skipping for now. ",
        ),
        (
            IssueCustomFieldOptions,
            1,
            6,
            "Stream `issue_custom_field_options`. An error occurred, details: ['Not found issue custom field options for issue fields issuetype3']. Skipping for now. ",
        ),
        (
            IssueWatchers,
            1,
            6,
            "Stream `issue_watchers`. An error occurred, details: ['Not found watchers for issue TESTKEY13-2']. Skipping for now. ",
        ),
        (
            ProjectEmail,
            4,
            4,
            "Stream `project_email`. An error occurred, details: ['No access to emails for project 3']. Skipping for now. ",
        ),
    ],
)
@responses.activate
def test_skip_slice(
    config,
    mock_projects_responses_additional_project,
    mock_issues_responses,
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
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", []) + ["Project3", "Project4"]}
    stream = stream(**args)
    records = list(read_full_refresh(stream))
    assert len(records) == expected_records_number

    assert len(responses.calls) == expected_calls_number
    assert log_message in caplog.messages
