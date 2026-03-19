# Changelog

All notable changes to the Kafka Destination Connector will be documented in this file.

## [0.2.0] - 2024-03-19

### Added
- **Partition Routing Feature**: Added configurable partition key support for deterministic routing of related records to the same Kafka partition
- **New Configuration Parameter**: `partition_key_field` - allows users to specify field(s) from record data as Kafka message key
- **Field Support**: 
  - Single field partitioning (e.g., `"user_id"`)
  - Multiple field partitioning with delimiter (e.g., `"user_id,order_id"`)
  - Nested field partitioning using dot notation (e.g., `"user.id"`)
  - Mixed field types (e.g., `"user_id,user.email,order.date"`)
- **Backward Compatibility**: Existing configurations continue to work with random UUID keys when `partition_key_field` is not specified
- **Robust Error Handling**: Graceful fallback to UUID for missing/null fields

### Technical Changes
- Added `PartitionKeyExtractor` utility class for extracting and processing partition keys from JSON record data
- Updated `KafkaDestinationConfig` to handle new `partition_key_field` parameter
- Modified `KafkaRecordConsumer` to use partition keys instead of random UUIDs when configured
- Enhanced connector specification (`spec.json`) with new configuration parameter
- Added comprehensive unit tests (17 test cases) for partition key extraction
- Added integration tests (5 scenarios) for partition routing behavior verification

### Documentation
- Updated README.md with partition routing feature documentation and examples
- Created comprehensive configuration examples in `PARTITION_ROUTING_EXAMPLES.md`
- Added inline code documentation for all new functionality

### Benefits
- **Deterministic Partitioning**: Related records (same user, order, etc.) now go to the same partition
- **Ordering Guarantees**: Maintains record order within partitions for related data
- **Flexible Configuration**: Support for various field types and combinations
- **Production Ready**: Full test coverage and error handling

### Migration Notes
- No breaking changes - existing configurations continue to work unchanged
- To enable partition routing, add `partition_key_field` to your connector configuration
- Example: `"partition_key_field": "user_id"` will route all records with the same `user_id` to the same partition

## [0.1.11] - Previous Release

### Previous Features
- Basic Kafka destination functionality with random UUID partitioning
- Support for various Kafka protocols (PLAINTEXT, SASL_PLAINTEXT, SASL_SSL)
- Configurable producer settings (batch size, compression, retries, etc.)
- Topic pattern support with namespace and stream variables
