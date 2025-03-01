# Eventee
This directory contains the manifest-only connector for `source-eventee`.

The Airbyte connector for Eventee enables seamless integration and automated data synchronization between Eventee, a leading event management platform, and your data destinations. It extracts and transfers event-related information such as attendee details, lectures, tracks, and more. This connector ensures real-time or scheduled data flow, helping you centralize and analyze Eventee&#39;s data effortlessly for improved event insights and reporting.

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
This will create a dev image (`source-eventee:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-eventee build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-eventee test
```

