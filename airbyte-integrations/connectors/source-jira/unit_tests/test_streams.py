#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re

import pendulum
import pytest
import responses
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_protocol.models import SyncMode
from conftest import find_stream
from responses import matchers
from source_jira.source import SourceJira
from source_jira.streams import IssueFields, Issues, PullRequests
from source_jira.utils import read_full_refresh, read_incremental


@responses.activate
def test_application_roles_stream_401_error(config, caplog):
    config["domain"] = "test_application_domain"
    responses.add(responses.GET, f"https://{config['domain']}/rest/api/3/applicationrole", status=401)

    authenticator = SourceJira().get_authenticator(config=config)
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
    with pytest.raises(
        AirbyteTracedException, match="Not found. The requested resource was not found on the server"
    ):
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

    with pytest.raises(
        AirbyteTracedException,
        match="Forbidden. You don't have permission to access this resource."
    ):
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
def test_python_issues_fields_ids_by_name(config, mock_fields_response):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config["projects"]}
    stream = IssueFields(**args)

    expected_ids_by_name = {
        "Development": ["PrIssueId"],
        "Status Category Changed": ["statuscategorychangedate"],
        "Issue Type": ["issuetype"],
        "Parent": ["parent"],
        "Issue Type2": ["issuetype2"],
        "Issue Type3": ["issuetype3"]
    }
    assert expected_ids_by_name == stream.field_ids_by_name()


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
    output = read(SourceJira(), config, CatalogBuilder().with_stream("sprints", SyncMode.full_refresh).build())

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
        status=400
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
        f"https://{config['domain']}/rest/agile/1.0/sprint/2/issue?maxResults=50&fields=key&fields=status&fields=created&fields=updated&jql=updated+%3E%3D+%272021%2F01%2F01+00%3A00%27",
        json=sprints_issues_response,
    )

    output = read(SourceJira(), config, CatalogBuilder().with_stream("sprint_issues", SyncMode.full_refresh).build())

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
            status=400
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
def test_python_issues_stream(config, mock_projects_responses_additional_project, mock_issues_responses_with_date_filter, caplog):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config["projects"] + ["Project3"]}
    stream = Issues(**args)
    records = list(read_incremental(stream, {"updated": "2021-01-01T00:00:00Z"}))
    assert len(records) == 1

    # check if only None values was filtered out from 'fields' field
    assert "empty_field" not in records[0]["fields"]
    assert "non_empty_field" in records[0]["fields"]

    assert len(responses.calls) == 3
    error_message = ("Stream `issues`. An error occurred, details: The user doesn't have "
                     'permission to the project. Please grant the user to the project. Errors: '
                     '["The value \'3\' does not exist for the field \'project\'."]')
    assert error_message in caplog.messages


@responses.activate
@pytest.mark.parametrize(
    "status_code, response_errorMessages, expected_log_message",
    (
            (400,
             ["The value 'incorrect_project' does not exist for the field 'project'."],
             (
                 "Stream `issues`. An error occurred, details: The user doesn't have permission to the project."
                 " Please grant the user to the project. "
                 "Errors: [\"The value \'incorrect_project\' does not exist for the field \'project\'.\"]"
             )
             ),
            (
                403,
                ["The value 'incorrect_project' doesn't have permission for the field 'project'."],
                (
                    'Stream `issues`. An error occurred, details:'
                    ' Errors: ["The value \'incorrect_project\' doesn\'t have permission for the field \'project\'."]'
                )
            ),
    )
)
def test_python_issues_stream_skip_on_http_codes_error_handling(config, status_code, response_errorMessages, expected_log_message, caplog):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/search?maxResults=50&expand=description%2Clead&status=live&status=archived&status=deleted",
        json={"values": [{"key": "incorrect_project", "id": "incorrect_project"}]},
    )
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/search",
        match=[
            matchers.query_param_matcher(
                {
                    "maxResults": 50,
                    "fields": "*all",
                    "jql": "updated >= '2021/01/01 00:00' and project in (incorrect_project) ORDER BY updated asc",
                    "expand": "renderedFields,transitions,changelog",
                }
            )
        ],
        json={"errorMessages": response_errorMessages},
        status=status_code,
    )

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": "incorrect_project"}
    stream = Issues(**args)

    records = list(read_incremental(stream, {"updated": "2021-01-01T00:00:00Z"}))

    assert len(records) == 0
    assert expected_log_message in caplog.messages


def test_python_issues_stream_updated_state(config):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config["projects"]}
    stream = Issues(**args)

    updated_state = stream._get_updated_state(
        current_stream_state={"updated": "2021-01-01T00:00:00Z"},
        latest_record={"updated": "2021-01-02T00:00:00Z"}
    )
    assert updated_state == {"updated": "2021-01-02T00:00:00Z"}


