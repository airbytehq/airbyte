# Destination Hugging Face Datasets

This is an Airbyte destination connector for [Hugging Face Datasets](https://huggingface.co/docs/hub/datasets).

## Overview

This connector writes data from Airbyte sources to Hugging Face Datasets.

## Configuration

| Field | Required | Description |
|-------|----------|-------------|
| `dataset_name` | Yes | The name of the Hugging Face Dataset to write to. Format: `{username}/{dataset_name}` |
| `token` | No | Hugging Face API token for authentication |

### Examples

```json
{
  "dataset_name": "lhoestq/demo1",
  "token": "hf_..."
}
```

## Supported Sync Modes

- `overwrite`: Replace existing datasets

## How it works

This destination connector receives records from Airbyte sources and writes them to Hugging Face Datasets. It pushes data directly to HF Hub using the `datasets` library.

## Limitations

- Only supports Parquet format
