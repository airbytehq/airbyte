# BigGeo

## Overview

The BigGeo destination allows you to sync data to [BigGeo](https://biggeo.com), a geospatial data platform. This connector sends data to your BigGeo data sources via their API.

## Supported sync modes

| Feature                        | Supported? |
| :----------------------------- | :--------- |
| Full Refresh Sync              | Yes        |
| Incremental - Append Sync      | Yes        |
| Incremental - Append + Deduped | No         |

## Prerequisites

To use the BigGeo destination connector, you'll need:

- A BigGeo account with access to [BigGeo Studio](https://studio.biggeo.com)
- A valid API key from your BigGeo account
- Access to create and manage data sources in BigGeo

## Setup guide

### Step 1: Obtain your BigGeo API Key

1. Retrieve your BigGeo API key.

### Step 2: Set up the BigGeo destination in Airbyte

1. Click **Destinations** and then click **+ New destination**
2. On the Set up the destination page, select **BigGeo** from the Destination type dropdown
3. Enter a **Name** for your BigGeo destination
4. Enter your **API Key** obtained from BigGeo Studio
5. (Optional) Configure the **Batch Size** - the number of records to send in each API request (default: 1000)
6. Click **Set up destination**

## Configuration

| Field      | Type    | Required | Default | Description                                                    |
| :--------- | :------ | :------- | :------ | :------------------------------------------------------------- |
| API Key    | string  | Yes      | -       | Your BigGeo API key for authentication                         |
| Batch Size | integer | No       | 1000    | Number of records to batch together in each API request        |

## Supported streams

The BigGeo destination writes data to a Data Source in your BigGeo account. Each stream in your Airbyte connection will be written to the corresponding data source in BigGeo.

## Output schema

The connector sends data to BigGeo in JSON format. The received format is then converted into a BigGeo compatible format.

## Performance considerations

- The default batch size is 1000 records. You can adjust this based on your network conditions and BigGeo API limits
- Larger batch sizes may improve throughput but could increase memory usage
- If you experience timeouts, consider reducing the batch size

## Troubleshooting

### Connection check fails

- Verify your API key is correct and hasn't expired
- Ensure you have network connectivity to `studio.biggeo.com`
- Check that your BigGeo account is active and has the necessary permissions

### Data not appearing in BigGeo

- Check the sync logs in Airbyte for any error messages
- Ensure your API key has write permissions for the target data source

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject         |
|:--------|:-----------|:-------------|:----------------|
| 0.1.0   | 2024-01-01 | N/A          | Initial release |

</details>
