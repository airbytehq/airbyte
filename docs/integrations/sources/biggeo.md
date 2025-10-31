# BigGeo

## Overview

The BigGeo source connector allows you to sync data from [BigGeo](https://biggeo.com), a geospatial data platform. This connector retrieves data from your BigGeo data sources via their API.

## Supported sync modes

| Feature                                  | Supported? |
|:-----------------------------------------|:-----------|
| Full Refresh Sync                        | Yes        |
| Incremental Sync                         | Yes        |
| Replicate Incremental Deletes            | No         |
| SSL connection                           | Yes        |
| Namespaces                               | No         |

## Prerequisites

To use the BigGeo source connector, you'll need:

- A BigGeo account with access to [BigGeo Studio](https://studio.biggeo.com)
- A valid API key from your BigGeo account
- At least one data source configured in your BigGeo account

## Setup guide

### Step 1: Obtain your BigGeo API Key

1. Retrieve your BigGeo API key.

### Step 2: Set up the BigGeo source in Airbyte

1. Click **Sources** and then click **+ New source**
2. On the Set up the source page, select **BigGeo** from the Source type dropdown
3. Enter a **Name** for your BigGeo source
4. Enter your **API Key** obtained from BigGeo Studio
5. Enter the **Data Source Name** - the name of the BigGeo data source you want to sync
6. Click **Set up source**

## Configuration

| Field             | Type   | Required | Default | Description                                                    |
|:------------------|:-------|:---------|:--------|:---------------------------------------------------------------|
| API Key           | string | Yes      | -       | Your BigGeo API key for authentication                         |
| Data Source Name  | string | Yes      | -       | The name of the BigGeo data source to sync data from           |

## Supported streams

The BigGeo source creates one stream per configured data source. The stream name will match your data source name in BigGeo.

### Output schema

The connector retrieves data from BigGeo in JSON format. The schema is dynamic and depends on the structure of your BigGeo data source. The connector uses a flexible schema that accepts any valid JSON structure.

## Performance considerations

- The connector fetches all data from the specified data source in each sync
- For large data sources, consider the memory and bandwidth requirements

## Limitations

- The connector currently supports only full refresh syncs
- Each Airbyte source connection can sync from one BigGeo data source at a time
- To sync multiple data sources, you'll need to create multiple source connections

## Troubleshooting

### Connection check fails

- Verify your API key is correct and hasn't expired
- Ensure you have network connectivity to `studio.biggeo.com`
- Check that your BigGeo account is active and has the necessary permissions

### Data not syncing

- Verify the data source name is correct (case-sensitive)
- Ensure the data source exists in your BigGeo account
- Check that your API key has read permissions for the specified data source
- Review the sync logs in Airbyte for specific error messages

### Authentication errors (401 Unauthorized)

- Your API key may be invalid or expired
- Regenerate your API key in BigGeo Studio and update the connector configuration

### Data source not found errors

- Double-check the spelling of your data source name
- Data source names are case-sensitive
- Verify the data source exists in your BigGeo Studio dashboard

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject         |
|:--------|:-----------|:-------------|:----------------|
| 0.1.0   | 2024-01-01 | N/A          | Initial release |

</details>