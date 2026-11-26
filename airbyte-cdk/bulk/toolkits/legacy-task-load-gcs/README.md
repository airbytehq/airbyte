# legacy-task-load-gcs

> **DEPRECATED**: This toolkit is for legacy (non-dataflow) GCS connectors only.

This toolkit contains GCS-specific loading infrastructure for connectors that use the legacy task-based architecture. It provides GCS client wrappers and upload utilities that predate the modern dataflow pipeline.

## Do Not Use For New Connectors

New GCS connectors should use `core-load` with the dataflow pipeline, using `load-gcp` for GCP credentials only. This toolkit should only be used and updated for the existing connectors that depend on it.

## Connectors Using This Toolkit

- destination-bigquery
- destination-gcs

## Configuration

To use this toolkit, add it to your connector's toolkits list along with `useLegacyTaskLoader`:

```groovy
airbyteBulkConnector {
    core = 'load'
    toolkits = ['legacy-task-load-gcs']
    useLegacyTaskLoader = true
}
```

## Contents

- GCS client wrappers
- GCS upload/download utilities
- GCS-specific configuration handling

## Authentication

`GcsClientFactory` picks the client from `GcsClientConfiguration.credential`:

| Configuration | Client | API |
| :--- | :--- | :--- |
| `GcsHmacKeyConfiguration` | `GcsS3Client` | S3-compatible XML API (`storage.googleapis.com`) |
| `GcsWorkloadIdentityFederationConfiguration` | `GcsNativeClient` | GCS JSON API |

Workload Identity Federation takes the contents of an `external_account` credential configuration file. Build it with `GcsWorkloadIdentityFederationConfiguration.fromCredentialsJson`, which validates the document without network access. The token exchange needs `sts.googleapis.com`, and service account impersonation also needs `iamcredentials.googleapis.com`, so add them to the connector's `allowedHosts`.

`GcsAuthSpecification` (the spec-side `credential` dropdown) only offers HMAC keys. A connector that offers WIF declares its own credential spec and maps it onto `GcsWorkloadIdentityFederationConfiguration`.

All clients take full object keys (already including the bucket path) and never prepend `GcsClientConfiguration.path`.

## Migration Path

Connectors should migrate to the modern dataflow pipeline when possible. For GCP credentials, use `load-gcp` instead. The dataflow architecture provides better performance, cleaner separation of concerns, and is the actively maintained code path.