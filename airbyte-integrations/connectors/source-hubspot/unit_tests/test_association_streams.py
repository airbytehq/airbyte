#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
import yaml
from requests import Response

from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver


@pytest.fixture
def mock_config():
    """Mock configuration for tests."""
    return {
        "start_date": "2021-01-10T00:00:00Z",
        "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
    }


@pytest.fixture
def mock_oauth_config():
    """Mock OAuth configuration for tests."""
    return {
        "start_date": "2021-01-10T00:00:00Z",
        "credentials": {
            "credentials_title": "OAuth Credentials",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
            "access_token": "test_access_token",
        },
    }


@pytest.fixture
def resolved_manifest(manifest_path):
    """Load and resolve $ref references in the manifest."""
    with open(manifest_path) as f:
        raw_manifest = yaml.safe_load(f)
    resolver = ManifestReferenceResolver()
    return resolver.preprocess_manifest(raw_manifest)


@pytest.mark.parametrize(
    "api_response, expected_records",
    [
        # Basic association with single type
        (
            {
                "results": [
                    {
                        "from": {"id": "123"},
                        "to": [{"toObjectId": 456, "associationTypes": [{"typeId": 3, "category": "HUBSPOT_DEFINED", "label": None}]}],
                    }
                ]
            },
            [{"from_id": "123", "to_id": "456", "association_type_id": 3, "category": "HUBSPOT_DEFINED", "label": None}],
        ),
        # Multiple associations with different types
        (
            {
                "results": [
                    {
                        "from": {"id": "100"},
                        "to": [
                            {
                                "toObjectId": 200,
                                "associationTypes": [
                                    {"typeId": 1, "category": "HUBSPOT_DEFINED", "label": None},
                                    {"typeId": 2, "category": "USER_DEFINED", "label": "Custom Label"},
                                ],
                            },
                            {"toObjectId": 300, "associationTypes": [{"typeId": 1, "category": "HUBSPOT_DEFINED", "label": None}]},
                        ],
                    }
                ]
            },
            [
                {"from_id": "100", "to_id": "200", "association_type_id": 1, "category": "HUBSPOT_DEFINED", "label": None},
                {"from_id": "100", "to_id": "200", "association_type_id": 2, "category": "USER_DEFINED", "label": "Custom Label"},
                {"from_id": "100", "to_id": "300", "association_type_id": 1, "category": "HUBSPOT_DEFINED", "label": None},
            ],
        ),
        # Empty response
        ({"results": []}, []),
        # From object with no associations
        ({"results": [{"from": {"id": "999"}, "to": []}]}, []),
    ],
    ids=["basic_single_association", "multiple_associations_and_types", "empty_response", "no_associations_for_object"],
)
def test_association_stream_extractor(api_response, expected_records, mock_config, components_module):
    """Test HubspotAssociationStreamExtractor extracts and flattens associations correctly."""
    extractor = components_module.HubspotAssociationStreamExtractor(
        from_object="deals", to_object="contacts", config=mock_config, parameters={}
    )

    # Mock response
    mock_response = Mock(spec=Response)
    mock_response.json.return_value = api_response

    # Extract records
    records = list(extractor.extract_records(mock_response))

    # Verify
    assert len(records) == len(expected_records)
    for record, expected in zip(records, expected_records):
        assert record == expected


def test_association_stream_extractor_string_ids(mock_config, components_module):
    """Test that extractor converts numeric IDs to strings for consistency."""
    api_response = {
        "results": [
            {
                "from": {"id": 123},  # numeric ID
                "to": [
                    {
                        "toObjectId": 456,  # numeric ID
                        "associationTypes": [{"typeId": 3, "category": "HUBSPOT_DEFINED", "label": None}],
                    }
                ],
            }
        ]
    }

    extractor = components_module.HubspotAssociationStreamExtractor(
        from_object="deals", to_object="contacts", config=mock_config, parameters={}
    )

    mock_response = Mock(spec=Response)
    mock_response.json.return_value = api_response

    records = list(extractor.extract_records(mock_response))

    assert len(records) == 1
    assert isinstance(records[0]["from_id"], str)
    assert isinstance(records[0]["to_id"], str)
    assert records[0]["from_id"] == "123"
    assert records[0]["to_id"] == "456"


