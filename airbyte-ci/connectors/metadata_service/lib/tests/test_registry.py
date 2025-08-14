#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import os
from unittest.mock import Mock, patch

import pytest
from google.cloud import storage
from google.oauth2 import service_account

from metadata_service.constants import REGISTRIES_FOLDER
from metadata_service.models.generated import ConnectorRegistryV0
from metadata_service.registry import (
    ConnectorTypePrimaryKey,
    ConnectorTypes,
    PolymorphicRegistryEntry,
    _apply_metrics_to_registry_entry,
    _build_connector_registry,
    _convert_json_to_metrics_dict,
    _get_connector_type_from_registry_entry,
    _persist_registry,
)


class TestGetConnectorTypeFromRegistryEntry:
    """Tests for _get_connector_type_from_registry_entry function."""

    @pytest.fixture
    def mock_source_entry(self):
        """Create a mock source registry entry."""
        entry = Mock(spec=PolymorphicRegistryEntry)
        setattr(entry, ConnectorTypePrimaryKey.SOURCE.value, "test-source-id")
        return entry

    @pytest.fixture
    def mock_destination_entry(self):
        """Create a mock destination registry entry."""
        entry = Mock(spec=PolymorphicRegistryEntry)
        setattr(entry, ConnectorTypePrimaryKey.DESTINATION.value, "test-destination-id")
        return entry

    @pytest.fixture
    def mock_invalid_entry(self):
        """Create a mock entry that is neither source nor destination."""
        entry = Mock(spec=PolymorphicRegistryEntry)
        return entry

    @pytest.mark.parametrize(
        "entry_fixture,expected_type,description",
        [
            ("mock_source_entry", ConnectorTypes.SOURCE, "source entry"),
            ("mock_destination_entry", ConnectorTypes.DESTINATION, "destination entry"),
        ],
    )
    def test_get_connector_type_from_registry_entry_types(self, entry_fixture, expected_type, description, request):
        """Test connector type detection from registry entries."""
        registry_entry = request.getfixturevalue(entry_fixture)

        result = _get_connector_type_from_registry_entry(registry_entry)

        assert result == expected_type
        assert isinstance(result, ConnectorTypes)

    @pytest.mark.parametrize(
        "entry_fixture,expected_type,has_attribute,not_has_attribute,description",
        [
            (
                "mock_source_entry",
                ConnectorTypes.SOURCE,
                ConnectorTypePrimaryKey.SOURCE.value,
                ConnectorTypePrimaryKey.DESTINATION.value,
                "source entry",
            ),
            (
                "mock_destination_entry",
                ConnectorTypes.DESTINATION,
                ConnectorTypePrimaryKey.DESTINATION.value,
                ConnectorTypePrimaryKey.SOURCE.value,
                "destination entry",
            ),
        ],
    )
    def test_get_connector_type_from_registry_entry_has_correct_attribute(
        self, entry_fixture, expected_type, has_attribute, not_has_attribute, description, request
    ):
        registry_entry = request.getfixturevalue(entry_fixture)

        assert hasattr(registry_entry, has_attribute)
        assert not hasattr(registry_entry, not_has_attribute)

        result = _get_connector_type_from_registry_entry(registry_entry)

        assert result == expected_type

    def test_get_connector_type_from_registry_entry_invalid_raises_error(self, mock_invalid_entry):
        """Test that invalid entry raises ValueError."""
        assert not hasattr(mock_invalid_entry, ConnectorTypePrimaryKey.SOURCE.value)
        assert not hasattr(mock_invalid_entry, ConnectorTypePrimaryKey.DESTINATION.value)

        with pytest.raises(ValueError) as exc_info:
            _get_connector_type_from_registry_entry(mock_invalid_entry)

        assert "Registry entry is not a source or destination" in str(exc_info.value)


