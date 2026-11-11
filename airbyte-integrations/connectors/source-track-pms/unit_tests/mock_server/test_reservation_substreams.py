# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .helpers import discovered_primary_keys, mock_reservations, read_stream, request, response


@pytest.mark.parametrize("suffix,key", [("fees", "fees"), ("tags", "tags")])
@pytest.mark.parametrize("scenario", ["paginated", "empty", "invalid_page"])
def test_reservation_children(suffix: str, key: str, scenario: str) -> None:
    with HttpMocker() as http_mocker:
        mock_reservations(
            http_mocker, [{"id": 10, "updatedAt": "2024-01-01T00:00:00+0000"}, {"id": 20, "updatedAt": "2024-01-01T00:00:00+0000"}]
        )
        for reservation_id in (10, 20):
            path = f"pms/reservations/{reservation_id}/{suffix.replace('_', '-')}"
            if scenario == "paginated":
                http_mocker.get(request(path), response(key, [{"id": i, "_links": {"self": {"href": "ignored"}}} for i in range(1, 101)]))
                http_mocker.get(request(path, 2), response(key, [{"id": 101}], page=2))
            elif scenario == "empty":
                http_mocker.get(request(path), response(key, []))
            else:
                http_mocker.get(request(path), response(key, [{"id": i} for i in range(1, 101)]))
                http_mocker.get(request(path, 2), HttpResponse('{"status": 409, "detail": "Invalid page provided"}', status_code=409))

        output = read_stream(f"reservations_{suffix}")

        last_child = {"paginated": 101, "empty": 0, "invalid_page": 100}[scenario]
        assert {(r.record.data["reservation_id"], r.record.data["id"]) for r in output.records} == {
            (parent, child) for parent in (10, 20) for child in range(1, last_child + 1)
        }
        assert len(output.records) == 2 * last_child
        assert all("_links" not in r.record.data for r in output.records)
        for reservation_id in (10, 20):
            path = f"pms/reservations/{reservation_id}/{suffix.replace('_', '-')}"
            http_mocker.assert_number_of_calls(request(path), 1)
            if scenario != "empty":
                http_mocker.assert_number_of_calls(request(path, 2), 1)
        assert not any(log.log.level == "ERROR" for log in output.logs)


def test_reservation_children_primary_key() -> None:
    primary_keys = discovered_primary_keys()
    for suffix in ("fees", "tags"):
        assert primary_keys[f"reservations_{suffix}"] == [["reservation_id"], ["id"]]
