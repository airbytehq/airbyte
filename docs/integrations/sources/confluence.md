# Confluence

## Overview

The Confluence source supports Full Refresh syncs. 

### Output schema

This Source is capable of syncing the following core Streams:

* [Pages](https://developer.atlassian.com/cloud/confluence/rest/api-group-content/#api-wiki-rest-api-content-get)
* [Blog Posts](https://developer.atlassian.com/cloud/confluence/rest/api-group-content/#api-wiki-rest-api-content-get)
* [Space](https://developer.atlassian.com/cloud/confluence/rest/api-group-space/#api-wiki-rest-api-space-get)
* [Group](https://developer.atlassian.com/cloud/confluence/rest/api-group-group/#api-wiki-rest-api-group-get)
* [Audit](https://developer.atlassian.com/cloud/confluence/rest/api-group-audit/#api-wiki-rest-api-audit-get)

### Data type mapping

The [Confluence API](https://developer.atlassian.com/cloud/confluence/rest/intro/#about) uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| Incremental - Dedupe Sync | No |
| SSL connection | No |
| Namespaces | No |

### Performance considerations

The Confluence connector should not run into Confluence API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Confluence Account
* Confluence API Token
* Confluence domain name
* Confluence email address

### Setup guide

Follow [this article](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/) to create an API token for your Confluence account. 

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.1 | 2022-01-31 | [9831](https://github.com/airbytehq/airbyte/pull/9831) | Fix: Spec was not pushed to cache |
| 0.1.0 | 2021-11-05 | [7241](https://github.com/airbytehq/airbyte/pull/7241) | 🎉 New Source: Confluence |