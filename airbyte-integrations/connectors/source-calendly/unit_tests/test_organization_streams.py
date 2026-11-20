# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from _helpers import ORGANIZATION_URI, collection, list_request, mock_user, read_stream, request

from airbyte_cdk.models import FailureType, Level, SyncMode, Type
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


def test_teams_lists_organization_teams_once_and_pages() -> None:
    first = request("teams", {"count": "100"})
    second = request("teams", {"count": "100", "page_token": "next"})
    with HttpMocker() as http:
        http.get(first, collection([{"uri": "https://api.calendly.com/teams/1"}], "next"))
        http.get(second, collection([{"uri": "https://api.calendly.com/teams/2"}]))

        output = read_stream("teams", sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert [record.record.data["uri"] for record in output.records] == [
            "https://api.calendly.com/teams/1",
            "https://api.calendly.com/teams/2",
        ]
        for target in [first, second]:
            http.assert_number_of_calls(target, 1)


def test_event_type_memberships_fans_out_by_event_type_and_pages() -> None:
    event_types = [
        {"uri": "https://api.calendly.com/event_types/a", "updated_at": "2024-01-01T00:00:00.000000Z"},
        {"uri": "https://api.calendly.com/event_types/b", "updated_at": "2024-01-02T00:00:00.000000Z"},
    ]
    first_a = request("event_type_memberships", {"count": "100", "event_type": "https://api.calendly.com/event_types/a"})
    second_a = request(
        "event_type_memberships",
        {"count": "100", "event_type": "https://api.calendly.com/event_types/a", "page_token": "next-a"},
    )
    first_b = request("event_type_memberships", {"count": "100", "event_type": "https://api.calendly.com/event_types/b"})
    with HttpMocker() as http:
        user = mock_user(http)
        parent = list_request("event_types")
        http.get(parent, collection(event_types))
        http.get(first_a, collection([{"uri": "https://api.calendly.com/event_type_memberships/a1"}], "next-a"))
        http.get(second_a, collection([{"uri": "https://api.calendly.com/event_type_memberships/a2"}]))
        http.get(first_b, collection([{"uri": "https://api.calendly.com/event_type_memberships/b1"}]))

        output = read_stream("event_type_memberships", sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert len(output.records) == 3
        for target in [user, parent, first_a, second_a, first_b]:
            http.assert_number_of_calls(target, 1)


def test_group_relationships_pages_for_each_group() -> None:
    groups = [f"https://api.calendly.com/groups/{name}" for name in ["a", "b"]]
    first = request("group_relationships", {"count": "100", "group": groups[0]})
    second = request("group_relationships", {"count": "100", "group": groups[0], "page_token": "next"})
    other = request("group_relationships", {"count": "100", "group": groups[1]})
    with HttpMocker() as http:
        user = mock_user(http)
        parents = [list_request("groups"), list_request("groups", "groups-next")]
        http.get(parents[0], collection([{"uri": groups[0]}], "groups-next"))
        http.get(parents[1], collection([{"uri": groups[1]}]))
        http.get(first, collection([{"uri": "https://api.calendly.com/group_relationships/1"}], "next"))
        http.get(second, collection([{"uri": "https://api.calendly.com/group_relationships/2"}]))
        http.get(other, collection([{"uri": "https://api.calendly.com/group_relationships/3"}]))

        output = read_stream("group_relationships", sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert sorted(r.record.data["uri"] for r in output.records) == [
            f"https://api.calendly.com/group_relationships/{i}" for i in [1, 2, 3]
        ]
        assert output.get_stream_statuses("group_relationships")[-1].value == "COMPLETE"
        for target in [user, *parents, first, second, other]:
            http.assert_number_of_calls(target, 1)


def test_group_relationships_without_groups_completes_empty() -> None:
    with HttpMocker() as http:
        mock_user(http)
        http.get(list_request("groups"), collection([]))
        output = read_stream("group_relationships", sync_mode=SyncMode.full_refresh)
        assert not output.errors
        assert not output.records
        assert any(
            s.trace.stream_status.status.value == "COMPLETE" for s in output.get_message_by_types([Type.TRACE]) if s.trace.stream_status
        )


def test_group_relationships_deleted_group_is_skipped() -> None:
    groups = [f"https://api.calendly.com/groups/{name}" for name in ["deleted", "present"]]
    with HttpMocker() as http:
        mock_user(http)
        http.get(list_request("groups"), collection([{"uri": uri} for uri in groups]))
        deleted = request("group_relationships", {"count": "100", "group": groups[0]})
        present = request("group_relationships", {"count": "100", "group": groups[1]})
        http.get(deleted, HttpResponse(body='{"message":"gone"}', status_code=404))
        uri = "https://api.calendly.com/group_relationships/present"
        http.get(present, collection([{"uri": uri}]))
        output = read_stream("group_relationships", sync_mode=SyncMode.full_refresh)
        assert not output.errors
        assert [r.record.data["uri"] for r in output.records] == [uri]
        assert output.get_stream_statuses("group_relationships")[-1].value == "COMPLETE"
        assert not any(entry.log.level == Level.ERROR for entry in output.logs)
        assert any(
            entry.log.level == Level.INFO and "https://api.calendly.com/group_relationships" in entry.log.message for entry in output.logs
        )
        for target in [deleted, present]:
            http.assert_number_of_calls(target, 1)


@pytest.mark.parametrize("endpoint", ["groups", "group_relationships"])
def test_group_relationships_permission_denied_still_fails(endpoint: str) -> None:
    with HttpMocker() as http:
        mock_user(http)
        group = "https://api.calendly.com/groups/a"
        parent = list_request("groups")
        if endpoint == "group_relationships":
            http.get(parent, collection([{"uri": group}]))
            target = request(endpoint, {"count": "100", "group": group})
        else:
            target = parent
        message = "You do not have permission to access this resource."
        http.get(target, HttpResponse(body=json.dumps({"message": message}), status_code=403))
        output = read_stream("group_relationships", sync_mode=SyncMode.full_refresh)
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert message in output.errors[0].trace.error.message
        http.assert_number_of_calls(target, 1)


def test_user_availability_schedules_are_unpaginated_per_member() -> None:
    members = [
        {"uri": "https://api.calendly.com/organization_memberships/a", "user": {"uri": "https://api.calendly.com/users/a"}},
        {"uri": "https://api.calendly.com/organization_memberships/b", "user": {"uri": "https://api.calendly.com/users/b"}},
    ]
    first = request("user_availability_schedules", {"user": "https://api.calendly.com/users/a"})
    second = request("user_availability_schedules", {"user": "https://api.calendly.com/users/b"})
    with HttpMocker() as http:
        user = mock_user(http)
        memberships = list_request("organization_memberships")
        http.get(memberships, collection(members))
        http.get(first, collection([{"uri": "https://api.calendly.com/user_availability_schedules/a"}], "ignored"))
        http.get(second, collection([{"uri": "https://api.calendly.com/user_availability_schedules/b"}], "ignored"))

        output = read_stream("user_availability_schedules", sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert len(output.records) == 2
        for target in [user, memberships, first, second]:
            http.assert_number_of_calls(target, 1)


def test_locations_adds_member_key_and_are_unpaginated() -> None:
    members = [
        {"uri": "https://api.calendly.com/organization_memberships/a", "user": {"uri": "https://api.calendly.com/users/a"}},
        {"uri": "https://api.calendly.com/organization_memberships/b", "user": {"uri": "https://api.calendly.com/users/b"}},
    ]
    first = request("locations", {"user": "https://api.calendly.com/users/a"})
    second = request("locations", {"user": "https://api.calendly.com/users/b"})
    with HttpMocker() as http:
        user = mock_user(http)
        memberships = list_request("organization_memberships")
        http.get(memberships, collection(members))
        # Calendly's own example lists a kind twice for one user, so the stream has no primary key.
        http.get(
            first,
            collection([{"kind": "inbound_call"}, {"kind": "inbound_call"}, {"kind": "zoom_conference", "connected": True}], "ignored"),
        )
        http.get(second, collection([{"kind": "zoom_conference", "connected": True}], "ignored"))

        output = read_stream("locations", sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert sorted((record.record.data["user"], record.record.data["kind"]) for record in output.records) == [
            ("https://api.calendly.com/users/a", "inbound_call"),
            ("https://api.calendly.com/users/a", "inbound_call"),
            ("https://api.calendly.com/users/a", "zoom_conference"),
            ("https://api.calendly.com/users/b", "zoom_conference"),
        ]
        for target in [user, memberships, first, second]:
            http.assert_number_of_calls(target, 1)


def test_organization_invitations_pages_by_organization_uuid() -> None:
    first = request("organizations/test-organization/invitations", {"count": "100", "sort": "created_at:asc"})
    second = request(
        "organizations/test-organization/invitations",
        {"count": "100", "sort": "created_at:asc", "page_token": "next"},
    )
    with HttpMocker() as http:
        user = mock_user(http)
        http.get(first, collection([{"uri": "https://api.calendly.com/organization_invitations/1"}], "next"))
        http.get(second, collection([{"uri": "https://api.calendly.com/organization_invitations/2"}]))

        output = read_stream("organization_invitations", sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert len(output.records) == 2
        for target in [user, first, second]:
            http.assert_number_of_calls(target, 1)


def test_webhook_subscriptions_pages_for_organization() -> None:
    first = request("webhook_subscriptions", {"count": "100", "organization": ORGANIZATION_URI, "scope": "organization"})
    second = request(
        "webhook_subscriptions",
        {"count": "100", "organization": ORGANIZATION_URI, "scope": "organization", "page_token": "next"},
    )
    with HttpMocker() as http:
        user = mock_user(http)
        http.get(first, collection([{"uri": "https://api.calendly.com/webhook_subscriptions/1"}], "next"))
        http.get(second, collection([{"uri": "https://api.calendly.com/webhook_subscriptions/2"}]))

        output = read_stream("webhook_subscriptions", sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert len(output.records) == 2
        for target in [user, first, second]:
            http.assert_number_of_calls(target, 1)


MEMBERS = [
    {"uri": "https://api.calendly.com/organization_memberships/a", "user": {"uri": "https://api.calendly.com/users/a"}},
    {"uri": "https://api.calendly.com/organization_memberships/b", "user": {"uri": "https://api.calendly.com/users/b"}},
]


@pytest.mark.parametrize("stream", ["user_availability_schedules", "locations"])
@pytest.mark.parametrize(
    "status,body",
    [
        (403, {"title": "Permission Denied", "message": "This user is not in your organization"}),
        (404, {"title": "Not Found", "message": "The server could not find the requested resource."}),
    ],
)
def test_member_removed_during_sync_is_skipped(stream: str, status: int, body: dict) -> None:
    with HttpMocker() as http:
        mock_user(http)
        http.get(list_request("organization_memberships"), collection(MEMBERS))
        removed = request(stream, {"user": MEMBERS[0]["user"]["uri"]})
        http.get(removed, HttpResponse(body=json.dumps(body), status_code=status))
        http.get(
            request(stream, {"user": MEMBERS[1]["user"]["uri"]}), collection([{"uri": "https://api.calendly.com/x/1", "kind": "custom"}])
        )

        output = read_stream(stream, sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert len(output.records) == 1
        http.assert_number_of_calls(removed, 1)


@pytest.mark.parametrize(
    "body",
    [
        {
            "title": "Insufficient scope",
            "message": "This operation requires the scopes listed in the 'required_scopes' array.",
            "required_scopes": ["availability:read"],
        },
        {"title": "Permission Denied", "message": "You do not have permission to access this resource."},
    ],
)
def test_other_403s_on_a_member_stream_still_fail(body: dict) -> None:
    with HttpMocker() as http:
        mock_user(http)
        http.get(list_request("organization_memberships"), collection(MEMBERS[:1]))
        http.get(
            request("user_availability_schedules", {"user": MEMBERS[0]["user"]["uri"]}),
            HttpResponse(body=json.dumps(body), status_code=403),
        )

        output = read_stream("user_availability_schedules", sync_mode=SyncMode.full_refresh)

        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert f"Calendly response (403): {body['message']}" in output.errors[0].trace.error.message


def test_event_type_deleted_during_sync_is_skipped() -> None:
    event_types = [
        {"uri": f"https://api.calendly.com/event_types/{name}", "updated_at": "2024-01-01T00:00:00.000000Z"} for name in ["gone", "kept"]
    ]
    with HttpMocker() as http:
        mock_user(http)
        http.get(list_request("event_types"), collection(event_types))
        gone = request("event_type_memberships", {"count": "100", "event_type": event_types[0]["uri"]})
        http.get(gone, HttpResponse(body='{"title":"Not Found","message":"gone"}', status_code=404))
        http.get(
            request("event_type_memberships", {"count": "100", "event_type": event_types[1]["uri"]}),
            collection([{"uri": "https://api.calendly.com/event_type_memberships/1"}]),
        )

        output = read_stream("event_type_memberships", sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert len(output.records) == 1
        http.assert_number_of_calls(gone, 1)


@pytest.mark.parametrize("stream", ["scheduled_events", "event_types"])
def test_not_in_organization_403_still_fails_outside_the_fan_out_streams(stream: str) -> None:
    body = {"title": "Permission Denied", "message": "This user is not in your organization"}
    with HttpMocker() as http:
        mock_user(http)
        http.get(list_request(stream), HttpResponse(body=json.dumps(body), status_code=403))

        output = read_stream(stream, sync_mode=SyncMode.full_refresh)

        assert output.errors[0].trace.error.failure_type == FailureType.config_error