class TestConvertJsonToMetricsDict:
    """Tests for _convert_json_to_metrics_dict function."""

    @pytest.mark.parametrize(
        "jsonl_input,expected_output,description",
        [
            (
                '{"_airbyte_data": {"connector_definition_id": "conn-123", "airbyte_platform": "cloud", "usage": 100}}',
                {"conn-123": {"cloud": {"connector_definition_id": "conn-123", "airbyte_platform": "cloud", "usage": 100}}},
                "single connector",
            ),
            (
                '{"_airbyte_data": {"connector_definition_id": "conn-123", "airbyte_platform": "cloud", "usage": 100}}\n{"_airbyte_data": {"connector_definition_id": "conn-456", "airbyte_platform": "oss", "usage": 50}}',
                {
                    "conn-123": {"cloud": {"connector_definition_id": "conn-123", "airbyte_platform": "cloud", "usage": 100}},
                    "conn-456": {"oss": {"connector_definition_id": "conn-456", "airbyte_platform": "oss", "usage": 50}},
                },
                "multiple connectors",
            ),
            ("", {}, "empty input"),
        ],
    )
    def test_convert_json_to_metrics_dict_valid_jsonl(self, jsonl_input, expected_output, description):
        """Test JSONL string conversion to metrics dictionary."""
        result = _convert_json_to_metrics_dict(jsonl_input)

        assert result == expected_output


class TestApplyMetricsToRegistryEntry:
    """Tests for _apply_metrics_to_registry_entry function."""

    @pytest.mark.parametrize(
        "connector_type,registry_entry,metrics_dict,expected_metrics,description",
        [
            (
                ConnectorTypes.SOURCE,
                {"sourceDefinitionId": "source-123", "name": "Test Source"},
                {"source-123": {"cloud": {"usage": 100}}},
                {"cloud": {"usage": 100}},
                "source with matching metrics",
            ),
            (
                ConnectorTypes.DESTINATION,
                {"destinationDefinitionId": "dest-456", "name": "Test Destination"},
                {"dest-456": {"oss": {"usage": 50}}},
                {"oss": {"usage": 50}},
                "destination with matching metrics",
            ),
            (
                ConnectorTypes.SOURCE,
                {"sourceDefinitionId": "source-999", "name": "No Metrics Source"},
                {},
                {},
                "entry with no matching metrics",
            ),
        ],
    )
    def test_apply_metrics_to_registry_entry_scenarios(self, connector_type, registry_entry, metrics_dict, expected_metrics, description):
        """Test metrics application to registry entries."""
        result = _apply_metrics_to_registry_entry(registry_entry, connector_type, metrics_dict)

        assert result["generated"]["metrics"] == expected_metrics
        assert result["name"] == registry_entry["name"]

    def test_apply_metrics_to_registry_entry_preserves_existing_structure(self):
        """Test that existing registry entry structure is preserved."""
        registry_entry = {"sourceDefinitionId": "source-123", "name": "Test Source", "existing_field": "value"}
        metrics_dict = {"source-123": {"cloud": {"usage": 100}}}

        result = _apply_metrics_to_registry_entry(registry_entry, ConnectorTypes.SOURCE, metrics_dict)

        assert result["existing_field"] == "value"
        assert result["name"] == "Test Source"
        assert result["generated"]["metrics"] == {"cloud": {"usage": 100}}


