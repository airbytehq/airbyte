# Changelog

All notable changes to the ClickHouse source connector will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.8] - 2025-09-26

### Added
- Custom `ClickHouseSourceOperations` class for improved array handling
- Comprehensive error handling with fallback mechanisms for array processing
- Enhanced documentation for implementation details

### Changed
- **BREAKING (Internal)**: Upgraded ClickHouse JDBC driver from `0.3.2-patch11` to `0.6.3`
- Replaced default JDBC source operations with custom implementation
- Updated array handling to use `getArray()` instead of deprecated `getResultSet()` method

### Fixed
- **Critical**: Resolved `SQLFeatureNotSupportedException: getResultSet not implemented` error when processing ClickHouse array types
- Array data processing now works correctly with ClickHouse JDBC driver v0.6.3+
- Improved robustness of array data extraction with proper null handling

### Technical Details
- **JDBC Driver**: `0.3.2-patch11` → `0.6.3`
- **New Classes**: `io.airbyte.integrations.source.clickhouse.ClickHouseSourceOperations`
- **Modified Classes**: `io.airbyte.integrations.source.clickhouse.ClickHouseSource`
- **Backward Compatibility**: Full backward compatibility maintained for end users
- **Performance**: Direct array access improves processing efficiency

## [0.2.6] - 2025-09-25

### Changed
- Reverted JDBC driver upgrade due to compatibility issues

## [0.2.5] - 2025-09-17

### Changed
- Upgraded ClickHouse JDBC driver from 0.3.2-patch10 to 0.9.0 (later reverted)

## [0.2.4] - 2025-07-10

### Changed
- Converted to new gradle build flow

## [0.2.3] - 2024-12-18

### Changed
- Updated to use base image: `airbyte/java-connector-base:1.0.0`

## [0.2.2] - 2024-02-13

### Changed
- Adopted CDK 0.20.4

## [0.2.1] - 2024-01-24

### Changed
- Bumped CDK version

## [0.1.17] - 2023-03-22

### Changed
- Removed redundant date-time datatypes formatting

## [0.1.16] - 2023-03-06

### Added
- Network isolation: source connector accepts a list of hosts it is allowed to connect to

## [0.1.15] - 2022-12-14

### Changed
- Consolidated date/time values mapping for JDBC sources

## [0.1.14] - 2022-09-27

### Added
- Custom JDBC URL parameters field

## [0.1.13] - 2022-09-01

### Changed
- Emit state messages more frequently

## [0.1.12] - 2022-08-18

### Changed
- DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field

## [0.1.10] - 2022-04-12

### Security
- Bumped mina-sshd from 2.7.0 to 2.8.0

## [0.1.9] - 2022-02-09

### Fixed
- Exception in case `password` field is not provided

## [0.1.8] - 2022-02-14

### Added
- `-XX:+ExitOnOutOfMemoryError` JVM option

## [0.1.7] - 2021-12-24

### Added
- Support for JdbcType.ARRAY

## [0.1.6] - 2021-12-15

### Changed
- Updated titles and descriptions

## [0.1.5] - 2021-12-01

### Fixed
- Incorrect handling of "\n" in SSH key

## [0.1.4] - 2021-10-20

### Added
- Support for connection via SSH tunnel (aka Bastion server)

## [0.1.3] - 2021-10-20

### Added
- SSL connections support

## [0.1.2] - 2021-08-13

### Added
- JSON config validator