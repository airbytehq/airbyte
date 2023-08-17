#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import unittest

import responses
from source_opsgenie.streams import AlertLogs, AlertRecipients, Alerts, Incidents, Integrations, Services, Teams, Users, UserTeams
from source_opsgenie.util import read_full_refresh


class TeamsStreamTestCase(unittest.TestCase):
    @responses.activate
    def test_teams_list(self):
        config = {"endpoint": "api.opsgenie.com"}
        stream = Teams(**config)
        responses.add(
            "GET",
            "https://api.opsgenie.com/v2/teams",
            json={
                "data": [
                    {"id": "90098alp9-f0e3-41d3-a060-0ea895027630", "name": "ops_team", "description": ""},
                    {"id": "a30alp45-65bf-422f-9d41-67b10a67282a", "name": "TeamName2", "description": "Description"},
                    {"id": "c569c016-alp9-4e20-8a28-bd5dc33b798e", "name": "TeamName", "description": ""},
                ],
                "took": 1.08,
                "requestId": "9cbfalp7-53f5-41ef-a360-be01277a903d",
            },
        )

        records = list(read_full_refresh(stream))
        self.assertEqual(3, len(records))


class UsersStreamTestCase(unittest.TestCase):
    @responses.activate
    def test_users_list(self):
        config = {"endpoint": "api.opsgenie.com"}
        stream = Users(**config)
        responses.add(
            "GET",
            "https://api.opsgenie.com/v2/users",
            json={
                "totalCount": 8,
                "data": [
                    {
                        "blocked": False,
                        "verified": False,
                        "id": "b5b92115-bfe7-43eb-8c2a-e467f2e5ddc4",
                        "username": "john.doe@opsgenie.com",
                        "fullName": "john doe",
                        "role": {"id": "Admin", "name": "Admin"},
                        "timeZone": "Europe/Kirov",
                        "locale": "en_US",
                        "userAddress": {"country": "", "state": "", "city": "", "line": "", "zipCode": ""},
                        "createdAt": "2017-05-12T08:34:30.283Z",
                    },
                    {
                        "blocked": False,
                        "verified": False,
                        "id": "e07c63f0-dd8c-4ad4-983e-4ee7dc600463",
                        "username": "jane.doe@opsgenie.com",
                        "fullName": "jane doe",
                        "role": {"id": "Admin", "name": "Admin"},
                        "timeZone": "Europe/Moscow",
                        "locale": "en_GB",
                        "tags": ["tag1", "tag3"],
                        "userAddress": {
                            "country": "US",
                            "state": "Indiana",
                            "city": "Terre Haute",
                            "line": "567 Stratford Park",
                            "zipCode": "47802",
                        },
                        "details": {"detail1key": ["detail1dvalue1", "detail1value2"], "detail2key": ["detail2value"]},
                        "createdAt": "2017-05-12T09:39:14.41Z",
                    },
                ],
                "took": 0.261,
                "requestId": "d2c50d0c-1c44-4fa5-99d4-20d1e7ca9938",
            },
        )

        records = list(read_full_refresh(stream))
        self.assertEqual(2, len(records))


class ServicesStreamTestCase(unittest.TestCase):
    @responses.activate
    def test_services_list(self):
        config = {"endpoint": "api.opsgenie.com"}
        stream = Services(**config)
        responses.add(
            "GET",
            "https://api.opsgenie.com/v1/services",
            json={
                "data": [
                    {
                        "teamId": "2e3c4c13-51e7-4cf6-a353-34c6f75494c7",
                        "name": "Service API Test Service - Updated",
                        "description": "Service API Test Service Description [Updated]",
                        "id": "6aa85159-9e2e-4e54-8088-546f9c15d513",
                        "tags": [],
                        "isExternal": False,
                    },
                    {
                        "teamId": "2e3c4c13-51e7-4cf6-a353-34c6f75494c7",
                        "name": "Service API Test Service 2 - Updated",
                        "description": "Service API Test Service 2 Description [Updated]",
                        "id": "6aa85159-9e2e-4e54-8088-546f9c15d513",
                        "tags": [],
                        "isExternal": False,
                    },
                ],
                "requestId": "656cfb15-e19f-11e7-ac88-af7c98633ff2",
            },
        )

        records = list(read_full_refresh(stream))
        self.assertEqual(2, len(records))


