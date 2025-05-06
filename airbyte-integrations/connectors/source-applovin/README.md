# AppLovin
This directory contains the manifest-only connector for `source-applovin`.

A lightweight, declarative Airbyte source that pulls your Applovin advertiser report via the /report endpoint into a single report stream. It requests data by date range (start_date → now), automatically re-fetching the prior 2 days on each run (lookback window = P2D) to capture any late-arriving hourly rows. Records are deduplicated in the destination using a composite primary key (ad_id, campaign_id_external, creative_set_id, day, hour, placement_type, platform). All hourly metrics (cost, clicks, ROAS, etc.) flow through the results array via a simple DpathExtractor, enabling both full historical backfills and efficient daily incremental loads with zero data loss.

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
This will create a dev image (`source-applovin:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-applovin build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-applovin test
```

