#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import os
from unittest.mock import Mock, patch

import pytest
import yaml
from google.cloud import storage
from google.oauth2 import service_account

from metadata_service.constants import REGISTRIES_FOLDER, SPECS_SECRETS_MASK_FILE_NAME, VALID_REGISTRIES
from metadata_service.models.generated import ConnectorRegistryV0
from metadata_service.registry import PolymorphicRegistryEntry
from metadata_service.specs_secrets_mask import _get_registries_from_gcs, _get_specs_secrets_from_registry_entries, _persist_secrets_to_gcs


class TestGetRegistriesFromGcs:
    """Tests for _get_registries_from_gcs function."""

    @pytest.fixture
    def mock_bucket(self):
        """Create a mock GCS bucket."""
        return Mock(spec=storage.Bucket)

    @pytest.fixture
    def valid_registry_data(self):
        """Sample valid registry data."""
        return {
            "sources": [],
            "destinations": [],
        }

    @pytest.fixture
    def mock_blob(self):
        """Create a mock GCS blob."""
        return Mock(spec=storage.Blob)

    def test_get_registries_from_gcs_success(self, mock_bucket, mock_blob, valid_registry_data):
        """Test successful retrieval of all valid registries from GCS."""
        mock_bucket.blob.return_value = mock_blob

        with (
            patch("metadata_service.specs_secrets_mask.safe_read_gcs_file") as mock_safe_read,
            patch("metadata_service.specs_secrets_mask.ConnectorRegistryV0.parse_obj") as mock_parse,
        ):
            mock_safe_read.return_value = json.dumps(valid_registry_data)
            mock_registry = Mock(spec=ConnectorRegistryV0)
            mock_parse.return_value = mock_registry

            result = _get_registries_from_gcs(mock_bucket)

            assert len(result) == len(VALID_REGISTRIES)
            assert all(registry == mock_registry for registry in result)

            expected_calls = [f"{REGISTRIES_FOLDER}/{registry}_registry.json" for registry in VALID_REGISTRIES]
            actual_calls = [call[0][0] for call in mock_bucket.blob.call_args_list]
            assert actual_calls == expected_calls

            assert mock_safe_read.call_count == len(VALID_REGISTRIES)

    def test_get_registries_from_gcs_multiple_registries(self, mock_bucket, mock_blob, valid_registry_data):
        """Test that the function correctly processes all registries in VALID_REGISTRIES."""
        mock_bucket.blob.return_value = mock_blob

        with (
            patch("metadata_service.specs_secrets_mask.safe_read_gcs_file") as mock_safe_read,
            patch("metadata_service.specs_secrets_mask.ConnectorRegistryV0.parse_obj") as mock_parse,
        ):
            mock_safe_read.return_value = json.dumps(valid_registry_data)
            mock_registry = Mock(spec=ConnectorRegistryV0)
            mock_parse.return_value = mock_registry

            result = _get_registries_from_gcs(mock_bucket)

            assert len(result) == 2
            assert mock_parse.call_count == 2
            assert mock_safe_read.call_count == 2