class IntegrationsStreamTestCase(unittest.TestCase):
    @responses.activate
    def test_services_list(self):
        config = {"endpoint": "api.opsgenie.com"}
        stream = Integrations(**config)
        responses.add(
            "GET",
            "https://api.opsgenie.com/v2/integrations",
            json={
                "code": 200,
                "data": [
                    {"id": "055082dc-9427-48dd-85e0-f93a76e5f4a2", "name": "Signal Sciences", "enabled": True, "type": "SignalSciences"},
                    {"id": "073e8e6a-a481-4b9b-8619-5c31d9a6e5da", "name": "Default API", "enabled": True, "type": "API"},
                    {"id": "3163a9f9-5950-4e73-b99f-92562956e39c", "name": "Datadog", "enabled": False, "type": "Datadog"},
                    {"id": "55e405e3-a130-4c7a-9866-664e498f39a9", "name": "Observium2", "enabled": False, "type": "ObserviumV2"},
                    {"id": "72f6f51b-1ea9-4efd-be1b-4f29d1f593c6", "name": "Solarwinds", "enabled": False, "type": "Solarwinds"},
                    {"id": "733388de-2ac1-4d70-8a2e-82834cb679d6", "name": "Webhook", "enabled": False, "type": "Webhook"},
                    {
                        "id": "8418d193-2dab-4490-b331-8c02cdd196b7",
                        "name": "Marid",
                        "enabled": False,
                        "type": "Marid",
                        "teamId": "87311c02-edda-11eb-9a03-0242ac130003",
                    },
                ],
                "took": 0,
                "requestId": "9ceeb66b-9890-4687-9dbb-a38abc71eda3",
            },
        )

        records = list(read_full_refresh(stream))
        self.assertEqual(7, len(records))


class UserTeamsStreamTestCase(unittest.TestCase):
    @responses.activate
    def test_user_teams_list(self):
        config = {"endpoint": "api.opsgenie.com"}
        users = Users(**config)
        stream = UserTeams(parent_stream=users, **config)
        responses.add(
            "GET",
            "https://api.opsgenie.com/v2/users",
            json={
                "totalCount": 8,
                "data": [
                    {
                        "blocked": False,
                        "verified": False,
                        "id": "b5b92115-bfe7-43eb-8c2a-e467f2e5ddc4",
                        "username": "john.doe@opsgenie.com",
                        "fullName": "john doe",
                        "role": {"id": "Admin", "name": "Admin"},
                        "timeZone": "Europe/Kirov",
                        "locale": "en_US",
                        "userAddress": {"country": "", "state": "", "city": "", "line": "", "zipCode": ""},
                        "createdAt": "2017-05-12T08:34:30.283Z",
                    },
                    {
                        "blocked": False,
                        "verified": False,
                        "id": "e07c63f0-dd8c-4ad4-983e-4ee7dc600463",
                        "username": "jane.doe@opsgenie.com",
                        "fullName": "jane doe",
                        "role": {"id": "Admin", "name": "Admin"},
                        "timeZone": "Europe/Moscow",
                        "locale": "en_GB",
                        "tags": ["tag1", "tag3"],
                        "userAddress": {
                            "country": "US",
                            "state": "Indiana",
                            "city": "Terre Haute",
                            "line": "567 Stratford Park",
                            "zipCode": "47802",
                        },
                        "details": {"detail1key": ["detail1dvalue1", "detail1value2"], "detail2key": ["detail2value"]},
                        "createdAt": "2017-05-12T09:39:14.41Z",
                    },
                ],
                "took": 0.261,
                "requestId": "d2c50d0c-1c44-4fa5-99d4-20d1e7ca9938",
            },
        )

        responses.add(
            "GET",
            "https://api.opsgenie.com/v2/users/b5b92115-bfe7-43eb-8c2a-e467f2e5ddc4/teams",
            json={
                "data": [{"id": "6fa6848c-8cac-4cea-8a98-ad9ff23d9b16", "name": "TeamName"}],
                "took": 0.023,
                "requestId": "bc40b7ad-11ee-4dcd-ae5f-6d75dbc16261",
            },
        )

        responses.add(
            "GET",
            "https://api.opsgenie.com/v2/users/e07c63f0-dd8c-4ad4-983e-4ee7dc600463/teams",
            json={
                "data": [
                    {"id": "6fa6848c-8cac-4cea-8a98-ad9ff23d9b16", "name": "TeamName"},
                    {"id": "bc40b7ad-11ee-4dcd-ae5f-6d75dbc16261", "name": "TeamName"},
                ],
                "took": 0.023,
                "requestId": "bc40b7ad-11ee-4dcd-ae5f-6d75dbc16261",
            },
        )

        records = list(read_full_refresh(stream))
        self.assertEqual(3, len(records))


