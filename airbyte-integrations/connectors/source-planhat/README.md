# Planhat
This directory contains the manifest-only connector for `source-planhat`.

This source can sync data for the [general Planhat API](https://docs.planhat.com/)

This Source is capable of syncing the following core Streams:

- [companies](https://docs.planhat.com/#companies)
- [conversations](https://docs.planhat.com/#conversations)
- [custom_fields](https://docs.planhat.com/#custom_fields)
- [endusers](https://docs.planhat.com/#endusers)
- [invoices](https://docs.planhat.com/#invoices)
- [issues](https://docs.planhat.com/#issues)
- [licenses](https://docs.planhat.com/#licenses)
- [nps](https://docs.planhat.com/#nps)
- [opportunities](https://docs.planhat.com/#opportunities)
- [objectives](https://docs.planhat.com/#objectives)
- [sales](https://docs.planhat.com/#sales)
- [tasks](https://docs.planhat.com/#tasks)
- [tickets](https://docs.planhat.com/#tickets)
- [users](https://docs.planhat.com/#users)
## Usage

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
This will create a dev image (`source-planhat:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-planhat build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-planhat test
```

