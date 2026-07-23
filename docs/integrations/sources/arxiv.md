# arXiv

## Prerequisites

The arXiv source connector uses the public arXiv API. No credentials are required.

## Supported sync modes

The arXiv source connector supports full refresh syncs.

## Supported streams

This connector supports the following stream:

- `papers`: paper metadata returned by the arXiv API for the configured search query.

The connector syncs metadata only. It does not download or store PDF files or source files.

## Configuration

| Field | Description |
| :---- | :---------- |
| Search query | arXiv API query string, such as `cat:cs.AI`, `all:electron`, or `au:"Hinton"`. |
| Page size | Number of records to request per API page. The default is 100. |

See the [arXiv API user manual](https://info.arxiv.org/help/api/user-manual.html) for query syntax and supported field prefixes.

## Performance considerations

The arXiv API Terms of Use limit clients to one request every three seconds and one connection at a time. This connector throttles requests to respect that limit.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject |
| :------ | :--------- | :----------- | :------ |
| 0.1.0 | 2026-05-26 | [78425](https://github.com/airbytehq/airbyte/pull/78425) | Added the arXiv source connector with paper metadata syncs. |

</details>
