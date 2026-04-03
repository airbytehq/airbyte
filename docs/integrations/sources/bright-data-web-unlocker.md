# Bright Data Web Unlocker
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

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `urls` | `array` | URLs to Scrape. List of URLs to scrape using Unlocker |  |
| `zone` | `string` | Zone. Bright Data zone identifier (e.g., web_unlocker1) | web_unlocker1 |
| `format` | `string` | Response Format. Response format | json |
| `method` | `string` | HTTP Method. HTTP method for the request | GET |
| `api_key` | `string` | API Key. Your Bright Data API Key |  |
| `country` | `string` | Country Code. Two-letter ISO country code for proxy location (e.g., us, gb, de) | us |
| `data_format` | `string` | Data Format. Additional response format transformation |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Bright Data Web Unlocker | url | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-12-08 | | Initial release by [@adomhamza](https://github.com/adomhamza) via Connector Builder |

</details>
