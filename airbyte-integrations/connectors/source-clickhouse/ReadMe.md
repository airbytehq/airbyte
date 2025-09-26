# ClickHouse Source Connector

## Overview

This connector provides integration between ClickHouse databases and Airbyte, supporting both Full Refresh and Incremental sync modes.

## Key Features

- **JDBC Driver**: Uses ClickHouse JDBC driver v0.6.3 with custom array handling
- **Array Support**: Custom implementation for handling ClickHouse array types without relying on deprecated JDBC methods
- **SSL Support**: Full SSL connection support
- **SSH Tunneling**: Connection via SSH tunnels for secure access
- **Incremental Sync**: Support for incremental data synchronization

## Implementation Details

### Custom Array Handling

This connector includes a custom `ClickHouseSourceOperations` class that extends the standard JDBC operations to properly handle ClickHouse array data types. The implementation:

- Uses `Array.getArray()` instead of the deprecated `getResultSet()` method
- Provides graceful fallback to string representation for unsupported array types
- Maintains compatibility with the latest ClickHouse JDBC driver (0.6.3)

### Integration tests

For ssl test custom image is used. To push it run this command under the tools\integration-tests-ssl dir:
_docker build -t your_user/clickhouse-with-ssl:dev -f Clickhouse.Dockerfile ._