class AlertsStreamTestCase(unittest.TestCase):
    @responses.activate
    def test_alerts_list(self):
        config = {"endpoint": "api.opsgenie.com", "start_date": "2022-07-01T00:00:00Z"}
        stream = Alerts(**config)
        responses.add(
            "GET",
            "https://api.opsgenie.com/v2/alerts",
            json={
                "data": [
                    {
                        "id": "70413a06-38d6-4c85-92b8-5ebc900d42e2",
                        "tinyId": "1791",
                        "alias": "event_573",
                        "message": "Our servers are in danger",
                        "status": "closed",
                        "acknowledged": False,
                        "isSeen": True,
                        "tags": ["OverwriteQuietHours", "Critical"],
                        "snoozed": True,
                        "snoozedUntil": "2017-04-03T20:32:35.143Z",
                        "count": 79,
                        "lastOccurredAt": "2017-04-03T20:05:50.894Z",
                        "createdAt": "2017-03-21T20:32:52.353Z",
                        "updatedAt": "2017-04-03T20:32:57.301Z",
                        "source": "Isengard",
                        "owner": "morpheus@opsgenie.com",
                        "priority": "P4",
                        "responders": [
                            {"id": "4513b7ea-3b91-438f-b7e4-e3e54af9147c", "type": "team"},
                            {"id": "bb4d9938-c3c2-455d-aaab-727aa701c0d8", "type": "user"},
                            {"id": "aee8a0de-c80f-4515-a232-501c0bc9d715", "type": "escalation"},
                            {"id": "80564037-1984-4f38-b98e-8a1f662df552", "type": "schedule"},
                        ],
                        "integration": {"id": "4513b7ea-3b91-438f-b7e4-e3e54af9147c", "name": "Nebuchadnezzar", "type": "API"},
                        "report": {
                            "ackTime": 15702,
                            "closeTime": 60503,
                            "acknowledgedBy": "agent_smith@opsgenie.com",
                            "closedBy": "neo@opsgenie.com",
                        },
                    },
                    {
                        "id": "70413a06-38d6-4c85-92b8-5ebc900d42e2",
                        "tinyId": "1791",
                        "alias": "event_573",
                        "message": "Sample Message",
                        "status": "open",
                        "acknowledged": False,
                        "isSeen": False,
                        "tags": ["RandomTag"],
                        "snoozed": False,
                        "count": 1,
                        "lastOccurredAt": "2017-03-21T20:32:52.353Z",
                        "createdAt": "2017-03-21T20:32:52.353Z",
                        "updatedAt": "2017-04-03T20:32:57.301Z",
                        "source": "Zion",
                        "owner": "",
                        "priority": "P5",
                        "responders": [],
                        "integration": {"id": "4513b7ea-3b91-b7e4-438f-e3e54af9147c", "name": "My_Lovely_Amazon", "type": "CloudWatch"},
                    },
                ],
                "took": 0.605,
                "requestId": "9ae63dd7-ed00-4c81-86f0-c4ffd33142c9",
            },
        )

        records = list(read_full_refresh(stream))
        self.assertEqual(2, len(records))


