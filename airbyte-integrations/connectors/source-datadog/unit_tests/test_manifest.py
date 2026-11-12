# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

from unit_tests.conftest import CONFIG, get_source


STREAMS = [
    "audit_logs",
    "dashboards",
    "downtimes",
    "incident_teams",
    "incidents",
    "logs",
    "metrics",
    "monitors",
    "service_level_objectives",
    "synthetic_tests",
    "users",
]

# https://docs.datadoghq.com/getting_started/site/
DATADOG_SITES = [
    "datadoghq.com",
    "us3.datadoghq.com",
    "us5.datadoghq.com",
    "datadoghq.eu",
    "ddog-gov.com",
    "us2.ddog-gov.com",
    "ap1.datadoghq.com",
    "ap2.datadoghq.com",
    "uk1.datadoghq.com",
]


def test_manifest_loads_on_the_pinned_cdk_and_lists_every_stream() -> None:
    streams = get_source().streams(CONFIG)

    assert sorted(stream.name for stream in streams) == sorted(STREAMS)


def test_site_offers_every_datadog_site() -> None:
    spec = get_source().spec(logging.getLogger("airbyte"))

    site = spec.connectionSpecification["properties"]["site"]
    assert sorted(site["enum"]) == sorted(DATADOG_SITES)
