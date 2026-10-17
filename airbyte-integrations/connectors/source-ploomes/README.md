# Ploomes
This directory contains the manifest-only connector for `source-ploomes`.

Ploomes CRM Source Connector (Declarative)

This connector provides native integration with the Ploomes CRM Public API, enabling continuous ingestion of entities such as Users, Products, and other CRM resources.

It is fully built using the Airbyte Connector Builder and implements:
- Pagination via $top and $skip
- Authentication using the User-Key header
- Incremental sync based on LastUpdateDate
- Automatic retry with exponential backoff
- Clean declarative schemas and reusable components

This connector is ideal for modern ELT pipelines, data lake ingestion, business analytics workflows, and integrations with Power BI, Snowflake, BigQuery, Databricks, and any destination supported by Airbyte.

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
This will create a dev image (`source-ploomes:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-ploomes build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-ploomes test
```

