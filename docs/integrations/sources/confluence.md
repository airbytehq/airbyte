# Confluence

This page contains the setup guide and reference information for the
[Confluence](https://www.atlassian.com/software/confluence) source connector.

## Prerequisites

- Atlassian API Token
- Your Confluence domain name
- Your Confluence login email

## Setup guide

### Step 1: Create an API Token

For detailed instructions on creating an Atlassian API Token, please refer to the
[official documentation](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).

### Step 2: Set up the Confluence connector in Airbyte

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or navigate to the Airbyte Open Source dashboard.
2. From the Airbyte UI, click **Sources**, then click on **+ New Source** and select **Confluence** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. In the **API Token** field, enter your Atlassian API Token.
5. In the **Domain name** field, enter your Confluence domain name.
6. In the **Email** field, enter your Confluence login email.
7. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | No         |
| Incremental - Dedupe Sync | No         |
| SSL connection            | No         |
| Namespaces                | No         |

## Supported streams

- [Audit](https://developer.atlassian.com/cloud/confluence/rest/api-group-audit/#api-wiki-rest-api-audit-get)
- [Blog Posts](https://developer.atlassian.com/cloud/confluence/rest/api-group-content/#api-wiki-rest-api-content-get)
- [Group](https://developer.atlassian.com/cloud/confluence/rest/api-group-group/#api-wiki-rest-api-group-get)
- [Pages](https://developer.atlassian.com/cloud/confluence/rest/api-group-content/#api-wiki-rest-api-content-get)
- [Space](https://developer.atlassian.com/cloud/confluence/rest/api-group-space/#api-wiki-rest-api-space-get)

:::note
The `audit` stream requires a Standard or Premium plan.
:::

## Data type mapping

The [Confluence Cloud REST API](https://developer.atlassian.com/cloud/confluence/rest/v1/intro/#about) uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

## Performance considerations

The Confluence connector should not run into Confluence API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.4   | 2024-05-14 | [38137](https://github.com/airbytehq/airbyte/pull/38137) | Make connector compatible with the builder                                      |
| 0.2.3   | 2024-04-19 | [37143](https://github.com/airbytehq/airbyte/pull/37143) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry.                      |
| 0.2.2   | 2024-04-15 | [37143](https://github.com/airbytehq/airbyte/pull/37143) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1   | 2024-04-12 | [37143](https://github.com/airbytehq/airbyte/pull/37143) | schema descriptions                                                             |
| 0.2.0   | 2023-08-14 | [29125](https://github.com/airbytehq/airbyte/pull/29125) | Migrate Confluence Source Connector to Low Code                                 |
| 0.1.3   | 2023-03-13 | [23988](https://github.com/airbytehq/airbyte/pull/23988) | Add view and storage to pages body, add check for stream Audit                  |
| 0.1.2   | 2023-03-06 | [23775](https://github.com/airbytehq/airbyte/pull/23775) | Set additionalProperties: true, update docs and spec                            |
| 0.1.1   | 2022-01-31 | [9831](https://github.com/airbytehq/airbyte/pull/9831)   | Fix: Spec was not pushed to cache                                               |
| 0.1.0   | 2021-11-05 | [7241](https://github.com/airbytehq/airbyte/pull/7241)   | 🎉 New Source: Confluence                                                       |

</details>