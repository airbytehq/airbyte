# Weaviate Migration Guide

## Upgrading to 0.3.0

This version moves the connector from version 3 to version 4 of the Weaviate Python client. Version 4 writes and deletes objects over gRPC, so Airbyte now needs to reach the cluster's gRPC port in addition to its HTTP endpoint.

- **Weaviate Cloud**: no action needed. The connector derives the gRPC endpoint (`grpc-<cluster host>:443`).
- **Self-hosted Weaviate**: make sure the gRPC port (`50051` by default) is reachable from Airbyte. If it is exposed on another host or port, for example behind an ingress, set **Connection Options > gRPC Endpoint** to its `host:port`, and **gRPC TLS** if its TLS setting differs from the public endpoint.
- The minimum supported Weaviate version is now 1.27.0.

## Upgrading to 0.2.0

This version adds several new features like flexible embedding options, overwrite and append+dedup sync modes. When upgrading from prior versions on this connector, a one-time migration of existing connections is required. This is done to align the behavior of vector database destinations in Airbyte. The following changes are included:

### Changed configuration object structure

Due to a change of the configuration structure, it's necessary to reconfigure existing destinations with the same information (e.g. credentials).

### Auto-generated ids

It's no longer possible to configure `id` fields in the destination. Instead, the destination will generate a UUID for each Weaviate object. The `id` for each record is stored in the `_ab_record_id` property and can be used to identify Weaviate objects by Airbyte record.

### Vector fields

It's not possible anymore to configure separate vector fields per stream. To load embedding vectors from the records itself, the embedding method `From Field` can be used and configured with a single field name that has to be available in records from all streams. If your records contain multiple vector fields, you need to configure separate destinations and connections to configure separate vector field names.
