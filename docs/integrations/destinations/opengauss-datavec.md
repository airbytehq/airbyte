# openGauss Datavec

## Overview

The openGauss Datavec destination allows you to sync data to openGauss database with vector storage capabilities using the Datavec extension.

## Supported sync modes

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  |       |

## Configuration

| Input | Type | Description | Default Value |
| :---- | :--- | :---------- | :------------ |
| `host` | string | Database host | Required |
| `port` | integer | Database port | 5432 |
| `database` | string | Database name | Required |
| `schema` | string | Database schema | public |
| `username` | string | Database username | Required |
| `password` | string | Database password | Required |

### Embedding Configuration

The destination supports multiple embedding providers:

- OpenAI
- Cohere  
- Azure OpenAI
- OpenAI-compatible services
- Fake embeddings (for testing)

### Processing Configuration

- **Chunk Size**: Size of text chunks for embedding
- **Chunk Overlap**: Overlap between chunks
- **Text Fields**: Fields to embed
- **Metadata Fields**: Fields to store as metadata

## Changelog

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
| 0.1.0 | 2025-07-30 | | Initial release |