class IncidentsStreamTestCase(unittest.TestCase):
    @responses.activate
    def test_alerts_list(self):
        config = {"endpoint": "api.opsgenie.com", "start_date": "2022-07-01T00:00:00Z"}
        stream = Incidents(**config)
        responses.add(
            "GET",
            "https://api.opsgenie.com/v1/incidents",
            json={
                "data": [
                    {
                        "id": "70413a06-38d6-4c85-92b8-5ebc900d42e2",
                        "tinyId": "1791",
                        "message": "Our servers are in danger",
                        "status": "closed",
                        "tags": ["OverwriteQuietHours", "Critical"],
                        "createdAt": "2017-03-21T20:32:52.353Z",
                        "updatedAt": "2017-04-03T20:32:57.301Z",
                        "priority": "P4",
                        "responders": [
                            {"type": "team", "id": "fc1448b7-46b2-401d-9df8-c02675958e3b"},
                            {"type": "team", "id": "fe954a67-813e-4356-87dc-afed1eec6b66"},
                        ],
                        "impactedServices": ["df635094-efd3-48e4-b73a-b8bdfbf1178f", "b6868288-02c7-440b-a693-0a5cf20576f5"],
                    },
                    {
                        "id": "70413a06-38d6-4c85-92b8-5ebc900d42e2",
                        "tinyId": "1791",
                        "message": "Sample Message",
                        "status": "open",
                        "tags": ["RandomTag"],
                        "createdAt": "2017-03-21T20:32:52.353Z",
                        "updatedAt": "2017-04-03T20:32:57.301Z",
                        "priority": "P5",
                        "responders": [{"type": "team", "id": "fc1448b7-46b2-401d-9df8-c02675958e3b"}],
                        "impactedServices": [],
                    },
                ],
                "took": 0.605,
                "requestId": "9ae63dd7-ed00-4c81-86f0-c4ffd33142c9",
            },
        )

        records = list(read_full_refresh(stream))
        self.assertEqual(2, len(records))


class AlertRecipientsStreamTestCase(unittest.TestCase):
    @responses.activate
    def test_alerts_list(self):
        alerts_config = {"endpoint": "api.opsgenie.com", "start_date": "2022-07-01T00:00:00Z"}
        config = {
            "endpoint": "api.opsgenie.com",
        }
        stream = AlertRecipients(parent_stream=Alerts(**alerts_config), **config)
        responses.add(
            "GET",
            "https://api.opsgenie.com/v2/alerts",
            json={
                "data": [
                    {
                        "id": "70413a06-38d6-4c85-92b8-5ebc900d42e2",
                        "tinyId": "1791",
                        "alias": "event_573",
                        "message": "Our servers are in danger",
                        "status": "closed",
                        "acknowledged": False,
                        "isSeen": True,
                        "tags": ["OverwriteQuietHours", "Critical"],
                        "snoozed": True,
                        "snoozedUntil": "2017-04-03T20:32:35.143Z",
                        "count": 79,
                        "lastOccurredAt": "2017-04-03T20:05:50.894Z",
                        "createdAt": "2017-03-21T20:32:52.353Z",
                        "updatedAt": "2017-04-03T20:32:57.301Z",
                        "source": "Isengard",
                        "owner": "morpheus@opsgenie.com",
                        "priority": "P4",
                        "responders": [
                            {"id": "4513b7ea-3b91-438f-b7e4-e3e54af9147c", "type": "team"},
                            {"id": "bb4d9938-c3c2-455d-aaab-727aa701c0d8", "type": "user"},
                            {"id": "aee8a0de-c80f-4515-a232-501c0bc9d715", "type": "escalation"},
                            {"id": "80564037-1984-4f38-b98e-8a1f662df552", "type": "schedule"},
                        ],
                        "integration": {"id": "4513b7ea-3b91-438f-b7e4-e3e54af9147c", "name": "Nebuchadnezzar", "type": "API"},
                        "report": {
                            "ackTime": 15702,
                            "closeTime": 60503,
                            "acknowledgedBy": "agent_smith@opsgenie.com",
                            "closedBy": "neo@opsgenie.com",
                        },
                    }
                ],
                "took": 0.605,
                "requestId": "9ae63dd7-ed00-4c81-86f0-c4ffd33142c9",
            },
        )
        responses.add(
            "GET",
            "https://api.opsgenie.com/v2/alerts/70413a06-38d6-4c85-92b8-5ebc900d42e2/recipients",
            json={
                "data": [
                    {
                        "user": {"id": "2503a523-8ba5-4158-a4bd-7850074b5cca", "username": "neo@opsgenie.com"},
                        "state": "action",
                        "method": "Acknowledge",
                        "createdAt": "2017-04-12T12:27:28.52Z",
                        "updatedAt": "2017-04-12T12:27:52.86Z",
                    },
                    {
                        "user": {"id": "0966cfd8-fc9a-4f5c-a013-7d1f9318aef8", "username": "trinity@opsgenie.com"},
                        "state": "notactive",
                        "method": "",
                        "createdAt": "2017-04-12T12:27:28.571Z",
                        "updatedAt": "2017-04-12T12:27:28.589Z",
                    },
                ],
                "took": 0.605,
                "requestId": "9ae63dd7-ed00-4c81-86f0-c4ffd33142c9",
            },
        )

        records = list(read_full_refresh(stream))
        self.assertEqual(2, len(records))


