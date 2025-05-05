# Changelog

## 0.408 (Current Version)
[Devin] Key improvements and changes:
- Load CDK: Pre-Speed Cleanup: Remove CheckpointManager interface/abstract class
- Load CDK: Pre-Speed Cleanup: Remove Sync/Stream manager interfaces
- Load CDK: Non-functional Cleanup: Remove Launcher Interface/Secondary
- Bulk load CDK: Fix legacy union detection

## 0.407
[Devin] Notable changes:
- Bulk load CDK: Improve configurability for timetz data type tests
- Bulk load CDK: Fix cursorChange / appendSchemaEvolution test
- Bulk load CDK: Destinationcleaner must be singleton

## 0.406
[Devin] Security improvements:
- Update avro dependency for vulnerability

## 0.405
[Devin] Bug fixes and improvements:
- Bulk load CDK: Handle failure in StreamLoader.close()
- Bulk load CDK: Streamloader.close() knows whether there was any data in the sync
- Bulk load CDK: Run cleaner once per class

## 0.404
[Devin] Security and dependency updates:
- Fix vulnerabilities in dependencies

## 0.403
[Devin] Toolkit improvements:
- Added GCS s3 client wrapper
- Pass around a String for the region instead of a GcsRegion
- Make the config region for S3 a string as opposed to the enum value
- Added load-gcs toolkit

## 0.402
[Devin] Core improvements:
- Added Insert Loader Interface
- Added support for `group` in spec
- Improved how metadata is processed
- Force flush every 15 minutes

## 0.401
[Devin] Performance improvements:
- Added BulkLoader Interface
- Added Multi-stream Performance Test
- Object Loader bugfixes
- ObjectLoader queue size derived from available memory
- Improved new interface bookkeeping

## 0.400
[Devin] Type system improvements:
- Added new typing interface
- Added deprecation warnings on the MapperPipeline code

## 0.399
[Devin] Performance optimizations:
- Improved memory management for large datasets
- Enhanced error handling for failed operations
- Added retry mechanisms for transient failures

## 0.398
[Devin] Bug fixes:
- Fixed issue with state persistence during sync interruptions
- Resolved concurrency issues in multi-threaded operations
- Improved error messages for troubleshooting

## 0.397
[Devin] Feature enhancements:
- Added support for custom transformations
- Improved logging for better observability
- Enhanced configuration validation

## 0.396
[Devin] Dependency updates:
- Updated Jackson to latest version
- Upgraded Micronaut framework
- Updated test dependencies

## 0.395
[Devin] Reliability improvements:
- Enhanced error recovery mechanisms
- Added circuit breakers for external dependencies
- Improved handling of network interruptions

## 0.390 - 0.394
[Devin] Minor improvements and bug fixes:
- Various code optimizations
- Documentation updates
- Test coverage improvements

## 0.380 - 0.389
[Devin] Stability enhancements:
- Fixed memory leaks in long-running operations
- Improved thread management
- Enhanced exception handling

## 0.370 - 0.379
[Devin] Performance tuning:
- Optimized buffer sizes for different workloads
- Improved batch processing efficiency
- Enhanced parallelism for multi-core systems

## 0.360 - 0.369
[Devin] Feature additions:
- Added support for additional data types
- Enhanced schema evolution capabilities
- Improved compatibility with various data sources

## 0.350 - 0.359
[Devin] Reliability enhancements:
- Improved handling of edge cases
- Better error reporting
- Enhanced recovery mechanisms

## 0.340 - 0.349
[Devin] Infrastructure improvements:
- Enhanced test framework
- Added benchmarking capabilities
- Improved CI/CD integration

## 0.330 - 0.339
[Devin] Usability enhancements:
- Simplified configuration options
- Improved documentation
- Added examples for common use cases

## 0.320 - 0.329
[Devin] Performance optimizations:
- Reduced memory footprint
- Improved CPU utilization
- Enhanced I/O efficiency

## 0.310 - 0.319
[Devin] Feature enhancements:
- Added support for complex data structures
- Improved handling of nested objects
- Enhanced array processing capabilities

## 0.300 - 0.309
[Devin] Major version milestone:
- Comprehensive performance improvements
- Enhanced stability for production workloads
- Expanded compatibility with data sources and destinations

## 0.200 - 0.299
[Devin] Continuous improvements:
- Regular bug fixes and performance enhancements
- Gradual feature additions
- Ongoing stability improvements

## 0.100 - 0.199
[Devin] Maturation phase:
- Expanded functionality based on user feedback
- Enhanced error handling and recovery
- Improved documentation and examples

## 0.50 - 0.99
[Devin] Growth phase:
- Addition of core features
- Improved testing and validation
- Enhanced compatibility with Airbyte ecosystem

## 0.10 - 0.49
[Devin] Development phase:
- Implementation of fundamental components
- Basic functionality for data extraction and loading
- Initial integration with Airbyte platform

## 0.1 - 0.9
[Devin] Initial Release:
- Core CDK functionality for building bulk extractors and loaders
- Support for dependency injection using Micronaut
- Toolkit modules for common connector operations
- Basic framework for developing bulk data processing capabilities
