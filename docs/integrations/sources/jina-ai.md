# Jina AI

## Overview

Jina AI Reader API addresses these issues of scraping by extracting the core content from a URL and converting it into clean, LLM-friendly text, ensuring high-quality input for your agent and RAG systems.

### Available Streams

Read output is based on input content, but the json format doesn't differ in the response,
Example:

- [Reader](https://r.jina.ai/https://example.com)
- [Search](https://s.jina.ai/When%20was%20Jina%20AI%20founded%3F)

In the above links, replace the substring after base url `https://r.jina.ai/` or `https://r.jina.ai/` with the url or search prompt to get the results

If there are more endpoints you'd like to support, please [Create an 
issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | Yes        |
| Namespaces        | No         |

## Getting started

### Requirements

- Jina AI Bearer Token
- Reader URL
- Search prompt

### Setup guide

Goto `https://jina.ai/reader/#apiform` for the complete guide about different pricing and tokens for that.
The website also provides a free bearer token for testing with its interface.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                              |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------- |
| 0.1.0   | 2024-06-17 | [00000](https://github.com/airbytehq/airbyte/pull/00000) | Add Jina AI source                                                   |

</details>