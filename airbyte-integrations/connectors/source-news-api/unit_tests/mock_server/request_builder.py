# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


def build_request(stream: str, page: int = 1) -> HttpRequest:
    params = {
        "q": "airbyte",
        "searchIn": "title,description",
        "domains": "example.com",
        "excludeDomains": "excluded.example.com",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": "100",
    }
    if page > 1:
        params["page"] = str(page - 1)
    if stream == "everything":
        params.update({"from": "2025-01-01", "to": "2025-01-02"})
    else:
        params.update({"country": "us", "category": "technology"})
    return HttpRequest(
        f"https://newsapi.org/v2/{stream.replace('_', '-')}",
        query_params=params,
        headers={"X-Api-Key": "test-api-key"},
    )
