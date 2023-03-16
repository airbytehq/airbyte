# National Vulnerability Database

This page contains the setup guide and reference information for the National Vulnerability Database (NVD) source connector.

## Prerequisites

NVD doesn't strictly require an API key to access their API.
However, without an API key, the number of requests you can make is very limited.
It is recommended to [request an API key](https://nvd.nist.gov/developers/request-an-api-key) to prevent being rate limited.

## Setup guide

1. Navigate to the Airbyte dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select NVD from the **Source type** dropdown.
4. Enter a name for the NVD connector.
5. Enter the start date from which to gather data in the following format: `%Y-%m-%dT%H:%M:%S`, for example, `2022-01-01T00:00:00`. This date is interpreted as being in the UTC timezone.
6. Optionally, fill in your API key (recommended).

## Supported sync modes
​
The NVD source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature | Support | Notes |
| :--- | :---: | :--- |
| Full Refresh Sync | ✅ | Not recommended due to large number of API requests |
| Incremental - Append Sync | ✅ |  |
| Incremental - Deduped History | ✅ |  |
| Namespaces | No |  |

​
## Supported Streams
​
The NVD source connector supports two streams.

### Vulnerabilities (CVEs)
The complete API documentation on CVEs can be found in the [official NVD documentation](https://nvd.nist.gov/developers/vulnerabilities).
The produced records look as follows:

```
{
   "id": "CVE-1999-0095",
   "last_modified": "2019-06-11T20:29:00.263",
   "cve": {...}
}
```

Refer to the [full schema](https://csrc.nist.gov/schema/nvd/api/2.0/cve_api_json_2.0.schema) to see all fields in the `cve` object.

### Products (CPEs)
The API documentation on CPEs can be found in the [official NVD documentation](https://nvd.nist.gov/developers/products).
The produced records look as follows:

```
{
   "id": "cpe:2.3:a:3com:3cdaemon:-:*:*:*:*:*:*:*",
   "last_modified": "2011-01-12T14:35:43.723"
   "cpe": {...}
}
```

Refer to the [full schema](https://csrc.nist.gov/schema/nvd/api/2.0/cpe_api_json_2.0.schema) to see all fields in the `cpe` object.

## Changelog
​
| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.0.1   | 2022-12-19 | [#20647](https://github.com/airbytehq/airbyte/pull/20647) | 🎉 New Source: NVD API [Python CDK] |
