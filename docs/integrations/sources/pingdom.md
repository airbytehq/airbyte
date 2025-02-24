# Pingdom
This Source is capable of syncing the following core Streams:

- [checks](https://docs.pingdom.com/api/#tag/Checks/paths/~1checks/get)
- [performance](https://docs.pingdom.com/api/#tag/Summary.performance/paths/~1summary.performance~1{checkid}/get)

## Requirements

- **Pingdom API Key**.[required] See the [PingDom API docs](https://docs.pingdom.com/api/#section/Authentication) for information on how to obtain the API token.
- **Start date**.[required]. To Fetch data from. Only use for Incremental way.
- **Probes**[optional]. Filter to only use results from a list of probes. Format is a comma separated list of probe identifiers.
- **Resolution**[optional]. Interval Size. Should be `hour`, `day`, `week`. Default: `hour`

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `probes` | `string` | probes.  |  |
| `api_key` | `string` | API Key.  |  |
| `resolution` | `string` | resolution.  | hour |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| checks | id | DefaultPaginator | ✅ |  ❌  |
| performance |  | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-12-03 | Initial release by [@KimPlv](https://github.com/KimPlv) via Connector Builder|

</details>