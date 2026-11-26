# Source Hugging Face Buckets

This is an Airbyte source connector for [Hugging Face Buckets](https://huggingface.co/docs/hub/en/buckets).

## Overview

This connector reads data from Hugging Face Buckets (file storage on Hugging Face Hub). It supports multiple file formats including Parquet, CSV, and JSONL.

## Configuration

| Field | Required | Description |
|-------|----------|-------------|
| `bucket_path` | Yes | The path to the Hugging Face Bucket to read from. Format: `hf://buckets/{username}/{bucket}/{path}/` |
| `file_format` | No | The format of files in the bucket (default: `parquet`). Options: `parquet`, `csv`, `jsonl` |
| `reader_options` | No | JSON string with reader options (e.g., separators, encoding) |
| `token` | No | Hugging Face API token for authentication |

### Examples

```json
{
  "bucket_path": "hf://buckets/lhoestq/b/",
  "file_format": "parquet",
  "reader_options": "{}",
  "token": "hf_..."
}
```

## How it works

This connector discovers all files in the specified bucket path and creates a stream for each file. During the sync, it reads the files and emits records based on the configured file format.

## Supported Formats

- Parquet (.parquet)
- CSV (.csv)
- JSON/JSONL (.json, .jsonl)