# Airbyte Infakt Connector
This directory contains the manifest-only connector for `source-airbyte-infakt-connector`.

InFakt is a Polish invoicing and accounting SaaS platform used by businesses to manage invoices, clients, and financial documents. This connector enables automated extraction of invoice and client data
from InFakt into your data warehouse.

The connector supports:
- **Clients stream**: Complete client/company directory with contact information and tax IDs (NIP)
- **Invoices stream**: Comprehensive invoice data including financial details, payment status, and client references with incremental sync support

Key features:
- Incremental sync based on invoice date for efficient data replication
- Automatic pagination handling for large datasets
- Robust error handling with exponential backoff for rate limits
- Configurable date ranges for historical data backfills

This connector is ideal for businesses using InFakt who need to:
- Build financial reporting dashboards in BI tools
- Integrate invoice data with ERP or accounting systems
- Perform revenue analysis and forecasting
- Track accounts receivable and payment status
- Consolidate data from multiple legal entities

Authentication requires an InFakt API key which can be obtained from the InFakt application settings.

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
This will create a dev image (`source-airbyte-infakt-connector:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-airbyte-infakt-connector build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-airbyte-infakt-connector test
```

