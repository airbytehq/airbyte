# Jina AI Reader

## Overview

This connector allows access to the [Jina Reader API](https://jina.ai/reader/) using two modes:
- **"Reader" Mode** (`https://r.jina.api`) - Given a set of one or more URLs as input, return the content of those pages as Markdown text. The Reader endpoint extracts the core content from a URL and converting it into clean, LLM-friendly text, ensuring high-quality input for your agent and RAG systems.
- **"Search" Mode** (`https://s.jina.api`) - Similar to the reader endpoint, but accepting a search prompt and returning the text from top 5 search results.
Both of these API endpoints will generate human readable markdown, which can also be efficiently processed by downstream LLM and GenAI applications.
Both modes can be utilized in the same sync, following the configuration instructions below.

### Available Streams

Read output is based on input content, but the json format doesn't differ in the response,
Example:

- [Reader](https://r.jina.ai/https://example.com)
- [Search](https://s.jina.ai/When%20was%20Jina%20AI%20founded%3F)

In the above links, replace the substring after base url `https://r.jina.ai/` or `https://s.jina.ai/` with the url or search prompt to get the results

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

- Jina AI Bearer Token (For higher rate limits)
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
| 0.1.13 | 2024-08-31 | [45015](https://github.com/airbytehq/airbyte/pull/45015) | Update dependencies |
| 0.1.12 | 2024-08-24 | [44641](https://github.com/airbytehq/airbyte/pull/44641) | Update dependencies |
| 0.1.11 | 2024-08-17 | [44235](https://github.com/airbytehq/airbyte/pull/44235) | Update dependencies |
| 0.1.10 | 2024-08-12 | [43916](https://github.com/airbytehq/airbyte/pull/43916) | Update dependencies |
| 0.1.9 | 2024-08-10 | [43469](https://github.com/airbytehq/airbyte/pull/43469) | Update dependencies |
| 0.1.8 | 2024-08-03 | [43126](https://github.com/airbytehq/airbyte/pull/43126) | Update dependencies |
| 0.1.7 | 2024-07-27 | [42675](https://github.com/airbytehq/airbyte/pull/42675) | Update dependencies |
| 0.1.6 | 2024-07-20 | [42361](https://github.com/airbytehq/airbyte/pull/42361) | Update dependencies |
| 0.1.5 | 2024-07-13 | [41692](https://github.com/airbytehq/airbyte/pull/41692) | Update dependencies |
| 0.1.4 | 2024-07-10 | [41594](https://github.com/airbytehq/airbyte/pull/41594) | Update dependencies |
| 0.1.3 | 2024-07-09 | [41245](https://github.com/airbytehq/airbyte/pull/41245) | Update dependencies |
| 0.1.2 | 2024-07-06 | [40880](https://github.com/airbytehq/airbyte/pull/40880) | Update dependencies |
| 0.1.1 | 2024-06-25 | [40359](https://github.com/airbytehq/airbyte/pull/40359) | Update dependencies |
| 0.1.0 | 2024-06-25 | [39515](https://github.com/airbytehq/airbyte/pull/39515) | Add Jina AI source |

</details>
