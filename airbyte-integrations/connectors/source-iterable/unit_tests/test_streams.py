#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import requests
import responses
from source_iterable.api import ListUsers


@responses.activate
def test_list_users_parse_response():
    emails_sample = [
        "te.st1@mail.com",
        "test2@mail.com",
        "11/test3@mail.com",
        "test4mail.com",
        "test-5@mail.com",
        "test:6@mail.com",
        "test.7@mail.com",
        "test,8@mail.com",
        "te.st9@mail.com1",
        "test10@mailcom",
    ]
    stream = ListUsers(api_key="key")
    test_url = "https://api.iterable.com/api/lists/getUsers?listId=12345&api_key=key"
    responses.add(responses.GET, test_url, body="\n".join(emails_sample))
    response = requests.get(test_url)

    valid_emails = list(stream.parse_response(response))
    assert valid_emails == [
        {"email": "te.st1@mail.com", "listId": 12345},
        {"email": "test2@mail.com", "listId": 12345},
        {"email": "test-5@mail.com", "listId": 12345},
        {"email": "test.7@mail.com", "listId": 12345},
    ]
