# Weaviate Migration Guide

## Upgrading to 0.2.0

This version adds several new features like flexible embedding options, overwrite and append+dedup sync modes , but also contains multiple changes that require a migration of existing connections. This is done to align the behavior of vector database destinations in Airbyte. The following changes are included:

### Changed configuration object structure

Due to a change of the configuration structure, it's necessary to reconfigure existing destinations with the same information (e.g. credentials).

### Configurable object class

Instead of creating separate object classes per stream, it's now possible to configure a single object class for all streams. This is configured via the `Class name` field in the configuration. If your downstream processing relies on the old behavior, you can configure the class name to be the same as the stream name. In case you are loading multiple streams via a single destination, you need to configure separate destinations and connections for each object class.

### Auto-generated ids

It's not possible anymore to configure id fields in the destination. Instead, the destination will generate a UUID for each Weaviate object. The id per record is stored in the `_ab_record_id` property and can be used to identify Weaviate objects by Airbyte record.

### Vector fields

It's not possible anymore to configure separate vector fields per stream. To load embedding vectors from the records itself, the embedding method `From Field` can be used and configured with a single field name that has to be available in all records. If your records contain multiple vector fields, you need to configure separate destinations and connections to configure separate vector field names.