class AlertLogsStreamTestCase(unittest.TestCase):
    @responses.activate
    def test_alerts_list(self):
        alerts_config = {"endpoint": "api.opsgenie.com", "start_date": "2022-07-01T00:00:00Z"}
        config = {
            "endpoint": "api.opsgenie.com",
        }
        stream = AlertLogs(parent_stream=Alerts(**alerts_config), **config)
        responses.add(
            "GET",
            "https://api.opsgenie.com/v2/alerts",
            json={
                "data": [
                    {
                        "id": "70413a06-38d6-4c85-92b8-5ebc900d42e2",
                        "tinyId": "1791",
                        "alias": "event_573",
                        "message": "Our servers are in danger",
                        "status": "closed",
                        "acknowledged": False,
                        "isSeen": True,
                        "tags": ["OverwriteQuietHours", "Critical"],
                        "snoozed": True,
                        "snoozedUntil": "2017-04-03T20:32:35.143Z",
                        "count": 79,
                        "lastOccurredAt": "2017-04-03T20:05:50.894Z",
                        "createdAt": "2017-03-21T20:32:52.353Z",
                        "updatedAt": "2017-04-03T20:32:57.301Z",
                        "source": "Isengard",
                        "owner": "morpheus@opsgenie.com",
                        "priority": "P4",
                        "responders": [
                            {"id": "4513b7ea-3b91-438f-b7e4-e3e54af9147c", "type": "team"},
                            {"id": "bb4d9938-c3c2-455d-aaab-727aa701c0d8", "type": "user"},
                            {"id": "aee8a0de-c80f-4515-a232-501c0bc9d715", "type": "escalation"},
                            {"id": "80564037-1984-4f38-b98e-8a1f662df552", "type": "schedule"},
                        ],
                        "integration": {"id": "4513b7ea-3b91-438f-b7e4-e3e54af9147c", "name": "Nebuchadnezzar", "type": "API"},
                        "report": {
                            "ackTime": 15702,
                            "closeTime": 60503,
                            "acknowledgedBy": "agent_smith@opsgenie.com",
                            "closedBy": "neo@opsgenie.com",
                        },
                    }
                ],
                "took": 0.605,
                "requestId": "9ae63dd7-ed00-4c81-86f0-c4ffd33142c9",
            },
        )
        responses.add(
            "GET",
            "https://api.opsgenie.com/v2/alerts/70413a06-38d6-4c85-92b8-5ebc900d42e2/logs",
            json={
                "data": [
                    {
                        "log": "Alert acknowledged via web",
                        "type": "system",
                        "owner": "neo@opsgenie.com",
                        "createdAt": "2017-04-12T12:27:52.838Z",
                        "offset": "1492000072838_1492000072838234593",
                    },
                    {
                        "log": "Viewed on [web]",
                        "type": "alertRecipient",
                        "owner": "trinity@opsgenie.com",
                        "createdAt": "2017-04-12T12:27:46.379Z",
                        "offset": "1492000066378_1492000066379000127",
                    },
                ],
                "took": 0.605,
                "requestId": "9ae63dd7-ed00-4c81-86f0-c4ffd33142c9",
            },
        )

        records = list(read_full_refresh(stream))
        self.assertEqual(2, len(records))
