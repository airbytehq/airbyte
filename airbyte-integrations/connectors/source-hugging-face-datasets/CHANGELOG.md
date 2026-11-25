# Changelog

## 0.1.0

Rewrite of the connector on the [Hugging Face `datasets`](https://huggingface.co/docs/datasets) library: datasets are read from the Hub
instead of through the dataset viewer API, so datasets without a Parquet export work, and cells are no longer truncated.

Breaking changes (see the [migration guide](https://docs.airbyte.com/integrations/sources/hugging-face-datasets-migrations#upgrading-to-010)):

- The `rows` and `splits` streams are replaced by one stream per dataset subset and split, named `{dataset}__{subset}__{split}`.
- Records now hold the dataset columns directly instead of the viewer response wrapper (`row`, `row_idx`, `truncated_cells`).
- The `api_token` configuration field is renamed to `token`. Connections configured with `api_token` keep working.

Non-breaking changes:

- Stream schemas are read from the dataset features instead of being catch-all objects.
- Image, audio and video columns are synced as base64 file bytes, without needing the decoding dependencies.
- NaN and infinity values are synced as null so records stay valid JSON.

## Detailed Changes

- [PR #81357](https://github.com/airbytehq/airbyte/pull/81357): Rewrite the connector on the `datasets` library
