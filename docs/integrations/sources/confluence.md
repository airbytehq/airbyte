# Confluence

This page contains the setup guide and reference information for the 
[Confluence](https://www.atlassian.com/software/confluence) source connector.

## Prerequisites

* Atlassian API Token
* Your Confluence domain name
* Your Confluence login email

## Setup guide
### Create an API Token 

For detailed instructions on creating an Atlassian API Token, please refer to the 
[official documentation](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).

### Set up Confluence connector in Airbyte
1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**.

:::tip
If this is your first time setting up an Airbyte source, skip the next step and proceed to step 4.
:::

3. In the top-right corner, click **+ New source**.
4. Find and select **Confluence** from the list of available sources.
5. Enter a **Source name** of your choosing.
6. In the **API Token** field, enter your Atlassian API Token.
7. In the **Domain name** field, enter your Confluence domain name.
8. In the **Email** field, enter your Confluence login email.
9. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

| Feature                   | Supported? |
|:--------------------------|:-----------|
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | No         |
| Incremental - Dedupe Sync | No         |
| SSL connection            | No         |
| Namespaces                | No         |

## Supported streams

* [Pages](https://developer.atlassian.com/cloud/confluence/rest/api-group-content/#api-wiki-rest-api-content-get)
* [Blog Posts](https://developer.atlassian.com/cloud/confluence/rest/api-group-content/#api-wiki-rest-api-content-get)
* [Space](https://developer.atlassian.com/cloud/confluence/rest/api-group-space/#api-wiki-rest-api-space-get)
* [Group](https://developer.atlassian.com/cloud/confluence/rest/api-group-group/#api-wiki-rest-api-group-get)
* [Audit](https://developer.atlassian.com/cloud/confluence/rest/api-group-audit/#api-wiki-rest-api-audit-get)

:::note
The `audit` stream requires a Standard or Premium plan.
:::

## Data type mapping
The [Confluence Cloud REST API](https://developer.atlassian.com/cloud/confluence/rest/v1/intro/#about) uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

## Performance considerations

The Confluence connector should not run into Confluence API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                        |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------|
| 0.1.3   | 2023-03-13 | [23988](https://github.com/airbytehq/airbyte/pull/23988) | Add view and storage to pages body, add check for stream Audit |
| 0.1.2   | 2023-03-06 | [23775](https://github.com/airbytehq/airbyte/pull/23775) | Set additionalProperties: true, update docs and spec           |
| 0.1.1   | 2022-01-31 | [9831](https://github.com/airbytehq/airbyte/pull/9831)   | Fix: Spec was not pushed to cache                              |
| 0.1.0   | 2021-11-05 | [7241](https://github.com/airbytehq/airbyte/pull/7241)   | 🎉 New Source: Confluence                                      |
