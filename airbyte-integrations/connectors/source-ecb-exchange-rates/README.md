# ECB Exchange Rates
This directory contains the manifest-only connector for `source-ecb-exchange-rates`.

- Low-code declarative source that hits https://api.frankfurter.app/{date} to fetch daily ECB
    reference rates directly from the Frankfurter API; no auth required.
  - Accepts start_date (required), optional end_date, base_currency, amount, and an optional list of
    target_currencies; when targets are omitted, the API returns the full rate map for every supported
    currency.
  - Uses a DatetimeStreamSlicer/DatetimeBasedCursor on the date field so incremental syncs request one
    business day at a time and resume automatically.
  - Response schema includes amount, base, date, optional start_date/end_date, and the raw rates object
    (currency→value). Downstream models can explode rates with SQL/ELT if per-currency rows are needed.
  - Designed for stable weekday updates (ECB publishes around 16:00 CET) and lightweight retries via
    DefaultErrorHandler.

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
This will create a dev image (`source-ecb-exchange-rates:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-ecb-exchange-rates build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-ecb-exchange-rates test
```

