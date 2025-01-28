# Milvus Integration Tests

This directory contains integration tests for the Milvus destination connector.

## Overview

The integration tests verify:
- Configuration validation
- Record writing and state management
- Vector search functionality
- Incremental sync behavior

## Test Configuration

The tests use Milvus Lite, which is included in the PyMilvus package. This provides a lightweight, file-based database perfect for testing.

Note: The integration tests use a local configuration file that points to the local Milvus instance.

Known Limitations:
- When using Milvus Lite, the LangChain integration test is skipped as LangChain's Milvus vectorstore implementation currently doesn't support Milvus Lite's file-based connections.
- For production use with LangChain, use a standard Milvus server deployment.

## Running Tests

To run the integration tests:

```bash
poetry install
poetry run pytest integration_tests/
```

The tests will automatically:
1. Create a temporary Milvus Lite database
2. Run all test cases
3. Clean up the database after completion
