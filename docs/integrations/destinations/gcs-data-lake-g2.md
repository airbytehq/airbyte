# GCS Data Lake (Experimental, Gen 2)

This is a private, experimental version of the [GCS Data Lake destination](https://docs.airbyte.com/integrations/destinations/gcs-data-lake).

The Gen 2 connector writes declared nested objects as typed Iceberg `struct` columns, and arrays of objects as `list<struct>`. All nested fields are nullable. Undeclared nested keys are dropped. Schemaless objects, unions, and unknown types are still written as JSON strings.

For configuration options, see the [GCS Data Lake documentation](https://docs.airbyte.com/integrations/destinations/gcs-data-lake).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject |
|:--------|:-----------|:-------------|:--------|
| 0.1.0 | 2026-10-22 | [89664](https://github.com/airbytehq/airbyte/pull/89664) | Initial experimental release with typed Iceberg structs |

</details>