class TestGetSpecsSecretsFromRegistryEntries:
    """Tests for _get_specs_secrets_from_registry_entries function."""

    @pytest.fixture
    def mock_registry_entry(self):
        """Create a mock registry entry."""
        return Mock(spec=PolymorphicRegistryEntry)

    @pytest.fixture
    def single_secret_entry_data(self):
        """Sample entry data with a single secret property."""
        return {
            "spec": {
                "connectionSpecification": {
                    "properties": {
                        "password": {"type": "string", "airbyte_secret": True},
                        "username": {"type": "string", "airbyte_secret": False},
                    }
                }
            }
        }

    @pytest.fixture
    def multiple_secrets_entry_data(self):
        """Sample entry data with multiple secret properties."""
        return {
            "spec": {
                "connectionSpecification": {
                    "properties": {
                        "password": {"type": "string", "airbyte_secret": True},
                        "api_key": {"type": "string", "airbyte_secret": True},
                        "username": {"type": "string", "airbyte_secret": False},
                    }
                }
            }
        }

    @pytest.fixture
    def nested_secrets_entry_data(self):
        """Sample entry data with nested secret properties."""
        return {
            "spec": {
                "connectionSpecification": {
                    "properties": {
                        "oauth": {
                            "type": "object",
                            "properties": {
                                "client_secret": {"type": "string", "airbyte_secret": True},
                                "client_id": {"type": "string", "airbyte_secret": False},
                            },
                        },
                        "username": {"type": "string", "airbyte_secret": False},
                    }
                }
            }
        }

    @pytest.fixture
    def deeply_nested_secrets_entry_data(self):
        """Sample entry data with deeply nested secret properties."""
        return {
            "spec": {
                "connectionSpecification": {
                    "properties": {
                        "connection": {
                            "type": "object",
                            "properties": {
                                "auth": {
                                    "type": "object",
                                    "properties": {
                                        "credentials": {
                                            "type": "object",
                                            "properties": {"secret_token": {"type": "string", "airbyte_secret": True}},
                                        }
                                    },
                                }
                            },
                        }
                    }
                }
            }
        }

    @pytest.fixture
    def no_secrets_entry_data(self):
        """Sample entry data with no secret properties."""
        return {
            "spec": {
                "connectionSpecification": {
                    "properties": {"username": {"type": "string", "airbyte_secret": False}, "host": {"type": "string"}}
                }
            }
        }

    @pytest.mark.parametrize(
        "entry_data_fixture,expected_secrets,description",
        [
            ("single_secret_entry_data", {"password"}, "single secret property"),
            ("multiple_secrets_entry_data", {"password", "api_key"}, "multiple secret properties"),
            ("nested_secrets_entry_data", {"client_secret"}, "nested secret property"),
            ("deeply_nested_secrets_entry_data", {"secret_token"}, "deeply nested secret property"),
            ("no_secrets_entry_data", set(), "no secret properties"),
        ],
    )
    def test_get_specs_secrets_valid_structures(self, mock_registry_entry, entry_data_fixture, expected_secrets, description, request):
        """Test extraction from various valid entry structures."""
        entry_data = request.getfixturevalue(entry_data_fixture)

        with patch("metadata_service.specs_secrets_mask.to_json_sanitized_dict") as mock_sanitize:
            mock_sanitize.return_value = entry_data

            result = _get_specs_secrets_from_registry_entries([mock_registry_entry])

            assert result == expected_secrets, f"Failed for {description}"
            mock_sanitize.assert_called_once_with(mock_registry_entry)

    def test_get_specs_secrets_multiple_entries_aggregation(self, mock_registry_entry, single_secret_entry_data, nested_secrets_entry_data):
        """Test that secrets from multiple entries are properly aggregated."""
        entry1 = Mock(spec=PolymorphicRegistryEntry)
        entry2 = Mock(spec=PolymorphicRegistryEntry)

        with patch("metadata_service.specs_secrets_mask.to_json_sanitized_dict") as mock_sanitize:
            mock_sanitize.side_effect = [single_secret_entry_data, nested_secrets_entry_data]

            result = _get_specs_secrets_from_registry_entries([entry1, entry2])

            assert result == {"password", "client_secret"}
            assert mock_sanitize.call_count == 2

    def test_get_specs_secrets_duplicate_secrets_handling(self, single_secret_entry_data):
        """Test that duplicate secret names from different entries are handled correctly."""
        entry1 = Mock(spec=PolymorphicRegistryEntry)
        entry2 = Mock(spec=PolymorphicRegistryEntry)

        with patch("metadata_service.specs_secrets_mask.to_json_sanitized_dict") as mock_sanitize:
            mock_sanitize.return_value = single_secret_entry_data

            result = _get_specs_secrets_from_registry_entries([entry1, entry2])

            assert result == {"password"}
            assert mock_sanitize.call_count == 2

    def test_get_specs_secrets_empty_entries_list(self):
        """Test behavior with empty entries list."""
        result = _get_specs_secrets_from_registry_entries([])

        assert result == set()

    def test_get_specs_secrets_complex_real_world_structure(self, mock_registry_entry):
        """Test with realistic connector specification structure."""
        complex_entry_data = {
            "spec": {
                "connectionSpecification": {
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer"},
                        "database": {"type": "string"},
                        "credentials": {
                            "type": "object",
                            "oneOf": [
                                {
                                    "properties": {
                                        "auth_type": {"type": "string", "const": "username_password"},
                                        "username": {"type": "string"},
                                        "password": {"type": "string", "airbyte_secret": True},
                                    }
                                },
                                {
                                    "properties": {
                                        "auth_type": {"type": "string", "const": "oauth2"},
                                        "client_id": {"type": "string"},
                                        "client_secret": {"type": "string", "airbyte_secret": True},
                                        "refresh_token": {"type": "string", "airbyte_secret": True},
                                    }
                                },
                            ],
                        },
                        "ssl_config": {
                            "type": "object",
                            "properties": {"ssl_mode": {"type": "string"}, "client_key": {"type": "string", "airbyte_secret": True}},
                        },
                    }
                }
            }
        }

        with patch("metadata_service.specs_secrets_mask.to_json_sanitized_dict") as mock_sanitize:
            mock_sanitize.return_value = complex_entry_data

            result = _get_specs_secrets_from_registry_entries([mock_registry_entry])

            expected_secrets = {"password", "client_secret", "refresh_token", "client_key"}
            assert result == expected_secrets