def test_association_stream_extractor_with_labeled_associations(mock_config, components_module):
    """Test extraction of labeled (custom) associations."""
    api_response = {
        "results": [
            {
                "from": {"id": "deal_123"},
                "to": [{"toObjectId": 456, "associationTypes": [{"typeId": 100, "category": "USER_DEFINED", "label": "Primary Contact"}]}],
            }
        ]
    }

    extractor = components_module.HubspotAssociationStreamExtractor(
        from_object="deals", to_object="contacts", config=mock_config, parameters={}
    )

    mock_response = Mock(spec=Response)
    mock_response.json.return_value = api_response

    records = list(extractor.extract_records(mock_response))

    assert len(records) == 1
    assert records[0]["label"] == "Primary Contact"
    assert records[0]["category"] == "USER_DEFINED"
    assert records[0]["association_type_id"] == 100


# --- Custom Object Association Stream Tests ---


class TestCustomObjectAssociationStreamRefResolution:
    """Tests that base_custom_object_association_stream correctly inherits from base_association_stream via $ref."""

    def test_custom_stream_inherits_primary_key(self, resolved_manifest):
        """Custom association stream should inherit the same primary key as the base."""
        base = resolved_manifest["definitions"]["base_association_stream"]
        custom = resolved_manifest["definitions"]["base_custom_object_association_stream"]
        assert custom["primary_key"] == base["primary_key"]
        assert custom["primary_key"] == ["from_id", "to_id", "association_type_id"]

    def test_custom_stream_inherits_record_selector(self, resolved_manifest):
        """Custom association stream should use the same custom extractor as the base."""
        base_extractor = resolved_manifest["definitions"]["base_association_stream"]["retriever"]["record_selector"]["extractor"]
        custom_extractor = resolved_manifest["definitions"]["base_custom_object_association_stream"]["retriever"]["record_selector"][
            "extractor"
        ]
        assert custom_extractor["type"] == base_extractor["type"]
        assert custom_extractor["class_name"] == base_extractor["class_name"]

    def test_custom_stream_inherits_requester_path(self, resolved_manifest):
        """Custom association stream should use the same API path as the base."""
        base_path = resolved_manifest["definitions"]["base_association_stream"]["retriever"]["requester"]["path"]
        custom_path = resolved_manifest["definitions"]["base_custom_object_association_stream"]["retriever"]["requester"]["path"]
        assert custom_path == base_path
        assert "crm/v4/associations" in custom_path

    def test_custom_stream_inherits_schema_loader(self, resolved_manifest):
        """Custom association stream should use the same schema as the base."""
        base_schema = resolved_manifest["definitions"]["base_association_stream"]["schema_loader"]
        custom_schema = resolved_manifest["definitions"]["base_custom_object_association_stream"]["schema_loader"]
        assert custom_schema == base_schema

    def test_custom_stream_inherits_paginator(self, resolved_manifest):
        """Custom association stream should inherit NoPagination from the base."""
        base_paginator = resolved_manifest["definitions"]["base_association_stream"]["retriever"]["paginator"]
        custom_paginator = resolved_manifest["definitions"]["base_custom_object_association_stream"]["retriever"]["paginator"]
        assert custom_paginator == base_paginator
        assert custom_paginator["type"] == "NoPagination"

    def test_custom_stream_overrides_error_handler(self, resolved_manifest):
        """Custom association stream should override the error handler with its own (including 400/403 FAIL filters)."""
        custom_requester = resolved_manifest["definitions"]["base_custom_object_association_stream"]["retriever"]["requester"]
        assert "error_handler" in custom_requester

        # The custom error handler should be a DefaultErrorHandler (not the base's CustomErrorHandler)
        custom_error_handler = custom_requester["error_handler"]
        assert custom_error_handler["type"] == "DefaultErrorHandler"

        # Verify it has the custom-object-specific 400 filter with a message about custom object names
        filter_400 = next((f for f in custom_error_handler["response_filters"] if 400 in f.get("http_codes", [])), None)
        assert filter_400 is not None
        assert "custom object" in filter_400["error_message"].lower()


