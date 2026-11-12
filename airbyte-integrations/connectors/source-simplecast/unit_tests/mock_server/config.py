# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def __init__(self):
        self._config = {"api_token": "test-token"}

    def with_api_token(self, api_token):
        self._config["api_token"] = api_token
        return self

    def build(self):
        return dict(self._config)
