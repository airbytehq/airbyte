# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest
from unit_tests.conftest import CONFIG


class DatadogRequestBuilder:
    """Builds the request a test expects. A request matches only when its query parameters are exactly these."""

    @classmethod
    def audit_logs_endpoint(cls) -> "DatadogRequestBuilder":
        return cls("v2/audit/events")

    @classmethod
    def dashboards_endpoint(cls) -> "DatadogRequestBuilder":
        return cls("v1/dashboard")

    @classmethod
    def incidents_endpoint(cls) -> "DatadogRequestBuilder":
        return cls("v2/incidents")

    @classmethod
    def logs_endpoint(cls) -> "DatadogRequestBuilder":
        return cls("v2/logs/events")

    @classmethod
    def metrics_endpoint(cls) -> "DatadogRequestBuilder":
        return cls("v2/metrics")

    @classmethod
    def service_level_objectives_endpoint(cls) -> "DatadogRequestBuilder":
        return cls("v1/slo")

    @classmethod
    def synthetic_tests_endpoint(cls) -> "DatadogRequestBuilder":
        return cls("v1/synthetics/tests")

    def __init__(self, path: str) -> None:
        self._path = path
        self._query_params: dict[str, str] = {}

    def with_query_param(self, name: str, value: str | int) -> "DatadogRequestBuilder":
        self._query_params[name] = str(value)
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"https://api.{CONFIG['site']}/api/{self._path}",
            query_params=self._query_params or None,
            headers={"DD-API-KEY": CONFIG["api_key"], "DD-APPLICATION-KEY": CONFIG["application_key"]},
        )
