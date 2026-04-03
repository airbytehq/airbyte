# Bright Data Web Unlocker
This directory contains the manifest-only connector for `source-bright-data-web-unlocker`.

# Bright Data Web Unlocker Connector Setup Guide

This guide will help you set up and configure the Bright Data Web Unlocker connector for Airbyte.


## Prerequisites

Before setting up the connector, ensure you have:

1. **Bright Data Account**
   - An active Bright Data account
   - API key (Bearer token)


2. **URLs to Unlock**
   - List of URLs you want to unlock
   - URLs should be publicly accessible

## Step 1: Obtain Bright Data Credentials

### Get Your API Key

1. Log in to your [Bright Data dashboard](https://brightdata.com/)
2. Navigate to **Settings** → **Users and API Keys**
3. Generate a new API key or copy your existing Bearer token
4. Store this securely - you&#39;ll need it for connector configuration


## Step 2: Configure the Connector

### Required Configuration Fields

The connector requires the following mandatory fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **API Key** | string (secret) | Your Bright Data Bearer token | `your_api_key_here` |
| **URLs** | array[string] | List of URLs to unlocke | `[&quot;https://example.com/page1&quot;, &quot;https://example.com/page2&quot;]` |

### Optional Configuration Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| **Format** | enum | Data delivery format | `json` |
| **Country** | enum | Data delivery format | `us` |

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
This will create a dev image (`source-bright-data-web-unlocker:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-bright-data-web-unlocker build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-bright-data-web-unlocker test
```

