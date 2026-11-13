# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import gzip
import json
from http import HTTPStatus
from pathlib import Path
from typing import Any

from airbyte_cdk.test.mock_http import HttpResponse


_RESPONSE_PATH = Path(__file__).parent.parent / "resource" / "http" / "response"


def load_fixture(stream_name: str) -> dict[str, Any]:
    return json.loads((_RESPONSE_PATH / f"{stream_name}.json").read_text())


def fixture_names() -> set[str]:
    return {path.stem for path in _RESPONSE_PATH.glob("*.json")}


def json_response(payload: Any, status_code: HTTPStatus = HTTPStatus.OK) -> HttpResponse:
    return HttpResponse(
        body=json.dumps(payload),
        status_code=status_code.value,
        headers={"Content-Type": "application/json"},
    )


def fixture_response(
    stream_name: str,
    *,
    next_url: str | None = None,
    id_suffix: str = "",
) -> HttpResponse:
    payload = load_fixture(stream_name)
    if next_url:
        payload.setdefault("links", {})["next"] = next_url
    if id_suffix:
        records = payload.get("data", [])
        records = records if isinstance(records, list) else [records]
        for record in records:
            record["id"] = f"{record['id']}{id_suffix}"
    return json_response(payload)


def tabular_response(stream_name: str) -> HttpResponse:
    body = load_fixture(stream_name)["body"]
    return HttpResponse(
        body=gzip.compress(body.encode()),
        status_code=HTTPStatus.OK.value,
        headers={"Content-Type": "application/a-gzip"},
    )


def error_response(status_code: HTTPStatus) -> HttpResponse:
    return json_response(
        {"errors": [{"status": str(status_code.value), "title": status_code.phrase}]},
        status_code,
    )
