# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse


def article_response(start: int, count: int) -> HttpResponse:
    articles = [
        {
            "url": f"https://example.com/articles/{index}",
            "title": f"Article {index}",
            "publishedAt": f"2025-01-01T00:{index // 60:02}:{index % 60:02}Z",
        }
        for index in range(start, start + count)
    ]
    return HttpResponse(json.dumps({"status": "ok", "totalResults": 101, "articles": articles}), 200)


def error_response(status: int, code: str, message: str) -> HttpResponse:
    return HttpResponse(json.dumps({"status": "error", "code": code, "message": message}), status)
