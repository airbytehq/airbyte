#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import responses
from airbyte_cdk.models import SyncMode

from source_jira.streams import (
    ApplicationRoles,
    Boards,
    Dashboards,
    Filters,
    Groups,
    IssueFields,
    IssueFieldConfigurations,
    IssueLinkTypes,
    IssueNavigatorSettings,
    IssueNotificationSchemes,
    IssuePriorities,
    IssueResolutions,
    IssueSecuritySchemes,
    IssueTypeSchemes
)
from source_jira.source import SourceJira


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
