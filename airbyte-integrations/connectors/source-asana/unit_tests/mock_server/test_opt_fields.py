# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.mock_server.helpers import FIELDS, mock_parents, read_streams, request, response


@pytest.mark.parametrize("stream", FIELDS)
@pytest.mark.parametrize("empty", [False, True])
def test_read_preserves_opt_fields(stream: str, empty: bool) -> None:
    with HttpMocker() as http:
        mock_parents(http, exclude=stream)
        target = request(stream)
        http.get(target, HttpResponse('{"data":[]}', 200) if empty else response())
        output = read_streams(stream)
        assert not output.errors
        assert {r.record.data["gid"] for r in output.records} == (set() if empty else {"1"})
        assert len(output.records) == (0 if empty else (2 if stream in ("attachments", "attachments_compact") else 1))
        http.assert_number_of_calls(target, 2 if stream == "attachments" else 1)