class TestBuildConnectorRegistry:
    """Tests for _build_connector_registry function."""

    @pytest.mark.parametrize(
        "entry_dicts,expected_sources_count,expected_destinations_count,description",
        [
            (
                [
                    {
                        "sourceDefinitionId": "550e8400-e29b-41d4-a716-446655440001",
                        "name": "Source 1",
                        "dockerRepository": "test/source",
                        "dockerImageTag": "1.0.0",
                        "documentationUrl": "https://docs.test.com",
                        "spec": {},
                    },
                    {
                        "destinationDefinitionId": "550e8400-e29b-41d4-a716-446655440002",
                        "name": "Destination 1",
                        "dockerRepository": "test/dest",
                        "dockerImageTag": "1.0.0",
                        "documentationUrl": "https://docs.test.com",
                        "spec": {},
                    },
                ],
                1,
                1,
                "mixed sources and destinations",
            ),
            (
                [
                    {
                        "sourceDefinitionId": "550e8400-e29b-41d4-a716-446655440001",
                        "name": "Source 1",
                        "dockerRepository": "test/source1",
                        "dockerImageTag": "1.0.0",
                        "documentationUrl": "https://docs.test.com",
                        "spec": {},
                    },
                    {
                        "sourceDefinitionId": "550e8400-e29b-41d4-a716-446655440002",
                        "name": "Source 2",
                        "dockerRepository": "test/source2",
                        "dockerImageTag": "1.0.0",
                        "documentationUrl": "https://docs.test.com",
                        "spec": {},
                    },
                ],
                2,
                0,
                "sources only",
            ),
            ([], 0, 0, "empty entries"),
        ],
    )
    def test_build_connector_registry_scenarios(self, entry_dicts, expected_sources_count, expected_destinations_count, description):
        """Test registry building with different entry combinations."""
        entries = []
        for entry_dict in entry_dicts:
            entry = Mock(spec=PolymorphicRegistryEntry)
            if "sourceDefinitionId" in entry_dict:
                setattr(entry, ConnectorTypePrimaryKey.SOURCE.value, entry_dict["sourceDefinitionId"])
            if "destinationDefinitionId" in entry_dict:
                setattr(entry, ConnectorTypePrimaryKey.DESTINATION.value, entry_dict["destinationDefinitionId"])
            entries.append(entry)

        with (
            patch("metadata_service.registry.to_json_sanitized_dict") as mock_sanitize,
            patch("metadata_service.registry._apply_metrics_to_registry_entry") as mock_apply_metrics,
            patch("metadata_service.registry._apply_release_candidate_entries") as mock_apply_rc,
        ):
            mock_sanitize.side_effect = entry_dicts
            mock_apply_metrics.side_effect = lambda x, *args: x
            mock_apply_rc.side_effect = lambda x, *args: x

            result = _build_connector_registry(entries, {}, {})

            assert isinstance(result, ConnectorRegistryV0)
            assert len(result.sources) == expected_sources_count
            assert len(result.destinations) == expected_destinations_count

    def test_build_connector_registry_applies_metrics_and_rc(self):
        """Test that metrics and release candidates are properly applied."""
        source_entry = Mock(spec=PolymorphicRegistryEntry)
        setattr(source_entry, ConnectorTypePrimaryKey.SOURCE.value, "550e8400-e29b-41d4-a716-446655440001")

        entry_dict = {
            "sourceDefinitionId": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Test Source",
            "dockerRepository": "test/source",
            "dockerImageTag": "1.0.0",
            "documentationUrl": "https://docs.test.com",
            "spec": {},
        }

        with (
            patch("metadata_service.registry.to_json_sanitized_dict") as mock_sanitize,
            patch("metadata_service.registry._apply_metrics_to_registry_entry") as mock_apply_metrics,
            patch("metadata_service.registry._apply_release_candidate_entries") as mock_apply_rc,
        ):
            mock_sanitize.return_value = entry_dict
            mock_apply_metrics.return_value = entry_dict
            mock_apply_rc.return_value = entry_dict

            result = _build_connector_registry([source_entry], {}, {})

            mock_apply_metrics.assert_called_once()
            mock_apply_rc.assert_called_once()
            assert len(result.sources) == 1


class TestPersistRegistryToJson:
    """Tests for _persist_registry_to_json function."""

    @pytest.fixture
    def mock_registry(self):
        """Create a mock registry object."""
        registry = Mock(spec=ConnectorRegistryV0)
        registry.json.return_value = '{"sources": [], "destinations": []}'
        return registry

    @pytest.fixture
    def mock_gcs_credentials(self):
        """Mock GCS credentials environment variable."""
        return {
            "type": "service_account",
            "project_id": "test-project",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
        }

    @pytest.mark.parametrize(
        "registry_type,expected_filename,description",
        [
            ("cloud", "cloud_registry.json", "cloud registry"),
            ("oss", "oss_registry.json", "oss registry"),
        ],
    )
    def test_persist_registry_success(self, mock_registry, mock_gcs_credentials, registry_type, expected_filename, description):
        """Test successful registry persistence to GCS."""
        with (
            patch.dict(os.environ, {"GCS_DEV_CREDENTIALS": json.dumps(mock_gcs_credentials)}),
            patch("metadata_service.registry.service_account.Credentials.from_service_account_info") as mock_creds,
            patch("metadata_service.registry.storage.Client") as mock_client_class,
        ):
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_bucket = Mock()
            mock_client.bucket.return_value = mock_bucket

            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob

            _persist_registry(mock_registry, registry_type, Mock())

            mock_bucket.blob.assert_called_once_with(f"{REGISTRIES_FOLDER}/{expected_filename}")
            mock_blob.upload_from_string.assert_called_once()