class TestCustomObjectAssociationStreamErrorHandler:
    """Tests for the error handler configuration on the custom object association stream."""

    def _get_error_handler(self, resolved_manifest):
        return resolved_manifest["definitions"]["base_custom_object_association_stream"]["retriever"]["requester"]["error_handler"]

    def test_error_handler_has_response_filters(self, resolved_manifest):
        """Error handler should have response filters for various HTTP status codes."""
        error_handler = self._get_error_handler(resolved_manifest)
        assert "response_filters" in error_handler
        assert len(error_handler["response_filters"]) > 0

    def test_400_response_fails_with_config_error_message(self, resolved_manifest):
        """HTTP 400 should be mapped to FAIL action with a user-facing message about invalid custom object names."""
        error_handler = self._get_error_handler(resolved_manifest)
        filter_400 = next((f for f in error_handler["response_filters"] if 400 in f.get("http_codes", [])), None)
        assert filter_400 is not None, "Expected a response filter for HTTP 400"
        assert filter_400["action"] == "FAIL"
        assert "custom object" in filter_400["error_message"].lower() or "bad request" in filter_400["error_message"].lower()

    def test_403_response_fails_with_permission_error_message(self, resolved_manifest):
        """HTTP 403 should be mapped to FAIL action with a permission error message."""
        error_handler = self._get_error_handler(resolved_manifest)
        filter_403 = next((f for f in error_handler["response_filters"] if 403 in f.get("http_codes", [])), None)
        assert filter_403 is not None, "Expected a response filter for HTTP 403"
        assert filter_403["action"] == "FAIL"
        assert "permission" in filter_403["error_message"].lower() or "access denied" in filter_403["error_message"].lower()

    def test_429_response_retries(self, resolved_manifest):
        """HTTP 429 (rate limit) should be mapped to RETRY action."""
        error_handler = self._get_error_handler(resolved_manifest)
        filter_429 = next((f for f in error_handler["response_filters"] if 429 in f.get("http_codes", [])), None)
        assert filter_429 is not None, "Expected a response filter for HTTP 429"
        assert filter_429["action"] == "RETRY"

    def test_5xx_response_retries(self, resolved_manifest):
        """HTTP 502/503 should be mapped to RETRY action."""
        error_handler = self._get_error_handler(resolved_manifest)
        filter_5xx = next(
            (f for f in error_handler["response_filters"] if 502 in f.get("http_codes", []) or 503 in f.get("http_codes", [])),
            None,
        )
        assert filter_5xx is not None, "Expected a response filter for HTTP 502/503"
        assert filter_5xx["action"] == "RETRY"

    def test_error_handler_has_backoff_strategies(self, resolved_manifest):
        """Error handler should include backoff strategies for retries."""
        error_handler = self._get_error_handler(resolved_manifest)
        assert "backoff_strategies" in error_handler
        backoff_types = [b["type"] for b in error_handler["backoff_strategies"]]
        assert "WaitTimeFromHeader" in backoff_types
        assert "ExponentialBackoffStrategy" in backoff_types