class TestPersistSecretsToGcs:
    """Tests for _persist_secrets_to_gcs function."""

    @pytest.fixture
    def mock_bucket(self):
        """Create a mock GCS bucket."""
        return Mock(spec=storage.Bucket)

    @pytest.fixture
    def mock_blob(self):
        """Create a mock GCS blob."""
        mock_blob = Mock()
        mock_blob.name = f"{REGISTRIES_FOLDER}/{SPECS_SECRETS_MASK_FILE_NAME}"
        return mock_blob

    @pytest.fixture
    def mock_gcs_credentials(self):
        """Mock GCS credentials environment variable."""
        return {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }

    @pytest.mark.parametrize(
        "secrets_set,expected_yaml_content,description",
        [
            (set(), {"properties": []}, "empty secrets set"),
            ({"password"}, {"properties": ["password"]}, "single secret"),
            ({"password", "api_key", "token"}, {"properties": ["api_key", "password", "token"]}, "multiple secrets sorted"),
            ({"z_secret", "a_secret", "m_secret"}, {"properties": ["a_secret", "m_secret", "z_secret"]}, "secrets sorted alphabetically"),
        ],
    )
    def test_persist_secrets_to_gcs_various_secret_sets(
        self, mock_bucket, mock_blob, mock_gcs_credentials, secrets_set, expected_yaml_content, description
    ):
        """Test persistence with different secret set sizes and contents."""
        with (
            patch.dict(os.environ, {"GCS_DEV_CREDENTIALS": json.dumps(mock_gcs_credentials)}),
            patch("metadata_service.specs_secrets_mask.service_account.Credentials.from_service_account_info") as mock_creds,
            patch("metadata_service.specs_secrets_mask.storage.Client") as mock_client_class,
        ):
            mock_credentials = Mock(spec=service_account.Credentials)
            mock_creds.return_value = mock_credentials

            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_dev_bucket = Mock(spec=storage.Bucket)
            mock_client.bucket.return_value = mock_dev_bucket
            mock_dev_bucket.blob.return_value = mock_blob

            _persist_secrets_to_gcs(secrets_set, mock_bucket)

            mock_creds.assert_called_once_with(mock_gcs_credentials)
            mock_client_class.assert_called_once_with(credentials=mock_credentials)

            mock_client.bucket.assert_called_once_with("dev-airbyte-cloud-connector-metadata-service")
            mock_dev_bucket.blob.assert_called_once_with(f"{REGISTRIES_FOLDER}/{SPECS_SECRETS_MASK_FILE_NAME}")

            mock_blob.upload_from_string.assert_called_once()
            uploaded_content = mock_blob.upload_from_string.call_args[0][0]
            parsed_yaml = yaml.safe_load(uploaded_content)
            assert parsed_yaml == expected_yaml_content, f"Failed for {description}"
