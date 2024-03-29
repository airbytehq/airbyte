# PingDom API

This page contains the setup guide and reference information for the Gitlab Source connector.


### Output schema

This Source is capable of syncing the following core Streams:

- [checks](https://docs.pingdom.com/api/#tag/Checks/paths/~1checks/get)
- [performance](https://docs.pingdom.com/api/#tag/Summary.performance/paths/~1summary.performance~1{checkid}/get)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | No                   |       |

## Requirements

- **Pingdom API Key**.[required] See the [PingDom API docs](https://docs.pingdom.com/api/#section/Authentication) for information on how to obtain the API token.
- **Probes**[optional]. Filter to only use results from a list of probes. Format is a comma separated list of probe identifiers.
- **Resolution**[optional]. Interval Size. Should be `hour`, `day`, `week`. Default: `hour`

## Changelog

| Version | Date       | Pull Request                                             | Subject                          |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------- |
| 0.1.0   | 2024-03-29 | [25790](https://github.com/airbytehq/airbyte/pull/25790) | Add Pingdom API Source Connector |
