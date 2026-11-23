# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse


class TrelloResponseBuilder:
    @staticmethod
    def records(records: list[dict]) -> HttpResponse:
        return HttpResponse(body=json.dumps(records), status_code=200)

    @staticmethod
    def tokens(access_token: str, refresh_token: str) -> HttpResponse:
        body = {"access_token": access_token, "refresh_token": refresh_token, "expires_in": 3600, "scope": "read:board:trello"}
        return HttpResponse(body=json.dumps(body), status_code=200)

    @staticmethod
    def token_error(status_code: int, error: str) -> HttpResponse:
        return HttpResponse(body=json.dumps({"error": error, "error_description": "refresh_token is invalid"}), status_code=status_code)

    @staticmethod
    def bearer_rejected() -> HttpResponse:
        # Atlassian's edge answers a rejected bearer token with an HTML page, not JSON.
        return HttpResponse(body="<!DOCTYPE html><html><head><title>Unauthorized</title></head></html>", status_code=401)
