#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import responses
from airbyte_cdk.models import SyncMode
from source_iterable.api import Events, ListUsers


@responses.activate
def test_events_slices_response(mocker):
    emails_sample = [
        {"email": "te.st1@mail.com", "list_id": 12345},
        {"email": "test2@mail.com", "list_id": 12345},
        {"email": "11/test3@mail.com", "list_id": 12345},
        {"email": "test4mail.com", "list_id": 12345},
        {"email": "test-5@mail.com", "list_id": 12345},
        {"email": "test:6@mail.com", "list_id": 12346},
        {"email": "test.7@mail.com", "list_id": 12346},
        {"email": "test,8@mail.com", "list_id": 12346},
        {"email": "te.st9@mail.com1", "list_id": 12346},
        {"email": "test10@mailcom", "list_id": 12346},
    ]
    test_url = "https://api.iterable.com/api/lists/getUsers?listId={list_id}&api_key=key"
    responses.add(
        responses.GET, test_url.format(list_id=12345), body="\n".join([s["email"] for s in emails_sample if s["list_id"] == 12345])
    )
    responses.add(
        responses.GET, test_url.format(list_id=12346), body="\n".join([s["email"] for s in emails_sample if s["list_id"] == 12346])
    )
    mocker.patch.object(ListUsers, "stream_slices", return_value=[{"list_id": 12345}, {"list_id": 12346}])

    stream = Events(api_key="key")
    events_slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh, corsor_field=None))

    assert events_slices == [
        {"email": "te.st1@mail.com"},
        {"email": "test2@mail.com"},
        {"email": "test-5@mail.com"},
        {"email": "test.7@mail.com"},
    ]
