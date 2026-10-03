# Bright Data SERP
# Bright Data SERP Scrape Connector Setup Guide

This guide will help you set up and configure the Bright Data SERP Scrape connector for Airbyte.


## Prerequisites

Before setting up the connector, ensure you have:

1. **Bright Data Account**
   - An active Bright Data account
   - API key (Bearer token)


2. **Search Queries**
   - List of strings you want to search

3. **Zone**
   - Zone to query. eg:serp_api1

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
| **Search Queries** | array[string] | List of queries to search | `[&quot;Pizza&quot;, &quot;Bright Data` |
| **Zone** | string | zone to search | `serp_api1` |


### Optional Configuration Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| **Search Engine** | enum | Search engines to query | `google` |
| **Response Format** | enum | Data delivery format | `json` |
| **Data Format** | enum | Additional response format transformation | `markdown` |
| **Country** | string | Two-letter ISO 3166-1 country code for proxy location | `us` |

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `zone` | `string` | Zone. Bright Data zone identifier (e.g., serp_api1) | serp_api1 |
| `format` | `string` | Response Format. Response format | json |
| `api_key` | `string` | API Key. Your Bright Data API Key |  |
| `country` | `string` | Country Code. Two-letter ISO country code for proxy location (e.g., us, gb, de) | us |
| `data_format` | `string` | Data Format. Additional response format transformation |  |
| `search_engine` | `string` | Search Engine. Search engine to use for scraping | Google |
| `search_queries` | `array` | Search Queries. List of search queries to scrape |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Bright Data SERP | search_query | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-12-08 | | Initial release by [@adomhamza](https://github.com/adomhamza) via Connector Builder |

</details>
