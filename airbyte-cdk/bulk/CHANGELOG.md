# Changelog

## 0.X (Current Version)
[Devin] Key improvements and changes:
- Load CDK: Pre-Speed Cleanup: Remove CheckpointManager interface/abstract class
- Load CDK: Pre-Speed Cleanup: Remove Sync/Stream manager interfaces
- Load CDK: Non-functional Cleanup: Remove Launcher Interface/Secondary
- Bulk load CDK: Fix legacy union detection

## 0.X-1
[Devin] Notable changes:
- Bulk load CDK: Improve configurability for timetz data type tests
- Bulk load CDK: Fix cursorChange / appendSchemaEvolution test
- Bulk load CDK: Destinationcleaner must be singleton

## 0.X-2
[Devin] Security improvements:
- Update avro dependency for vulnerability

## 0.X-3
[Devin] Bug fixes and improvements:
- Bulk load CDK: Handle failure in StreamLoader.close()
- Bulk load CDK: Streamloader.close() knows whether there was any data in the sync
- Bulk load CDK: Run cleaner once per class

## 0.X-4
[Devin] Security and dependency updates:
- Fix vulnerabilities in dependencies

## 0.X-5
[Devin] Toolkit improvements:
- Added GCS s3 client wrapper
- Pass around a String for the region instead of a GcsRegion
- Make the config region for S3 a string as opposed to the enum value
- Added load-gcs toolkit

## 0.X-6
[Devin] Core improvements:
- Added Insert Loader Interface
- Added support for `group` in spec
- Improved how metadata is processed
- Force flush every 15 minutes

## 0.X-7
[Devin] Performance improvements:
- Added BulkLoader Interface
- Added Multi-stream Performance Test
- Object Loader bugfixes
- ObjectLoader queue size derived from available memory
- Improved new interface bookkeeping

## 0.X-8
[Devin] Type system improvements:
- Added new typing interface
- Added deprecation warnings on the MapperPipeline code

## 0.X-9
[Devin] Initial Release:
- Core CDK functionality for building bulk extractors and loaders
- Support for dependency injection using Micronaut
- Toolkit modules for common connector operations
