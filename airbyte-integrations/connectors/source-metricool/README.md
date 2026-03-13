# Metricool
This directory contains the manifest-only connector for `source-metricool`.

The Metricool connector enables you to extract comprehensive social media analytics data from multiple platforms through Metricool’s unified API. This connector supports data extraction from Facebook, Instagram, TikTok, LinkedIn, Twitter (X), and YouTube, providing detailed insights into your social media performance.

Key Features:
- Multi-Platform Support: Extract data from 6 major social media platforms in a single connector
- Comprehensive Analytics: Access post-level metrics, timeline data, competitor analysis, and content performance
- Flexible Date Range: Configure custom date ranges for data extraction (defaults to 60 days if not specified)
- Multiple Content Types: Supports various content formats including posts, reels, stories, and videos

Supported Data Streams:
- Brand Information: Basic account and profile data
- Content Analytics: Posts, reels, stories, and videos with engagement metrics
- Timeline Data: Historical performance metrics tracked over time
- Competitor Analysis: Available for Facebook and Instagram

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
This will create a dev image (`source-metricool:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-metricool build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-metricool test
```

