# Invoiced
This directory contains the manifest-only connector for `source-invoiced`.

This Airbyte connector for **Invoiced** enables seamless data integration between Invoiced, a cloud-based billing and invoicing platform, and various data destinations. Using this connector, you can automatically extract and sync data such as invoices, customers, payments, and more from the Invoiced API into your preferred data warehouse or analytics platform. It simplifies the process of managing financial data and helps businesses maintain accurate and up-to-date records, facilitating better reporting and analysis. Ideal for users who need to automate data pipelines from their invoicing system.

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
This will create a dev image (`source-invoiced:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-invoiced build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-invoiced test
```

