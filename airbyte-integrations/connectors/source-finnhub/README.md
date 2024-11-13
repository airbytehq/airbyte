# Finnhub
This directory contains the manifest-only connector for `source-finnhub`.

Finnhub is a financial data platform that provides real-time stock market, forex, and cryptocurrency data, along with extensive fundamental data, economic indicators, and alternative data for global markets. With its powerful API, Finnhub delivers actionable insights, enabling developers, financial institutions, and traders to integrate market intelligence into their applications, build trading algorithms, and track investment performance. It supports a wide range of financial metrics, including earnings reports, company profiles, and news, making it a comprehensive solution for financial analysis and market research

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
This will create a dev image (`source-finnhub:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-finnhub build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-finnhub test
```

