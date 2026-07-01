# Source Hugging Face Datasets

This is an Airbyte source connector for [Hugging Face Datasets](https://huggingface.co/datasets).

## Overview

This connector reads data from Hugging Face Datasets (dataset repositories on Hugging Face Hub).

## Configuration

| Field | Required | Description |
|-------|----------|-------------|
| `dataset_name` | Yes | The name of the Hugging Face Dataset to read from. Format: `{username}/{dataset_name}` |
| `token` | No | Hugging Face API token for authentication |
| `streaming` | No | Whether to enable streaming to save disk space |

### Examples

```json
{
  "dataset_name": "lhoestq/demo1",
  "token": "hf_..."
}
```

## How it works

This connector uses the `datasets` library to read the dataset. During the sync, it reads the files and emits records based on the configured file format.

## Supported Formats

- Parquet (.parquet)
- CSV (.csv)
- JSON/JSONL (.json, .jsonl)
- Lance (.lance)
- WebDataset (.tar)
- Image, audio, video
- and more, see the full list in the [documentation](https://huggingface.co/docs/datasets/package_reference/loading_methods#from-files)
