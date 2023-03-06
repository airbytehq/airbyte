# Confluence

This page contains the setup guide and reference information for the Confluence source connector.

## Prerequisites

* [API Token](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
* Your Confluence domain name
* Your Confluence login email

## Setup guide
### Step 1: Set up Confluence connector
1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Confluence** from the Source type dropdown.
4. Enter a name for your source.
5. For **API Tokene** follow the Jira confluence for generating an  [API Token](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
6. For **Domain name** enter your Confluence domain name.
7. For **Email** enter your Confluence login email.

## Supported sync modes

| Feature                   | Supported? |
|:--------------------------|:-----------|
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | No         |
| Incremental - Dedupe Sync | No         |
| SSL connection            | No         |
| Namespaces                | No         |

## Supported Streams

* [Pages](https://developer.atlassian.com/cloud/confluence/rest/api-group-content/#api-wiki-rest-api-content-get)
* [Blog Posts](https://developer.atlassian.com/cloud/confluence/rest/api-group-content/#api-wiki-rest-api-content-get)
* [Space](https://developer.atlassian.com/cloud/confluence/rest/api-group-space/#api-wiki-rest-api-space-get)
* [Group](https://developer.atlassian.com/cloud/confluence/rest/api-group-group/#api-wiki-rest-api-group-get)
* [Audit](https://developer.atlassian.com/cloud/confluence/rest/api-group-audit/#api-wiki-rest-api-audit-get)

## Data type map
The [Confluence API](https://developer.atlassian.com/cloud/confluence/rest/intro/#about) uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

### Performance considerations

The Confluence connector should not run into Confluence API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                              |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------|
| 0.1.2   | 2023-03-06 | [23775](https://github.com/airbytehq/airbyte/pull/23775) | Set additionalProperties: true, update docs and spec |
| 0.1.1   | 2022-01-31 | [9831](https://github.com/airbytehq/airbyte/pull/9831)   | Fix: Spec was not pushed to cache                    |
| 0.1.0   | 2021-11-05 | [7241](https://github.com/airbytehq/airbyte/pull/7241)   | 🎉 New Source: Confluence                            |