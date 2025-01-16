# Pingdom
This directory contains the manifest-only connector for `source-pingdom`.

This Source is capable of syncing the following core Streams:

- [checks](https://docs.pingdom.com/api/#tag/Checks/paths/~1checks/get)
- [performance](https://docs.pingdom.com/api/#tag/Summary.performance/paths/~1summary.performance~1{checkid}/get)

## Requirements

- **Pingdom API Key**.[required] See the [PingDom API docs](https://docs.pingdom.com/api/#section/Authentication) for information on how to obtain the API token.
- **Start date**.[required]. To Fetch data from. Only use for Incremental way.
- **Probes**[optional]. Filter to only use results from a list of probes. Format is a comma separated list of probe identifiers.
- **Resolution**[optional]. Interval Size. Should be `hour`, `day`, `week`. Default: `hour`

## Usage
There are multiple ways to use this connector:
- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` using `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.

Please refer to the manifest-only connector documentation for more details.

## Local Development
We recommend you use the Connector Builder to edit this connector.

But, if you want to develop this connector locally, you can use the following steps.

### Environment Setup
You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build
This will create a dev image (`source-pingdom:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-pingdom build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-pingdom test
```

