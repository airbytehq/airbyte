# Launchdarkly API

## Sync overview

This source can sync data from the [Leadfeeder API](https://docs.leadfeeder.com/api).
The Leadfeeder API provides information from the web-based version of Leadfeeder. It identifies the businesses of website visitors, so it’s really useful information to integrate with a B2B sales pipeline.

## Getting started

### Requirements

- **[API Token](https://docs.leadfeeder.com/api/#authentication)**
- **Start date**. use for incremental sync in the format %Y-%m-%dT%H:%M:%SZ
  
## This Source Supports the Following Streams

- accounts
- leads
- visits


### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |

### Performance considerations

To get data from `leads` and `visits` streams, your account needs to have Leadfeeder Premium subscription.



## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ ||
| 0.1.0   | 2024-07-17 | [42051](https://github.com/airbytehq/airbyte/pull/42051) | 🎉 New Source: Leadfeeder |

</details>
