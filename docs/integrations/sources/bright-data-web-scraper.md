# Bright Data Web Scraper
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

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `urls` | `array` | URLs. List of URLs to scrape |  |
| `format` | `string` | Format. Data delivery format | json |
| `notify` | `boolean` | Notify. Send notifications upon completion | false |
| `api_key` | `string` | API Key. Your Bright Data API Key |  |
| `endpoint` | `string` | Webhook Endpoint. Webhook URL for data collection notifications |  |
| `dataset_id` | `string` | Dataset ID. Dataset ID for which data collection is triggered |  |
| `auth_header` | `string` | Webhook Auth Header. Authorization header for webhook delivery |  |
| `include_errors` | `boolean` | Include Errors. Include errors report with the results | false |
| `limit_per_input` | `number` | Limit Per Input. Limit the number of results per input |  |
| `custom_output_fields` | `string` | Custom Output Fields. Filter response data to include only specified fields (pipe-separated) |  |
| `uncompressed_webhook` | `boolean` | Uncompressed Webhook. Send webhook data uncompressed | false |
| `limit_multiple_results` | `number` | Limit Multiple Results. Limit the total number of results |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Bright Data Web Scraper | id.url | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-12-08 | | Initial release by [@adomhamza](https://github.com/adomhamza) via Connector Builder |

</details>
