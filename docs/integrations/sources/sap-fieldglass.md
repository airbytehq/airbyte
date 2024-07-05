# SAP Fieldglass

This page contains the setup guide and reference information for the SAP Fieldglass Active Worker Download source connector built in `low-code cdk`.

## Prerequisites

- A [Fieldglass Account](https://www.fieldglass.net/)
- An [api key from SAP](https://api.sap.com/)

## Supported sync modes

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Supported Streams

- [Active Worker Download](https://api.sap.com/api/activeWorkerDownload/resource)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                    | Subject                                     |
| :------ | :--------- | :---------------------------------------------- |:--------------------------------------------|
| 0.1.3 | 2024-06-04 | [39021](https://github.com/airbytehq/airbyte/pull/39021) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-05-28 | [38689](https://github.com/airbytehq/airbyte/pull/38689) | Make connector compatible with Builder |
| 0.1.1 | 2024-05-20 | [38384](https://github.com/airbytehq/airbyte/pull/38384) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-22 | https://github.com/airbytehq/airbyte/pull/18656 | Initial commit                              |

</details>