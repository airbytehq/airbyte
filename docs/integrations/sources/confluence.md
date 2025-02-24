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
| 0.3.12 | 2025-02-22 | [54431](https://github.com/airbytehq/airbyte/pull/54431) | Update dependencies |
| 0.3.11 | 2025-02-15 | [53715](https://github.com/airbytehq/airbyte/pull/53715) | Update dependencies |
| 0.3.10 | 2025-02-08 | [53317](https://github.com/airbytehq/airbyte/pull/53317) | Update dependencies |
| 0.3.9 | 2025-02-01 | [52865](https://github.com/airbytehq/airbyte/pull/52865) | Update dependencies |
| 0.3.8 | 2025-01-25 | [52314](https://github.com/airbytehq/airbyte/pull/52314) | Update dependencies |
| 0.3.7 | 2025-01-18 | [51633](https://github.com/airbytehq/airbyte/pull/51633) | Update dependencies |
| 0.3.6 | 2025-01-11 | [51109](https://github.com/airbytehq/airbyte/pull/51109) | Update dependencies |
| 0.3.5 | 2024-12-28 | [50564](https://github.com/airbytehq/airbyte/pull/50564) | Update dependencies |
| 0.3.4 | 2024-12-21 | [49541](https://github.com/airbytehq/airbyte/pull/49541) | Update dependencies |
| 0.3.3 | 2024-12-12 | [48263](https://github.com/airbytehq/airbyte/pull/48263) | Update dependencies |
| 0.3.2 | 2024-10-28 | [47553](https://github.com/airbytehq/airbyte/pull/47553) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.3.0 | 2024-08-15 | [44162](https://github.com/airbytehq/airbyte/pull/44162) | Refactor connector to manifest-only format |
| 0.2.16 | 2024-08-10 | [43573](https://github.com/airbytehq/airbyte/pull/43573) | Update dependencies |
| 0.2.15 | 2024-08-03 | [43053](https://github.com/airbytehq/airbyte/pull/43053) | Update dependencies |
| 0.2.14 | 2024-07-27 | [42699](https://github.com/airbytehq/airbyte/pull/42699) | Update dependencies |
| 0.2.13 | 2024-07-20 | [42333](https://github.com/airbytehq/airbyte/pull/42333) | Update dependencies |
| 0.2.12 | 2024-07-13 | [41857](https://github.com/airbytehq/airbyte/pull/41857) | Update dependencies |
| 0.2.11 | 2024-07-10 | [41398](https://github.com/airbytehq/airbyte/pull/41398) | Update dependencies |
| 0.2.10 | 2024-07-09 | [41270](https://github.com/airbytehq/airbyte/pull/41270) | Update dependencies |
| 0.2.9 | 2024-07-06 | [41013](https://github.com/airbytehq/airbyte/pull/41013) | Update dependencies |
| 0.2.8 | 2024-06-25 | [40436](https://github.com/airbytehq/airbyte/pull/40436) | Update dependencies |
| 0.2.7 | 2024-06-22 | [40115](https://github.com/airbytehq/airbyte/pull/40115) | Update dependencies |
| 0.2.6 | 2024-06-15 | [39495](https://github.com/airbytehq/airbyte/pull/39495) | Fix parameters as comma seperated single string |
| 0.2.5 | 2024-06-06 | [39261](https://github.com/airbytehq/airbyte/pull/39261) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.4 | 2024-05-14 | [38137](https://github.com/airbytehq/airbyte/pull/38137) | Make connector compatible with the builder |
| 0.2.3 | 2024-04-19 | [37143](https://github.com/airbytehq/airbyte/pull/37143) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37143](https://github.com/airbytehq/airbyte/pull/37143) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37143](https://github.com/airbytehq/airbyte/pull/37143) | schema descriptions |
| 0.2.0 | 2023-08-14 | [29125](https://github.com/airbytehq/airbyte/pull/29125) | Migrate Confluence Source Connector to Low Code |
| 0.1.3 | 2023-03-13 | [23988](https://github.com/airbytehq/airbyte/pull/23988) | Add view and storage to pages body, add check for stream Audit |
| 0.1.2 | 2023-03-06 | [23775](https://github.com/airbytehq/airbyte/pull/23775) | Set additionalProperties: true, update docs and spec |
| 0.1.1 | 2022-01-31 | [9831](https://github.com/airbytehq/airbyte/pull/9831) | Fix: Spec was not pushed to cache |
| 0.1.0 | 2021-11-05 | [7241](https://github.com/airbytehq/airbyte/pull/7241) | 🎉 New Source: Confluence |

</details>