class TestCustomObjectAssociationDynamicStreams:
    """Tests for the DynamicDeclarativeStream resolution of custom object association streams."""

    @pytest.fixture
    def config_with_custom_associations(self):
        """Config with custom_object_association_streams defined."""
        return {
            "start_date": "2021-01-10T00:00:00Z",
            "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
            "custom_object_association_streams": [
                {"from_object": "p_my_custom_object", "to_object": "contacts"},
            ],
        }

    @pytest.fixture
    def config_with_custom_stream_name(self):
        """Config with custom_object_association_streams using a custom stream_name."""
        return {
            "start_date": "2021-01-10T00:00:00Z",
            "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
            "custom_object_association_streams": [
                {"from_object": "p_my_custom_object", "to_object": "contacts", "stream_name": "my_custom_to_contacts"},
            ],
        }

    @pytest.fixture
    def config_with_multiple_custom_associations(self):
        """Config with multiple custom_object_association_streams entries."""
        return {
            "start_date": "2021-01-10T00:00:00Z",
            "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
            "custom_object_association_streams": [
                {"from_object": "p_my_custom_object", "to_object": "contacts"},
                {"from_object": "2-12345", "to_object": "companies"},
                {"from_object": "deals", "to_object": "p_another_custom"},
            ],
        }

    def test_custom_association_stream_created_from_config(self, requests_mock, config_with_custom_associations):
        """A custom object association stream should be created when custom_object_association_streams is in the config."""
        from .conftest import get_source

        requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
        streams = get_source(config_with_custom_associations).streams(config_with_custom_associations)
        stream_names = [s.name for s in streams]
        assert "associations_p_my_custom_object_contacts" in stream_names

    def test_custom_association_stream_default_name(self, requests_mock, config_with_custom_associations):
        """Default stream name should be associations_<from_object>_<to_object>."""
        from .conftest import get_source

        requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
        streams = get_source(config_with_custom_associations).streams(config_with_custom_associations)
        stream_names = [s.name for s in streams]
        assert "associations_p_my_custom_object_contacts" in stream_names

    def test_custom_association_stream_custom_name(self, requests_mock, config_with_custom_stream_name):
        """When stream_name is provided, it should be used instead of the default."""
        from .conftest import get_source

        requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
        streams = get_source(config_with_custom_stream_name).streams(config_with_custom_stream_name)
        stream_names = [s.name for s in streams]
        assert "my_custom_to_contacts" in stream_names
        assert "associations_p_my_custom_object_contacts" not in stream_names

    def test_multiple_custom_association_streams(self, requests_mock, config_with_multiple_custom_associations):
        """Multiple custom association streams should all be created."""
        from .conftest import get_source

        requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
        streams = get_source(config_with_multiple_custom_associations).streams(config_with_multiple_custom_associations)
        stream_names = [s.name for s in streams]
        assert "associations_p_my_custom_object_contacts" in stream_names
        assert "associations_2-12345_companies" in stream_names
        assert "associations_deals_p_another_custom" in stream_names

    def test_no_custom_streams_without_config(self, requests_mock):
        """Without custom_object_association_streams in config, no custom association streams should be created."""
        from .conftest import get_source

        config = {
            "start_date": "2021-01-10T00:00:00Z",
            "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
        }
        requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
        streams = get_source(config).streams(config)
        stream_names = [s.name for s in streams]
        # No stream name should start with "associations_p_" or contain custom object patterns
        custom_association_streams = [n for n in stream_names if n.startswith("associations_p_") or "2-" in n]
        assert len(custom_association_streams) == 0


