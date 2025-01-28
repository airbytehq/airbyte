# S3 Data Lake

:::danger

This connector is in early access, and SHOULD NOT be used for production workloads.
This connector is subject to breaking changes **without notice**.

We're interested in hearing about your experience! See [Github](https://github.com/airbytehq/airbyte/discussions/50404)
for more information.

:::

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                      |
|:--------|:-----------|:-----------------------------------------------------------|:-----------------------------------------------------------------------------|
| 0.2.24 | 2025-01-28 | [52605](https://github.com/airbytehq/airbyte/pull/52605) | [s3-data-lake] Adding support for the Dremio (-Nessie) catalog |
| 0.2.23  | 2025-01-27 | [\#51600](https://github.com/airbytehq/airbyte/pull/51600) | Internal refactor                                                            |
| 0.2.22  | 2025-01-22 | [\#52081](https://github.com/airbytehq/airbyte/pull/52081) | Implement support for REST catalog                                           |
| 0.2.21  | 2025-01-27 | [\#52564](https://github.com/airbytehq/airbyte/pull/52564) | Fix crash on stream with 0 records                                           |
| 0.2.20  | 2025-01-23 | [\#52068](https://github.com/airbytehq/airbyte/pull/52068) | Add support for default namespace (/database name)                           |
| 0.2.19  | 2025-01-16 | [\#51595](https://github.com/airbytehq/airbyte/pull/51595) | Clarifications in connector config options                                   |
| 0.2.18  | 2025-01-15 | [\#51042](https://github.com/airbytehq/airbyte/pull/51042) | Write structs as JSON strings instead of Iceberg structs.                    |
| 0.2.17  | 2025-01-14 | [\#51542](https://github.com/airbytehq/airbyte/pull/51542) | New identifier fields should be marked as required.                          |
| 0.2.16  | 2025-01-14 | [\#51538](https://github.com/airbytehq/airbyte/pull/51538) | Update identifier fields if incoming fields are different than existing ones |
| 0.2.15  | 2025-01-14 | [\#51530](https://github.com/airbytehq/airbyte/pull/51530) | Set AWS region for S3 bucket for nessie catalog                              |
| 0.2.14  | 2025-01-14 | [\#50413](https://github.com/airbytehq/airbyte/pull/50413) | Update existing table schema based on the incoming schema                    |
| 0.2.13  | 2025-01-14 | [\#50412](https://github.com/airbytehq/airbyte/pull/50412) | Implement logic to determine super types between iceberg types               |
| 0.2.12  | 2025-01-10 | [\#50876](https://github.com/airbytehq/airbyte/pull/50876) | Add support for AWS instance profile auth                                    |
| 0.2.11  | 2025-01-10 | [\#50971](https://github.com/airbytehq/airbyte/pull/50971) | Internal refactor in AWS auth flow                                           |
| 0.2.10  | 2025-01-09 | [\#50400](https://github.com/airbytehq/airbyte/pull/50400) | Add S3DataLakeTypesComparator                                                |
| 0.2.9   | 2025-01-09 | [\#51022](https://github.com/airbytehq/airbyte/pull/51022) | Rename all classes and files from Iceberg V2                                 |
| 0.2.8   | 2025-01-09 | [\#51012](https://github.com/airbytehq/airbyte/pull/51012) | Rename/Cleanup package from Iceberg V2                                       |
| 0.2.7   | 2025-01-09 | [\#50957](https://github.com/airbytehq/airbyte/pull/50957) | Add support for GLUE RBAC (Assume role)                                      |
| 0.2.6   | 2025-01-08 | [\#50991](https://github.com/airbytehq/airbyte/pull/50991) | Initial public release.                                                      |

</details>
