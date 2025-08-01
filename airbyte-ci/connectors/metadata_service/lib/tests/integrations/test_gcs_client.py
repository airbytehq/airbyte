#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import json
import pytest
import hashlib
import tempfile
from unittest.mock import Mock, patch
from pathlib import Path

from metadata_service.integrations.gcs_client import GCSClient


@pytest.fixture
def bucket_name():
    """Fixture providing a test bucket name."""
    return "test-bucket"


@pytest.fixture
def test_credentials():
    """Fixture providing test service account credentials."""
    return {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "test-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }


@pytest.fixture
def credentials_json(test_credentials):
    """Fixture providing test credentials as JSON string."""
    return json.dumps(test_credentials)


@pytest.fixture
def mock_gcs_dependencies():
    """Fixture providing mocked Google Cloud Storage dependencies."""
    with patch('metadata_service.integrations.gcs_client.storage.Client') as mock_storage_client, \
         patch('metadata_service.integrations.gcs_client.service_account.Credentials.from_service_account_info') as mock_creds_from_info:

        mock_credentials = Mock()
        mock_creds_from_info.return_value = mock_credentials
        mock_client = Mock()
        mock_storage_client.return_value = mock_client

        yield {
            'mock_storage_client': mock_storage_client,
            'mock_creds_from_info': mock_creds_from_info,
            'mock_credentials': mock_credentials,
            'mock_client': mock_client
        }


@pytest.fixture
def temp_file():
    """Fixture providing a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file.write("test file content for upload")
        temp_file_path = Path(temp_file.name)

    yield temp_file_path

    if temp_file_path.exists():
        temp_file_path.unlink()

class TestGCSClientBucketProperty:
    """Tests for GCSClient bucket property."""

    def test_bucket_lazy_loading(self, bucket_name, credentials_json, mock_gcs_dependencies):
        """Test that bucket property implements lazy loading correctly."""
        mock_bucket_instance = Mock()
        mock_gcs_dependencies['mock_client'].bucket.return_value = mock_bucket_instance

        client = GCSClient(bucket_name=bucket_name, gcs_credentials=credentials_json)

        # Initially, bucket should be None (not loaded yet)
        assert client._bucket is None

        # First access should create and cache the bucket
        bucket1 = client.bucket
        assert client._bucket is not None
        assert client._bucket == mock_bucket_instance
        assert bucket1 == mock_bucket_instance
        mock_gcs_dependencies['mock_client'].bucket.assert_called_once_with(bucket_name)

        # Second access should return the cached instance without calling bucket() again
        bucket2 = client.bucket
        assert bucket2 == bucket1
        assert bucket2 == mock_bucket_instance
        # bucket() should still only have been called once
        mock_gcs_dependencies['mock_client'].bucket.assert_called_once_with(bucket_name)


class TestGCSClientGetBlobMD5:
    """Tests for GCSClient get_blob_md5 method."""

    def test_get_blob_md5_existing_blob(self, bucket_name, credentials_json, mock_gcs_dependencies):
        """Test get_blob_md5 returns correct hash when blob exists."""
        client = GCSClient(bucket_name=bucket_name, gcs_credentials=credentials_json)

        # Generate expected MD5 hash for test data
        test_content = "test blob content for md5 calculation"
        expected_md5 = hashlib.md5(test_content.encode()).hexdigest()

        mock_bucket_instance = Mock()
        mock_gcs_dependencies['mock_client'].bucket.return_value = mock_bucket_instance

        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.md5_hash = expected_md5
        mock_bucket_instance.blob.return_value = mock_blob

        blob_path = "test/path/file.txt"

        result = client.get_blob_md5(blob_path)

        assert result == expected_md5
        mock_bucket_instance.blob.assert_called_once_with(blob_path)
        mock_blob.exists.assert_called_once()
        mock_blob.reload.assert_called_once()

    def test_get_blob_md5_nonexistent_blob(self, bucket_name, credentials_json, mock_gcs_dependencies):
        """Test get_blob_md5 returns None when blob doesn't exist."""
        client = GCSClient(bucket_name=bucket_name, gcs_credentials=credentials_json)

        mock_bucket_instance = Mock()
        mock_gcs_dependencies['mock_client'].bucket.return_value = mock_bucket_instance
        mock_blob = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_blob.exists.return_value = False

        blob_path = "test/path/file.txt"

        result = client.get_blob_md5(blob_path)

        assert result is None
        mock_blob.exists.assert_called_once()
        mock_blob.reload.assert_not_called()  # Should not reload if blob doesn't exist


class TestGCSClientUploadFile:
    """Tests for GCSClient upload_file method."""

    def test_upload_file_success(self, bucket_name, credentials_json, mock_gcs_dependencies, temp_file):
        """Test upload_file successfully uploads when file exists."""
        client = GCSClient(bucket_name=bucket_name, gcs_credentials=credentials_json)

        mock_bucket_instance = Mock()
        mock_gcs_dependencies['mock_client'].bucket.return_value = mock_bucket_instance

        mock_blob = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_blob.exists.return_value = False  # New file, doesn't exist yet

        blob_path = "test/path/file.txt"

        result = client.upload_file(temp_file, blob_path)

        assert result is True
        mock_bucket_instance.blob.assert_called_once_with(blob_path)
        mock_blob.upload_from_filename.assert_called_once_with(temp_file)

    def test_upload_file_skip_existing_no_overwrite(self, bucket_name, credentials_json, mock_gcs_dependencies, temp_file):
        """Test upload_file skips upload when overwrite=False and blob exists."""
        client = GCSClient(bucket_name=bucket_name, gcs_credentials=credentials_json)

        mock_bucket_instance = Mock()
        mock_gcs_dependencies['mock_client'].bucket.return_value = mock_bucket_instance

        mock_blob = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_blob.exists.return_value = True  # Blob already exists

        blob_path = "test/path/existing-file.txt"

        result = client.upload_file(temp_file, blob_path, overwrite=False)

        assert result is False
        mock_blob.exists.assert_called_once()
        mock_blob.upload_from_filename.assert_not_called()

    def test_upload_file_local_file_not_found(self, bucket_name, credentials_json, mock_gcs_dependencies):
        """Test upload_file raises FileNotFoundError when local file doesn't exist."""
        client = GCSClient(bucket_name=bucket_name, gcs_credentials=credentials_json)
        nonexistent_file = Path("/tmp/nonexistent_file.txt")
        blob_path = "test/path/file.txt"

        with pytest.raises(FileNotFoundError, match=f"Local file not found: {nonexistent_file}"):
            client.upload_file(nonexistent_file, blob_path)


class TestGCSClientUploadFileIfChanged:
    """Tests for GCSClient upload_file_if_changed method."""

    @patch('metadata_service.integrations.gcs_client.compute_gcs_md5')
    def test_upload_file_if_changed_file_changed(self, mock_compute_md5, bucket_name, credentials_json, mock_gcs_dependencies, temp_file):
        """Test upload_file_if_changed uploads when local and remote MD5 differ."""
        client = GCSClient(bucket_name=bucket_name, gcs_credentials=credentials_json)

        mock_bucket_instance = Mock()
        mock_gcs_dependencies['mock_client'].bucket.return_value = mock_bucket_instance

        # Mock local file MD5
        local_md5 = "abc123def456"
        mock_compute_md5.return_value = local_md5

        # Mock remote blob with different MD5
        mock_blob = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.md5_hash = "different_md5_hash"
        mock_blob.id = "gs://test-bucket/test/path/file.txt"

        blob_path = "test/path/file.txt"

        result = client.upload_file_if_changed(temp_file, blob_path)

        assert result.uploaded is True
        assert result.blob_id == mock_blob.id
        mock_compute_md5.assert_called_once_with(temp_file)
        mock_blob.upload_from_filename.assert_called_once_with(temp_file)

    @patch('metadata_service.integrations.gcs_client.compute_gcs_md5')
    def test_upload_file_if_changed_file_unchanged(self, mock_compute_md5, bucket_name, credentials_json, mock_gcs_dependencies, temp_file):
        """Test upload_file_if_changed skips upload when local and remote MD5 match."""
        client = GCSClient(bucket_name=bucket_name, gcs_credentials=credentials_json)

        mock_bucket_instance = Mock()
        mock_gcs_dependencies['mock_client'].bucket.return_value = mock_bucket_instance

        # Mock local file MD5
        same_md5 = "abc123def456"
        mock_compute_md5.return_value = same_md5

        # Mock remote blob with same MD5
        mock_blob = Mock()
        mock_bucket_instance.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.md5_hash = same_md5  # Same as local
        mock_blob.id = "gs://test-bucket/test/path/file.txt"

        blob_path = "test/path/file.txt"

        result = client.upload_file_if_changed(temp_file, blob_path)

        assert result.uploaded is False
        assert result.blob_id == mock_blob.id
        mock_compute_md5.assert_called_once_with(temp_file)
        mock_blob.upload_from_filename.assert_not_called()