class TestCustomObjectAssociationCursorField:
    """Tests that custom object association streams always use hs_lastmodifieddate."""

    def test_custom_stream_always_uses_hs_lastmodifieddate(self, resolved_manifest):
        """The custom object DynamicDeclarativeStream components_mapping should always set hs_lastmodifieddate
        (not conditionally based on contacts like the standard association streams)."""
        # Find the DynamicDeclarativeStream that uses base_custom_object_association_stream
        dynamic_streams = resolved_manifest.get("dynamic_streams", [])
        custom_dynamic = None
        for ds in dynamic_streams:
            # After resolution, we can't check $ref directly. Check if the components_resolver
            # reads from custom_object_association_streams config pointer
            resolver = ds.get("components_resolver", {})
            stream_config = resolver.get("stream_config", {})
            configs_pointer = stream_config.get("configs_pointer", [])
            if "custom_object_association_streams" in configs_pointer:
                custom_dynamic = ds
                break

        assert custom_dynamic is not None, "Expected to find a DynamicDeclarativeStream for custom_object_association_streams"

        # Check that cursor_field and cursor_filter_property_field are always hs_lastmodifieddate (no contacts conditional)
        mappings = custom_dynamic["components_resolver"]["components_mapping"]
        cursor_field_mapping = None
        cursor_filter_mapping = None
        for mapping in mappings:
            field_path = mapping.get("field_path", [])
            if "cursor_field" in field_path:
                cursor_field_mapping = mapping
            if "cursor_filter_property_field" in field_path:
                cursor_filter_mapping = mapping

        assert cursor_field_mapping is not None, "Expected a mapping for cursor_field"
        assert cursor_filter_mapping is not None, "Expected a mapping for cursor_filter_property_field"

        # These should be hardcoded to hs_lastmodifieddate, NOT a Jinja conditional
        assert cursor_field_mapping["value"] == "hs_lastmodifieddate"
        assert cursor_filter_mapping["value"] == "hs_lastmodifieddate"

    def test_standard_stream_has_contacts_conditional(self, resolved_manifest):
        """In contrast, the standard association stream should have a conditional for contacts vs other objects."""
        dynamic_streams = resolved_manifest.get("dynamic_streams", [])
        standard_dynamic = None
        for ds in dynamic_streams:
            resolver = ds.get("components_resolver", {})
            stream_config = resolver.get("stream_config", {})
            configs_pointer = stream_config.get("configs_pointer", [])
            if "association_streams" in configs_pointer:
                standard_dynamic = ds
                break

        assert standard_dynamic is not None, "Expected to find a DynamicDeclarativeStream for association_streams"

        mappings = standard_dynamic["components_resolver"]["components_mapping"]
        cursor_field_mapping = None
        for mapping in mappings:
            field_path = mapping.get("field_path", [])
            if "cursor_field" in field_path:
                cursor_field_mapping = mapping
                break

        assert cursor_field_mapping is not None
        # Standard streams use Jinja conditional for contacts
        assert "contacts" in cursor_field_mapping["value"]
        assert "lastmodifieddate" in cursor_field_mapping["value"]


class TestCustomObjectAssociationExtractor:
    """Tests that the extractor works correctly with custom object identifiers."""

    def test_extractor_with_custom_object_identifiers(self, mock_config, components_module):
        """Extractor should work with custom object identifiers like fullyQualifiedName."""
        api_response = {
            "results": [
                {
                    "from": {"id": "123"},
                    "to": [{"toObjectId": 456, "associationTypes": [{"typeId": 3, "category": "HUBSPOT_DEFINED", "label": None}]}],
                }
            ]
        }

        extractor = components_module.HubspotAssociationStreamExtractor(
            from_object="p_my_custom_object", to_object="contacts", config=mock_config, parameters={}
        )

        mock_response = Mock(spec=Response)
        mock_response.json.return_value = api_response

        records = list(extractor.extract_records(mock_response))

        assert len(records) == 1
        assert records[0]["from_id"] == "123"
        assert records[0]["to_id"] == "456"

    def test_extractor_with_object_type_id(self, mock_config, components_module):
        """Extractor should work with objectTypeId format like '2-12345'."""
        api_response = {
            "results": [
                {
                    "from": {"id": "789"},
                    "to": [
                        {
                            "toObjectId": 101,
                            "associationTypes": [{"typeId": 5, "category": "USER_DEFINED", "label": "Related"}],
                        }
                    ],
                }
            ]
        }

        extractor = components_module.HubspotAssociationStreamExtractor(
            from_object="2-12345", to_object="2-67890", config=mock_config, parameters={}
        )

        mock_response = Mock(spec=Response)
        mock_response.json.return_value = api_response

        records = list(extractor.extract_records(mock_response))

        assert len(records) == 1
        assert records[0]["from_id"] == "789"
        assert records[0]["to_id"] == "101"
        assert records[0]["label"] == "Related"
