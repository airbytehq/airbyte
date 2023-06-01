#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

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
        responses.GET,
        f"https://{config['domain']}/rest/api/3/applicationrole?maxResults=50",
        json={'error': 'not found'}, status=404
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ApplicationRoles(**args)
    with pytest.raises(HTTPError):
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
    stream = Boards(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    assert len(responses.calls) == 1


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
def test_filters_stream(config, filters_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/filter/search?maxResults=50&expand=description%2Cowner%2Cjql%2CviewUrl%2CsearchUrl%2Cfavourite%2CfavouritedCount%2CsharePermissions%2CisWritable%2Csubscriptions",
        json=filters_response,
    )

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
def test_issues_fields_stream(config, issue_fields_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/field?maxResults=50",
        json=issue_fields_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssueFields(**args)

    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
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
def test_board_issues_stream(config, board_issues_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/1/issue?maxResults=50&fields=key&fields=created&fields=updated",
        json=board_issues_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/2/issue?maxResults=50&fields=key&fields=created&fields=updated",
        json={},
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/agile/1.0/board/3/issue?maxResults=50&fields=key&fields=created&fields=updated",
        json={},
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = BoardIssues(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 1
    assert len(responses.calls) == 3


@responses.activate
def test_filter_sharing_stream(config, filter_sharing_response):
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
    assert len(responses.calls) == 1


@responses.activate
def test_projects_stream(config, projects_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/search?maxResults=50&expand=description%2Clead",
        json=projects_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Projects(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2


@responses.activate
def test_projects_avatars_stream(config, projects_avatars_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/Project1/avatars?maxResults=50",
        json=projects_avatars_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ProjectAvatars(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 4
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
def test_screens_stream(config, screens_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/screens?maxResults=50",
        json=screens_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Screens(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_screen_tabs_stream(config, screen_tabs_response):
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
    assert len(responses.calls) == 2


@responses.activate
def test_sprints_stream(config, sprints_response):
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

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Sprints(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 3
    assert len(responses.calls) == 3


@responses.activate
def test_board_does_not_support_sprints(config):
    url = f"https://{config['domain']}/rest/agile/1.0/board/4/sprint?maxResults=50"
    error = {'errorMessages': ['The board does not support sprints'], 'errors': {}}
    responses.add(responses.GET, url, json=error, status=400)
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Sprints(**args)
    response = requests.get(url)
    actual = stream.should_retry(response)
    assert actual is False


@responses.activate
def test_sprint_issues_stream(config, sprints_issues_response):
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
    assert len(responses.calls) == 3


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
def test_users_stream(config, users_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/users/search?maxResults=50",
        json=users_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Users(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.incremental)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_users_groups_detailed_stream(config, users_groups_detailed_response):
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
    assert len(responses.calls) == 2


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
    records = [r for r in
               stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"avatar_type": "issuetype"})]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_issues_stream(config, projects_response, mock_issues_responses, issues_response, caplog):
    Projects.use_cache = False
    projects_response['values'].append({"id": "3", "key": "Project1"})
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/search?maxResults=50&expand=description%2Clead",
        json=projects_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/search",
        match=[matchers.query_param_matcher({"maxResults": 50, "fields": '*all', "jql": "project in (3)"})],
        json={"errorMessages": ["The value '3' does not exist for the field 'project'."]},
        status=400
    )
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = Issues(**args)
    records = list(read_full_refresh(stream))
    assert len(records) == 1
    assert len(responses.calls) == 4
    error_message = "Stream `issues`. An error occurred, details: [\"The value '3' does not exist for the field 'project'.\"].Check permissions for this project. Skipping for now."
    assert error_message in caplog.messages


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
    records = [r for r in
               stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 2
    assert len(responses.calls) == 4


@responses.activate
def test_issue_custom_field_contexts_stream(config, issue_custom_field_contexts_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/field/issuetype/context?maxResults=50",
        json=issue_custom_field_contexts_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssueCustomFieldContexts(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"field_id": "10130"})]
    assert len(records) == 2
    assert len(responses.calls) == 1


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
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh,
                                              stream_slice={"issue_key": "TESTKEY13-1", "key": "TESTKEY13-1"})]
    assert len(records) == 2
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
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh,
                                              stream_slice={"key": "TESTKEY13-1"})]
    assert len(records) == 4


@responses.activate
def test_project_email_stream(config, mock_projects_responses, project_email_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/1/email?maxResults=50",
        json=project_email_response,
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/2/email?maxResults=50",
        json=project_email_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ProjectEmail(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh,
                                              stream_slice={"key": "TESTKEY13-1"})]
    assert len(records) == 4
    assert len(responses.calls) == 3


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
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh,
                                              stream_slice={"key": "Project1"})]
    assert len(records) == 4
    assert len(responses.calls) == 3


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
    assert len(responses.calls) == 4


@responses.activate
def test_issue_watchers_stream(config, mock_projects_responses, mock_issues_responses, issue_watchers_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/watchers?maxResults=50",
        json=issue_watchers_response,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = IssueWatchers(**args)
    records = [r for r in stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(records) == 1
    assert len(responses.calls) == 4


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
    assert len(responses.calls) == 4


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
    assert len(responses.calls) == 4


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

    assert len(records) == 4
    assert len(responses.calls) == 3
