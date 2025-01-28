# Integration Tests for Destination Milvus

This directory contains integration tests for the Milvus destination connector. The tests verify the connector's ability to:
- Connect to a local Milvus instance
- Write records in different sync modes (overwrite, append, append_dedup)
- Handle vector operations and similarity search
- Validate configurations

## Prerequisites

- Docker installed and running
- Default ports available:
  - 19530 (Milvus)
  - 2379 (etcd)
  - 9091 (WebUI)

## Test Configuration

The tests use a local configuration file (`secrets/config.json`) that points to a local Milvus instance. The configuration includes:
- Text and metadata field settings
- Fake embeddings for testing
- Local Milvus connection details

## Running Tests

The test suite automatically manages a local Milvus container using the provided `standalone_embed.sh` script:

1. Start the tests:
   ```bash
   poetry run pytest -s integration_tests
   ```

2. The test suite will:
   - Start a local Milvus instance using standalone_embed.sh
   - Run the integration tests
   - Clean up the Milvus container and volumes

## Test Structure

- `milvus_integration_test.py`: Main test file extending BaseIntegrationTest
- `standalone_embed.sh`: Script for managing local Milvus instance
- `secrets/config.json`: Test configuration file
- `.gitignore`: Ignores test artifacts and volumes

## Adding New Tests

When adding new tests:
1. Extend the existing test class `MilvusIntegrationTest`
2. Use the provided fixture methods for setup/teardown
3. Follow the existing patterns for sync mode testing
4. Clean up resources in tearDown