@pytest.mark.parametrize(
    "dev_field, has_pull_request",
    (
        ("PullRequestOverallDetails{openCount=1, mergedCount=1, declinedCount=1}", True),
        ("PullRequestOverallDetails{openCount=0, mergedCount=0, declinedCount=0}", False),
        ("pullrequest={dataType=pullrequest, state=thestate, stateCount=1}", True),
        ("pullrequest={dataType=pullrequest, state=thestate, stateCount=0}", False),
        ("{}", False),
    )
)
def test_python_pull_requests_stream_has_pull_request(config, dev_field, has_pull_request):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config["projects"]}
    issues_stream = Issues(**args)
    issue_fields_stream = IssueFields(**args)
    incremental_args = {
        **args,
        "start_date": pendulum.parse(config["start_date"]),
        "lookback_window_minutes": 0,
    }
    pull_requests_stream = PullRequests(issues_stream=issues_stream, issue_fields_stream=issue_fields_stream, **incremental_args)

    assert has_pull_request == pull_requests_stream.has_pull_requests(dev_field)


@responses.activate
def test_python_pull_requests_stream_has_pull_request(config, mock_fields_response, mock_projects_responses_additional_project, mock_issues_responses_with_date_filter):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config["projects"]}
    issues_stream = Issues(**args)
    issue_fields_stream = IssueFields(**args)
    incremental_args = {
        **args,
        "start_date": pendulum.parse(config["start_date"]),
        "lookback_window_minutes": 0,
    }
    stream = PullRequests(issues_stream=issues_stream, issue_fields_stream=issue_fields_stream, **incremental_args)

    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/dev-status/1.0/issue/detail?maxResults=50&issueId=10627&applicationType=GitHub&dataType=branch",
        json={"detail": [{"id": "1", "name": "Source Jira: pull request"}]},
    )

    records = list(read_incremental(stream, {"updated": "2021-01-01T00:00:00Z"}))

    assert len(records) == 1
    assert len(responses.calls) == 4


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
def test_python_issue_comments_stream(config, mock_projects_responses, mock_issues_responses_with_date_filter, issue_comments_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/comment?maxResults=50",
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
    output = read(SourceJira(), config, CatalogBuilder().with_stream("project_email", SyncMode.full_refresh).build())

    assert len(output.records) == 2
    assert len(responses.calls) == 2


@responses.activate
def test_project_components_stream(config, mock_non_deleted_projects_responses, project_components_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/project/Project1/component?maxResults=50",
        json=project_components_response,
    )

    output = read(SourceJira(), config, CatalogBuilder().with_stream("project_components", SyncMode.full_refresh).build())

    assert len(output.records) == 2
    assert len(responses.calls) == 2


@responses.activate
def test_permissions_stream(config, permissions_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/permissions",
        json=permissions_response,
    )

    output = read(SourceJira(), config, CatalogBuilder().with_stream("permissions", SyncMode.full_refresh).build())

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

    output = read(SourceJira(), config, CatalogBuilder().with_stream("labels", SyncMode.full_refresh).build())

    assert len(output.records) == 2
    assert len(responses.calls) == 2


@responses.activate
def test_issue_worklogs_stream(config, mock_projects_responses, mock_issues_responses_with_date_filter, issue_worklogs_response):
    responses.add(
        responses.GET,
        f"https://{config['domain']}/rest/api/3/issue/TESTKEY13-1/worklog?maxResults=50",
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

    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = find_stream("project_versions", config)
    records = list(read_full_refresh(stream))

    assert len(records) == 2
    assert len(responses.calls) == 2


@pytest.mark.parametrize(
    "stream, expected_records_number, expected_calls_number, log_message",
    [
        (
            "issues",
            2,
            4,
            "The user doesn't have permission to the project. Please grant the user to the project."
        ),
        (
            "issue_custom_field_contexts",
            2,
            4,
            "Not found. The requested resource was not found on the server."
            # "Stream `issue_custom_field_contexts`. An error occurred, details: ['Not found issue custom field context for issue fields issuetype2']. Skipping for now. ",
        ),
        (
            "issue_custom_field_options",
            1,
            6,
            "Not found. The requested resource was not found on the server."
            # "Stream `issue_custom_field_options`. An error occurred, details: ['Not found issue custom field options for issue fields issuetype3']. Skipping for now. ",
        ),
        (
            "issue_watchers",
            1,
            6,
            "Not found. The requested resource was not found on the server."
            # "Stream `issue_watchers`. An error occurred, details: ['Not found watchers for issue TESTKEY13-2']. Skipping for now. ",
        ),
        (
            "project_email",
            4,
            4,
            "Forbidden. You don't have permission to access this resource."
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
    output = read(SourceJira(), config, CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build())
    assert len(output.records) == expected_records_number

    assert len(responses.calls) == expected_calls_number
    assert log_message in caplog.messages
