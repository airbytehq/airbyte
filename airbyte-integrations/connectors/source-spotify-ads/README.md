# Spotify Ads
This directory contains the manifest-only connector for `source-spotify-ads`.

Spotify Ads Connector
Extract campaign performance data from Spotify&#39;s advertising platform
This connector syncs advertising data from Spotify&#39;s Partner API, enabling you to analyze campaign performance metrics and optimize your Spotify advertising strategy. Perfect for marketers, agencies, and businesses running audio and video advertising campaigns on Spotify.
Available Data

Ad Accounts: Basic account information and settings
Campaigns: Campaign details, names, and status
Campaign Performance: Daily metrics including:

Standard metrics: impressions, clicks, spend, CTR, reach, frequency
Audio-specific: streams, listeners, new listeners, paid listens
Video metrics: video views, expands, completion rates
Advanced: conversion rates, intent rates, frequency metrics



Requirements

Spotify Developer application with Partner API access
OAuth 2.0 credentials (Client ID, Client Secret, Refresh Token)
Valid Spotify Ad Account ID

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
This will create a dev image (`source-spotify-ads:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-spotify-ads build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-spotify-ads test
```

