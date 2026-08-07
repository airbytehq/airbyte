# Cursor
This directory contains the manifest-only connector for `source-cursor`.

Sync Cursor Teams usage, per-seat spend, and per-event cost data from the Cursor Admin API into your warehouse. Captures Cursor&#39;s rolling usage and spend window into permanent storage, so history accrues from the day you install.

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
This will create a dev image (`source-cursor:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-cursor build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-cursor test
```

