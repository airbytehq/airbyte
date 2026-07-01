# Destination Hugging Face Datasets

This is an Airbyte destination connector for [Hugging Face Datasets](https://huggingface.co/docs/hub/datasets).

## Overview

This connector writes data from Airbyte sources to Hugging Face Datasets. It supports two modes:

1. **Push to HF Hub**: Creates/updates datasets on Hugging Face Hub
2. **Write to HF Buckets**: Stores data in Hugging Face Buckets (file storage)

## Configuration

| Field | Required | Description |
|-------|----------|-------------|
| `dataset_name` | Yes | The name of the Hugging Face Dataset to write to. Format: `{username}/{dataset_name}` |
| `push_to_hub` | No | Whether to push data to Hugging Face Hub (default: `false`). If `false`, data will be written to HF Buckets. |
| `overwrite` | No | Whether to overwrite existing datasets in Hub (default: `false`) |
| `token` | No | Hugging Face API token for authentication |

### Examples

```json
{
  "dataset_name": "lhoestq/b",
  "push_to_hub": true,
  "overwrite": false,
  "token": "hf_..."
}
```

## Supported Sync Modes

- `append`: Append data to existing datasets
- `overwrite`: Replace existing datasets

## How it works

This destination connector receives records from Airbyte sources and writes them to Hugging Face Datasets. Depending on the configuration, it either:

1. Pushes data directly to HF Hub using the `datasets` library
2. Writes data to HF Buckets as Parquet files

## Limitations

- Only supports Parquet format for bucket writes
- Hub pushes require proper dataset structure and authentication