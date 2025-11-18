# Standardize Company Names API
This directory contains the manifest-only connector for `source-standardize-company-names-api`.

This API standardizes/normalizes organization and company names into their official name standard using an advanced &#39;closest match&#39; AI algorithm. It handles various input variations including abbreviations, alternate spellings, and multiple languages, converting them all to standardized English equivalents. Perfect for data cleansing, analytics/reporting, and maintaining consistent organization records across your data assets and systems.

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
This will create a dev image (`source-standardize-company-names-api:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-standardize-company-names-api build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-standardize-company-names-api test
```

