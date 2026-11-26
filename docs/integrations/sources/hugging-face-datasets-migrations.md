import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Hugging Face - Datasets Migration Guide

## Upgrading to 0.1.0

Version 0.1.0 rewrites the connector on top of the [datasets](https://huggingface.co/docs/datasets) library. It reads datasets directly
from the Hugging Face Hub instead of going through the [Dataset Viewer](https://huggingface.co/docs/dataset-viewer) HTTP API, which used
to cap what could be read: the Viewer only served datasets it had converted to Parquet, and it truncated long cells.

This is a breaking release: stream names, record structure and the token field all change.

### Streams are renamed

The two fixed streams `rows` and `splits` are replaced by one stream per dataset subset and split, named
`{dataset}__{subset}__{split}`, for example `nyu-mll/glue__mrpc__train`.

The `splits` stream is gone. Subsets and splits are now synced as data, so there is nothing left to list separately.

### Records are the dataset rows

Records now hold the columns of the dataset directly, instead of being wrapped into a Viewer response:

| Before 0.1.0                                                                   | Since 0.1.0                    |
| ------------------------------------------------------------------------------ | ------------------------------ |
| `{"config": "dataset::subset::split", "row": {"col_a": ...}, "row_idx": 0, "truncated_cells": []}` | `{"col_a": ..., "col_b": ...}` |

The columns are discovered from the [dataset features](https://huggingface.co/docs/datasets/about_dataset_features), so every stream now
has the real schema of its dataset instead of a catch-all one. Cells are no longer truncated: `truncated_cells` is gone and every value
is synced in full.

Image, audio and video columns are synced as `{"bytes": ..., "path": ...}` objects, where `bytes` is the base64 encoded original file.
Those files can be large, so consider deselecting these columns when the destination cannot store them.

### The token field is renamed

The `api_token` configuration field is named `token` now. Connections created before 0.1.0 keep syncing through the deprecated field, but
its value should be moved to the new **Hugging Face token** field at the next configuration edit.

### What you need to do

1. Upgrade the connector to 0.1.0 or later.
2. Refresh the source schema and re-map the columns: the `rows` and `splits` columns no longer exist.
3. Clear and re-sync every stream, since the old data was structured differently.
4. Move the token to the new **Hugging Face token** field.

## Connector upgrade guide

<MigrationGuide />
