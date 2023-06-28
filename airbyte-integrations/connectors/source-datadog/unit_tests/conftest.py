#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture(name="config")
def config_fixture():
    return {
        "site": "datadoghq.com",
        "api_key": "test_api_key",
        "application_key": "test_application_key",
        "query": "",
        "max_records_per_request": 5000,
        "start_date": "2022-10-10T00:00:00Z",
        "end_date": "2022-10-10T00:10:00Z",
    }


@fixture(name="config_eu")
def config_fixture_eu():
    return {
        "site": "datadoghq.eu",
        "api_key": "test_api_key",
        "application_key": "test_application_key",
        "query": "",
        "max_records_per_request": 5000,
        "start_date": "2022-10-10T00:00:00Z",
        "end_date": "2022-10-10T00:10:00Z",
    }


@fixture(name="mock_responses")
def mock_responses():
    return {
        "Dashboards": {
            "dashboards": [
                {
                    "author_handle": "string",
                    "created_at": "2019-09-19T10:00:00.000Z",
                    "description": "string",
                    "id": "string",
                    "is_read_only": False,
                    "layout_type": "ordered",
                    "modified_at": "2019-09-19T10:00:00.000Z",
                    "title": "string",
                    "url": "string",
                }
            ],
        },
        "Downtimes": {
            "active": True,
            "active_child": {
                "active": True,
                "canceled": 1412799983,
                "creator_id": 123456,
                "disabled": False,
                "downtime_type": 2,
                "end": 1412793983,
                "id": 1626,
                "message": "Message on the downtime",
                "monitor_id": 123456,
                "monitor_tags": ["*"],
                "mute_first_recovery_notification": False,
                "parent_id": 123,
                "recurrence": {
                    "period": 1,
                    "rrule": "FREQ=MONTHLY;BYSETPOS=3;BYDAY=WE;INTERVAL=1",
                    "type": "weeks",
                    "until_date": 1447786293,
                    "until_occurrences": 2,
                    "week_days": ["Mon", "Tue"],
                },
                "scope": ["env:staging"],
                "start": 1412792983,
                "timezone": "America/New_York",
                "updater_id": 123456,
            },
            "canceled": 1412799983,
            "creator_id": 123456,
            "disabled": False,
            "downtime_type": 2,
            "end": 1412793983,
            "id": 1625,
            "message": "Message on the downtime",
            "monitor_id": 123456,
            "monitor_tags": ["*"],
            "mute_first_recovery_notification": False,
            "parent_id": 123,
            "recurrence": {
                "period": 1,
                "rrule": "FREQ=MONTHLY;BYSETPOS=3;BYDAY=WE;INTERVAL=1",
                "type": "weeks",
                "until_date": 1447786293,
                "until_occurrences": 2,
                "week_days": ["Mon", "Tue"],
            },
            "scope": ["env:staging"],
            "start": 1412792983,
            "timezone": "America/New_York",
            "updater_id": 123456,
        },
        "SyntheticTests": {
            "tests": [
                {
                    "config": {
                        "assertions": [{"operator": "contains", "property": "string", "target": 123456, "type": "statusCode"}],
                        "configVariables": [
                            {"example": "string", "id": "string", "name": "VARIABLE_NAME", "pattern": "string", "type": "text"}
                        ],
                        "request": {
                            "allow_insecure": False,
                            "basicAuth": {"password": "PaSSw0RD!", "type": "web", "username": "my_username"},
                            "body": "string",
                            "certificate": {
                                "cert": {"content": "string", "filename": "string", "updatedAt": "string"},
                                "key": {"content": "string", "filename": "string", "updatedAt": "string"},
                            },
                            "certificateDomains": [],
                            "dnsServer": "string",
                            "dnsServerPort": "integer",
                            "follow_redirects": False,
                            "headers": {"<any-key>": "string"},
                            "host": "string",
                            "message": "string",
                            "metadata": {"<any-key>": "string"},
                            "method": "GET",
                            "noSavingResponseBody": False,
                            "numberOfPackets": "integer",
                            "port": "integer",
                            "proxy": {"headers": {"<any-key>": "string"}, "url": "https://example.com"},
                            "query": {},
                            "servername": "string",
                            "service": "string",
                            "shouldTrackHops": False,
                            "timeout": "number",
                            "url": "https://example.com",
                        },
                        "variables": [{"example": "string", "id": "string", "name": "VARIABLE_NAME", "pattern": "string", "type": "text"}],
                    },
                    "creator": {"email": "string", "handle": "string", "name": "string"},
                    "locations": ["aws:eu-west-3"],
                    "message": "string",
                    "monitor_id": "integer",
                    "name": "string",
                    "options": {
                        "accept_self_signed": False,
                        "allow_insecure": False,
                        "checkCertificateRevocation": False,
                        "ci": {"executionRule": "string"},
                        "device_ids": ["laptop_large"],
                        "disableCors": False,
                        "disableCsp": False,
                        "follow_redirects": False,
                        "ignoreServerCertificateError": False,
                        "initialNavigationTimeout": "integer",
                        "min_failure_duration": "integer",
                        "min_location_failed": "integer",
                        "monitor_name": "string",
                        "monitor_options": {"renotify_interval": "integer"},
                        "monitor_priority": "integer",
                        "noScreenshot": False,
                        "restricted_roles": ["xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
                        "retry": {"count": "integer", "interval": "number"},
                        "rumSettings": {"applicationId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "clientTokenId": 12345, "isEnabled": True},
                        "tick_every": "integer",
                    },
                    "public_id": "string",
                    "status": "live",
                    "steps": [
                        {
                            "allowFailure": False,
                            "isCritical": False,
                            "name": "string",
                            "params": {},
                            "timeout": "integer",
                            "type": "assertElementContent",
                        }
                    ],
                    "subtype": "http",
                    "tags": [],
                    "type": "string",
                }
            ]
        },
        "Metrics": {"data": [{"id": "test.metric.latency", "type": "metrics"}]},
        "Incidents": {
            "data": [
                {
                    "attributes": {
                        "created": "2019-09-19T10:00:00.000Z",
                        "customer_impact_duration": "integer",
                        "customer_impact_end": "2019-09-19T10:00:00.000Z",
                        "customer_impact_scope": "An example customer impact scope",
                        "customer_impact_start": "2019-09-19T10:00:00.000Z",
                        "customer_impacted": False,
                        "detected": "2019-09-19T10:00:00.000Z",
                        "fields": {"<any-key>": {}},
                        "modified": "2019-09-19T10:00:00.000Z",
                        "notification_handles": [{"display_name": "Jane Doe", "handle": "@test.user@test.com"}],
                        "public_id": 1,
                        "resolved": "2019-09-19T10:00:00.000Z",
                        "time_to_detect": "integer",
                        "time_to_internal_response": "integer",
                        "time_to_repair": "integer",
                        "time_to_resolve": "integer",
                        "title": "A test incident title",
                    },
                    "id": "00000000-0000-0000-1234-000000000000",
                    "relationships": {
                        "attachments": {"data": [{"id": "00000000-0000-abcd-1000-000000000000", "type": "incident_attachments"}]},
                        "commander_user": {"data": {"id": "00000000-0000-0000-0000-000000000000", "type": "users"}},
                        "created_by_user": {"data": {"id": "00000000-0000-0000-2345-000000000000", "type": "users"}},
                        "integrations": {"data": [{"id": "00000000-abcd-0001-0000-000000000000", "type": "incident_integrations"}]},
                        "last_modified_by_user": {"data": {"id": "00000000-0000-0000-2345-000000000000", "type": "users"}},
                    },
                    "type": "incidents",
                }
            ],
            "included": [
                {
                    "attributes": {
                        "created_at": "2019-09-19T10:00:00.000Z",
                        "disabled": False,
                        "email": "string",
                        "handle": "string",
                        "icon": "string",
                        "modified_at": "2019-09-19T10:00:00.000Z",
                        "name": "string",
                        "service_account": False,
                        "status": "string",
                        "title": "string",
                        "verified": False,
                    },
                    "id": "string",
                    "relationships": {
                        "org": {"data": {"id": "00000000-0000-beef-0000-000000000000", "type": "orgs"}},
                        "other_orgs": {"data": [{"id": "00000000-0000-beef-0000-000000000000", "type": "orgs"}]},
                        "other_users": {"data": [{"id": "00000000-0000-0000-2345-000000000000", "type": "users"}]},
                        "roles": {"data": [{"id": "3653d3c6-0c75-11ea-ad28-fb5701eabc7d", "type": "roles"}]},
                    },
                    "type": "users",
                }
            ],
            "meta": {"pagination": {"next_offset": 1000, "offset": 10, "size": 1000}},
        },
        "IncidentTeams": {
            "data": [
                {
                    "attributes": {"created": "2019-09-19T10:00:00.000Z", "modified": "2019-09-19T10:00:00.000Z", "name": "team name"},
                    "id": "00000000-7ea3-0000-000a-000000000000",
                    "relationships": {
                        "created_by": {"data": {"id": "00000000-0000-0000-2345-000000000000", "type": "users"}},
                        "last_modified_by": {"data": {"id": "00000000-0000-0000-2345-000000000000", "type": "users"}},
                    },
                    "type": "teams",
                }
            ],
            "included": [
                {
                    "attributes": {
                        "created_at": "2019-09-19T10:00:00.000Z",
                        "disabled": False,
                        "email": "string",
                        "handle": "string",
                        "icon": "string",
                        "modified_at": "2019-09-19T10:00:00.000Z",
                        "name": "string",
                        "service_account": False,
                        "status": "string",
                        "title": "string",
                        "verified": False,
                    },
                    "id": "string",
                    "relationships": {
                        "org": {"data": {"id": "00000000-0000-beef-0000-000000000000", "type": "orgs"}},
                        "other_orgs": {"data": [{"id": "00000000-0000-beef-0000-000000000000", "type": "orgs"}]},
                        "other_users": {"data": [{"id": "00000000-0000-0000-2345-000000000000", "type": "users"}]},
                        "roles": {"data": [{"id": "3653d3c6-0c75-11ea-ad28-fb5701eabc7d", "type": "roles"}]},
                    },
                    "type": "users",
                }
            ],
            "meta": {"pagination": {"next_offset": 1000, "offset": 10, "size": 1000}},
        },
        "Users": {
            "data": [
                {
                    "attributes": {
                        "created_at": "2019-09-19T10:00:00.000Z",
                        "disabled": False,
                        "email": "string",
                        "handle": "string",
                        "icon": "string",
                        "modified_at": "2019-09-19T10:00:00.000Z",
                        "name": "string",
                        "service_account": False,
                        "status": "string",
                        "title": "string",
                        "verified": False,
                    },
                    "id": "string",
                    "relationships": {
                        "org": {"data": {"id": "00000000-0000-beef-0000-000000000000", "type": "orgs"}},
                        "other_orgs": {"data": [{"id": "00000000-0000-beef-0000-000000000000", "type": "orgs"}]},
                        "other_users": {"data": [{"id": "00000000-0000-0000-2345-000000000000", "type": "users"}]},
                        "roles": {"data": [{"id": "3653d3c6-0c75-11ea-ad28-fb5701eabc7d", "type": "roles"}]},
                    },
                    "type": "users",
                }
            ],
            "included": [
                {
                    "attributes": {
                        "created_at": "2019-09-19T10:00:00.000Z",
                        "description": "string",
                        "disabled": False,
                        "modified_at": "2019-09-19T10:00:00.000Z",
                        "name": "string",
                        "public_id": "string",
                        "sharing": "string",
                        "url": "string",
                    },
                    "id": "string",
                    "type": "orgs",
                }
            ],
            "meta": {"page": {"total_count": "integer", "total_filtered_count": "integer"}},
        },
        "Logs": {
            "data": [
                {
                    "attributes": {
                        "attributes": {"customAttribute": 123, "duration": 2345},
                        "host": "i-0123",
                        "message": "Host connected to remote",
                        "service": "agent",
                        "status": "INFO",
                        "tags": ["team:A"],
                        "timestamp": "2019-01-02T09:42:36.320Z",
                    },
                    "id": "AAAAAWgN8Xwgr1vKDQAAAABBV2dOOFh3ZzZobm1mWXJFYTR0OA",
                    "type": "log",
                }
            ],
            "links": {
                "next": "https://app.datadoghq.com/api/v2/logs/event?filter[query]=foo\u0026page[cursor]=eyJzdGFydEF0IjoiQVFBQUFYS2tMS3pPbm40NGV3QUFBQUJCV0V0clRFdDZVbG8zY3pCRmNsbHJiVmxDWlEifQ=="
            },
            "meta": {
                "elapsed": 132,
                "page": {"after": "eyJzdGFydEF0IjoiQVFBQUFYS2tMS3pPbm40NGV3QUFBQUJCV0V0clRFdDZVbG8zY3pCRmNsbHJiVmxDWlEifQ=="},
                "request_id": "MWlFUjVaWGZTTTZPYzM0VXp1OXU2d3xLSVpEMjZKQ0VKUTI0dEYtM3RSOFVR",
                "status": "done",
                "warnings": [
                    {
                        "code": "unknown_index",
                        "detail": "indexes: foo, bar",
                        "title": "One or several indexes are missing or invalid, results hold data from the other indexes",
                    }
                ],
            },
        },
        "AuditLogs": {
            "data": [
                {
                    "attributes": {
                        "attributes": {"customAttribute": 123, "duration": 2345},
                        "service": "web-app",
                        "tags": ["team:A"],
                        "timestamp": "2019-01-02T09:42:36.320Z",
                    },
                    "id": "AAAAAWgN8Xwgr1vKDQAAAABBV2dOOFh3ZzZobm1mWXJFYTR0OA",
                    "type": "audit",
                }
            ],
            "links": {
                "next": "https://app.datadoghq.com/api/v2/audit/event?filter[query]=foo\u0026page[cursor]=eyJzdGFydEF0IjoiQVFBQUFYS2tMS3pPbm40NGV3QUFBQUJCV0V0clRFdDZVbG8zY3pCRmNsbHJiVmxDWlEifQ=="
            },
            "meta": {
                "elapsed": 132,
                "page": {"after": "eyJzdGFydEF0IjoiQVFBQUFYS2tMS3pPbm40NGV3QUFBQUJCV0V0clRFdDZVbG8zY3pCRmNsbHJiVmxDWlEifQ=="},
                "request_id": "MWlFUjVaWGZTTTZPYzM0VXp1OXU2d3xLSVpEMjZKQ0VKUTI0dEYtM3RSOFVR",
                "status": "done",
                "warnings": [
                    {
                        "code": "unknown_index",
                        "detail": "indexes: foo, bar",
                        "title": "One or several indexes are missing or invalid, results hold data from the other indexes",
                    }
                ],
            },
        },
    }


@fixture(name="mock_stream")
def mock_stream_fixture(requests_mock):
    def _mock_stream(path, response=None):
        if response is None:
            response = {}

        url = f"https://api.datadoghq.com/api/v1/{path}"
        requests_mock.get(url, json=response)

    return _mock_stream


@fixture(name="config_timeseries")
def config_timeseries_fixture():
    return {
        "site": "datadoghq.eu",
        "api_key": "test_api_key",
        "application_key": "test_application_key",
        "query": "",
        "max_records_per_request": 5000,
        "start_date": "2022-10-10T00:00:00Z",
        "end_date": "2022-10-10T00:10:00Z",
        "queries": [
            {
                "name": "NodeCount",
                "data_source": "metrics",
                "query": "kubernetes_state.node.count{*}"
            },
            {
                "name": "Resource",
                "data_source": "rum",
                "query": "@type:resource @resource.status_code:>=400 @resource.type:(xhr OR fetch)"
            }
        ]
    }


@fixture(name="config_timeseries_invalid")
def config_timeseries_invalid_fixture():
    return {
        "site": "datadoghq.eu",
        "api_key": "test_api_key",
        "application_key": "test_application_key",
        "query": "",
        "max_records_per_request": 5000,
        "start_date": "2022-10-10T00:00:00Z",
        "end_date": "2022-10-10T00:10:00Z",
        "queries": [
            {
                "data_source": "metrics",
                "query": "missing_name_query_string",
            },
            {
                "query": "missing_name_and_data_source_query_string",
            },
            {
                "name": "MissingQuery",
                "data_source": "metrics",
            }
        ]
    }
