# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from _helpers import ORGANIZATION_URI, collection, list_request, mock_user, read_stream, request

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker


def test_teams_fans_out_by_member_and_pages() -> None:
    members = [
        {"uri": "https://api.calendly.com/organization_memberships/a", "user": {"uri": "https://api.calendly.com/users/a"}},
        {"uri": "https://api.calendly.com/organization_memberships/b", "user": {"uri": "https://api.calendly.com/users/b"}},
    ]
    first_a = request("teams", {"count": "100", "user": "https://api.calendly.com/users/a"})
    second_a = request("teams", {"count": "100", "user": "https://api.calendly.com/users/a", "page_token": "next-a"})
    first_b = request("teams", {"count": "100", "user": "https://api.calendly.com/users/b"})
    with HttpMocker() as http:
        user = mock_user(http)
        memberships = list_request("organization_memberships")
        http.get(memberships, collection(members))
        http.get(first_a, collection([{"uri": "https://api.calendly.com/teams/a1"}], "next-a"))
        http.get(second_a, collection([{"uri": "https://api.calendly.com/teams/a2"}]))
        http.get(first_b, collection([{"uri": "https://api.calendly.com/teams/b1"}]))

        output = read_stream("teams", sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert len(output.records) == 3
        for target in [user, memberships, first_a, second_a, first_b]:
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


def test_group_relationships_pages_for_organization() -> None:
    first = request("group_relationships", {"count": "100", "organization": ORGANIZATION_URI})
    second = request("group_relationships", {"count": "100", "organization": ORGANIZATION_URI, "page_token": "next"})
    with HttpMocker() as http:
        user = mock_user(http)
        http.get(first, collection([{"uri": "https://api.calendly.com/group_relationships/1"}], "next"))
        http.get(second, collection([{"uri": "https://api.calendly.com/group_relationships/2"}]))

        output = read_stream("group_relationships", sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert len(output.records) == 2
        for target in [user, first, second]:
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
        http.get(first, collection([{"kind": "zoom_conference", "connected": True}], "ignored"))
        http.get(second, collection([{"kind": "zoom_conference", "connected": True}], "ignored"))

        output = read_stream("locations", sync_mode=SyncMode.full_refresh)

        assert not output.errors
        assert {(record.record.data["user"], record.record.data["kind"], record.record.data["connected"]) for record in output.records} == {
            (member["user"]["uri"], "zoom_conference", True) for member in members
        }
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
