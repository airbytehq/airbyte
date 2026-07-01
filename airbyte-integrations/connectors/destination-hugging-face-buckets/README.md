# Destination Hugging Face Buckets

This is an Airbyte destination connector for [Hugging Face Buckets](https://huggingface.co/docs/hub/en/buckets).

## Overview

This connector writes data from Airbyte sources to Hugging Face Buckets in Parquet or JSONL format.

## Configuration

| Field | Required | Description |
|-------|----------|-------------|
| `destination_path` | Yes | The path to the Hugging Face Bucket where data will be written. Format: `hf://buckets/{username}/{bucket}/{path}/` or `hf://username/bucket/path/` |
| `file_format` | No | The format to use when writing files (default: `parquet`). Options: `parquet`, `jsonl` |
| `overwrite` | No | Whether to overwrite existing files (default: `false`) |
| `token` | No | Hugging Face API token for authentication |

### Examples

```json
{
  "destination_path": "hf://buckets/lhoestq/b/",
  "file_format": "parquet",
  "overwrite": true,
  "token": "hf_..."
}
```

## Supported Sync Modes

- `append`: Append data to existing files
- `overwrite`: Overwrite existing files

## Supported Formats

- Parquet (.parquet)
- JSON Lines (.jsonl)