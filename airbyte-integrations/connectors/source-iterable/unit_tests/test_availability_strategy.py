#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

import responses
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_iterable.streams import Events, Lists, ListUsers


@responses.activate
def test_lists_availability_strategy():
    stream = Lists(authenticator=NoAuth())
    responses.get("https://api.iterable.com/api/lists", json={"lists": []})
    stream_is_available, error = stream.check_availability(MagicMock(), None)
    assert stream_is_available
    responses.replace(responses.GET, "https://api.iterable.com/api/lists", status=401)
    stream_is_available, error = stream.check_availability(MagicMock(), None)
    assert not stream_is_available
    assert error.startswith("The endpoint to access stream 'lists' returned 401: Unauthorized. Provided API Key has not sufficient permissions.")


@responses.activate
def test_list_users_availability_strategy():
    stream = ListUsers(authenticator=NoAuth())
    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=1", body='user1')
    stream_is_available, error = stream.check_availability(MagicMock(), None)
    assert stream_is_available

    responses.replace(responses.GET, "https://api.iterable.com/api/lists", status=401)
    stream_is_available, error = stream.check_availability(MagicMock(), None)
    assert not stream_is_available
    assert error.startswith("The endpoint to access stream 'list_users' returned 401: Unauthorized. Provided API Key has not sufficient permissions.")

    responses.replace(responses.GET, "https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})
    responses.replace(responses.GET, "https://api.iterable.com/api/lists/getUsers?listId=1", status=401)
    stream_is_available, error = stream.check_availability(MagicMock(), None)
    assert not stream_is_available
    assert error.startswith("The endpoint to access stream 'list_users' returned 401: Unauthorized. Provided API Key has not sufficient permissions.")


@responses.activate
def test_events_availability_strategy():
    stream = Events(authenticator=NoAuth())
    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=1", body='user1')
    responses.get("https://api.iterable.com/api/export/userEvents?email=user1&includeCustomEvents=true", json={})
    stream_is_available, error = stream.check_availability(MagicMock(), None)
    assert stream_is_available

    responses.replace(responses.GET, "https://api.iterable.com/api/lists", status=401)
    stream_is_available, error = stream.check_availability(MagicMock(), None)
    assert not stream_is_available
    assert error.startswith("The endpoint to access stream 'events' returned 401: Unauthorized. Provided API Key has not sufficient permissions.")

    responses.replace(responses.GET, "https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})
    responses.replace(responses.GET, "https://api.iterable.com/api/lists/getUsers?listId=1", status=401)
    stream_is_available, error = stream.check_availability(MagicMock(), None)
    assert not stream_is_available
    assert error.startswith("The endpoint to access stream 'events' returned 401: Unauthorized. Provided API Key has not sufficient permissions.")

    responses.replace(responses.GET, "https://api.iterable.com/api/lists/getUsers?listId=1", body='user1')
    responses.replace(responses.GET, "https://api.iterable.com/api/export/userEvents?email=user1&includeCustomEvents=true", status=401)
    stream_is_available, error = stream.check_availability(MagicMock(), None)
    assert not stream_is_available
    assert error.startswith("The endpoint to access stream 'events' returned 401: Unauthorized. Provided API Key has not sufficient permissions.")
