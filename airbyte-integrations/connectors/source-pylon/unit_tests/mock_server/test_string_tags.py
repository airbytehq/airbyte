# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import NOW, fixture_record, list_request, page, run, search_request


@pytest.mark.parametrize("stream", ["accounts", "issues"])
@pytest.mark.parametrize("tags", [[], ["synthetic-priority", "synthetic-support"]])
@freeze_time(NOW)
def test_string_tags_are_emitted_unchanged(stream: str, tags: list[str]) -> None:
    record = {**fixture_record(stream), "tags": tags}
    request = search_request() if stream == "issues" else list_request("accounts")
    with HttpMocker() as mocker:
        if stream == "issues":
            mocker.post(request, page([record]))
        else:
            mocker.get(request, page([record]))
        output = run(stream)
        mocker.assert_number_of_calls(request, 1)
    assert output.errors == []
    assert [message.record.data["tags"] for message in output.records] == [tags]
