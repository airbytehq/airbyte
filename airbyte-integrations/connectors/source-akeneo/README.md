# Akeneo
This directory contains the manifest-only connector for `source-akeneo`.

The Akeneo Airbyte connector enables seamless data synchronization between Akeneo PIM (Product Information Management) and other platforms. It allows you to easily extract, transform, and load product information from Akeneo to a desired data destination, facilitating efficient management and integration of product catalogs across systems. This connector supports bidirectional data flows, helping businesses maintain accurate and up-to-date product information for various sales channels.

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
This will create a dev image (`source-akeneo:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-akeneo build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-akeneo test
```

