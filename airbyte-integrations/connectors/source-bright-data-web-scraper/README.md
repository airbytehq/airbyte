# Bright Data Web Scraper
This directory contains the manifest-only connector for `source-bright-data-web-scraper`.

# Bright Data Web Scraper Connector Setup Guide

This guide will help you set up and configure the Bright Data Web Scraper connector for Airbyte.


## Prerequisites

Before setting up the connector, ensure you have:

1. **Bright Data Account**
   - An active Bright Data account
   - API key (Bearer token)
   - Dataset ID for the web scraper


2. **URLs to Scrape**
   - List of URLs you want to scrape
   - URLs should be publicly accessible or within your Bright Data dataset scope

## Step 1: Obtain Bright Data Credentials

### Get Your API Key

1. Log in to your [Bright Data dashboard](https://brightdata.com/)
2. Navigate to **Settings** → **Users and API Keys**
3. Generate a new API key or copy your existing Bearer token
4. Store this securely - you&#39;ll need it for connector configuration

### Get Your Dataset ID

1. In Bright Data dashboard, go to your **Datasets** section
2. Select the dataset you want to use for web scraping
3. Copy the Dataset ID (format: `gd_xxxxxxxxxxxxx`)
4. Example: `gd_l1vikfnt1wgvvqz95w`

## Step 2: Configure the Connector

### Required Configuration Fields

The connector requires the following mandatory fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **API Key** | string (secret) | Your Bright Data Bearer token | `your_api_key_here` |
| **Dataset ID** | string | Bright Data dataset identifier | `gd_l1vikfnt1wgvvqz95w` |
| **URLs** | array[string] | List of URLs to scrape | `[&quot;https://example.com/page1&quot;, &quot;https://example.com/page2&quot;]` |

### Optional Configuration Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| **Format** | enum | Data delivery format | `json` |
| **Custom Output Fields** | string | Pipe-separated field filter | - |
| **Collection Type** | enum | Set to &quot;discover_new&quot; for discovery phase | - |
| **Discover By** | enum | Discovery method (keyword, best_sellers_url, etc.) | - |
| **Include Errors** | boolean | Include error reports in results | `false` |
| **Limit Per Input** | number | Max results per URL input | - |
| **Limit Multiple Results** | number | Total max results | - |
| **Notify** | boolean | Enable completion notifications | `false` |
| **Webhook Endpoint** | string | URL for webhook notifications | - |
| **Webhook Auth Header** | string (secret) | Authorization header for webhook | - |
| **Uncompressed Webhook** | boolean | Send uncompressed webhook data | `false` |

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
This will create a dev image (`source-bright-data-web-scraper:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-bright-data-web-scraper build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-bright-data-web-scraper test
```

