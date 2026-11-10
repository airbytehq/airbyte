# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


def request_for(stream: str, config: dict, offset: int | None = None) -> HttpRequest:
    params = {"query": config[f"query_{stream}"], "limit": "50"}
    if offset is not None:
        params["offset"] = str(offset)
    path = {"recreationareaaddresses": "recareaaddresses", "recreationareas": "recareas"}.get(stream, stream)
    return HttpRequest(
        f"https://ridb.recreation.gov/api/v1/{path}",
        query_params=params,
        headers={"apikey": config["apikey"]},
    )
