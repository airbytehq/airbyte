# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `domain` config validation wired in through
`spec.config_normalization_rules.validations` in `manifest.yaml`.

These tests exercise the validator end-to-end through the declarative manifest
pipeline (`source.streams(config)` triggers `Spec.validate_config`) instead of
calling `ValidateJiraDomain.validate()` directly. This mirrors the precedent in
`source-amplitude/unit_tests/test_custom_extractors.py` where custom components
are exercised via the manifest, not just by direct invocation.
"""

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun
import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import JiraRequestBuilder


_NOW = datetime.now(timezone.utc)
_VALID_DOMAIN = "airbyteio.atlassian.net"


@pytest.mark.parametrize(
    "domain, expected_message_fragment",
    [
        pytest.param("airbyteio", "must include the full host", id="bare_subdomain"),
        pytest.param("https://airbyteio.atlassian.net", "Do not include 'https://'", id="https_scheme"),
        pytest.param("airbyteio.atlassian.net/rest/api/3", "hostname only", id="trailing_path"),
        pytest.param("", "cannot be empty", id="empty_string"),
        pytest.param(".atlassian.net", "valid hostname", id="leading_dot"),
        pytest.param("airbyte..io.com", "valid hostname", id="consecutive_dots"),
    ],
)
def test_invalid_domain_rejected_through_manifest_pipeline(domain, expected_message_fragment):
    """
    Verify that an invalid `domain` is rejected by the manifest's
    `config_normalization_rules.validations` block before any HTTP call is
    attempted, surfacing a clear `ValueError` (which the CDK turns into a
    `config_error`) rather than allowing the connector to spend approximately 10
    minutes retrying DNS-resolution failures.
    """
    config = ConfigBuilder().with_domain(domain).build()
    source = get_source(config=config)

    with pytest.raises(ValueError, match=expected_message_fragment):
        source.streams(config)


@freezegun.freeze_time(_NOW.isoformat())
class TestDomainValidationAcceptsValidDomain(TestCase):
    """Verify that a valid domain passes validation and the connector proceeds
    to issue the expected HTTP request — the validator does not interfere with
    normal sync behavior on accepted inputs."""

    @HttpMocker()
    def test_valid_domain_proceeds_to_http_call(self, http_mocker: HttpMocker):
        config = ConfigBuilder().with_domain(_VALID_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.application_roles_endpoint(_VALID_DOMAIN).build(),
            HttpResponse(
                body=json.dumps(
                    [
                        {
                            "key": "jira-software",
                            "groups": ["jira-software-users"],
                            "name": "Jira Software",
                            "defaultGroups": ["jira-software-users"],
                            "selectedByDefault": False,
                            "defined": True,
                            "numberOfSeats": 100,
                            "remainingSeats": 61,
                            "userCount": 14,
                            "userCountDescription": "users",
                            "hasUnlimitedSeats": False,
                            "platform": False,
                        }
                    ]
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream("application_roles", SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["key"] == "jira-software"
