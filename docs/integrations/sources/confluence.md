# Confluence

This page contains the setup guide and reference information for the
[Confluence](https://www.atlassian.com/software/confluence) source connector.

## Prerequisites

- A Confluence Cloud site, for example `your-domain.atlassian.net`
- An Atlassian account email for a user who can access the site
- An Atlassian API token for that account

## Setup guide

### Step 1: Create an API token

Create an Atlassian API token in your Atlassian account. For detailed instructions,
see [Manage API tokens for your Atlassian account](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).

This connector authenticates to your Confluence site URL with HTTP Basic authentication
using your Atlassian account email and API token. If you create a scoped API token,
Atlassian requires requests to use `https://api.atlassian.com/ex/confluence/{cloudId}`.
This connector doesn't support scoped API tokens.

### Step 2: Set up the Confluence connector in Airbyte

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or navigate to the Airbyte Open Source dashboard.
2. From the Airbyte UI, click **Sources**, then click **+ New Source** and select **Confluence** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. In the **API Token** field, enter your Atlassian API token.
5. In the **Domain name** field, enter your Confluence Cloud hostname, for example `your-domain.atlassian.net`. Don't include `https://`.
6. In the **email** field, enter the Atlassian account email you used to create the API token.
7. Click **Set up source** and wait for the tests to complete.

## Permissions

The connector can only sync records that the configured Atlassian user can view in
Confluence.

- The `pages`, `blog_posts`, `space`, and `group` streams require the user to have
  permission to access the Confluence site.
- The `pages` and `blog_posts` streams only return content the user can view in the
  corresponding space.
- The `space` stream only returns spaces the user can view.
- The `audit` stream requires the **Confluence Administrator** global permission.
  The audit log is available only on Standard and Premium Confluence plans.

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
- [Blog Posts](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-blog-post/#api-blogposts-get)
- [Group](https://developer.atlassian.com/cloud/confluence/rest/api-group-group/#api-wiki-rest-api-group-get)
- [Pages](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-get)
- [Space](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/#api-spaces-get)

All streams sync in Full Refresh mode. The `pages`, `blog_posts`, and `space`
streams use Confluence REST API v2 cursor-based pagination. The `audit` and
`group` streams use Confluence REST API v1 offset-based pagination.

## Data type mapping

The [Confluence Cloud REST API](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/) uses the same [JSON Schema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally: `string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`. No type conversions happen as part of this source.

## Performance considerations

The Confluence Cloud REST API uses rate limits and quotas. Atlassian doesn't publish
fixed limits for this API. The connector automatically retries rate-limited
requests. If you see rate limit issues that aren't retried successfully, contact
Airbyte Support or post in the [Airbyte community Slack](https://slack.airbyte.com/).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Reference

The connector uses these configuration fields for programmatic setup with PyAirbyte,
Terraform, or the Airbyte API:

- `email`: Atlassian account email for the user whose permissions determine which
  Confluence records Airbyte can sync.
- `api_token`: Atlassian API token for the email account. Use an API token without scopes.
- `domain_name`: Confluence Cloud hostname, for example `your-domain.atlassian.net`.
  Don't include the protocol.

All streams use Full Refresh sync. Version `1.0.23` fixed a discovery issue that
incorrectly advertised Incremental sync for streams that don't define cursors. If an
existing connection selected Incremental sync for this connector, refresh the source
schema and set the affected streams back to Full Refresh.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
| 1.0.27 | 2026-06-23 | [80413](https://github.com/airbytehq/airbyte/pull/80413) | Update dependencies |
| 1.0.26 | 2026-06-16 | [79819](https://github.com/airbytehq/airbyte/pull/79819) | Update dependencies |
| 1.0.25 | 2026-06-09 | [79251](https://github.com/airbytehq/airbyte/pull/79251) | Update dependencies |
| 1.0.24 | 2026-06-02 | [78568](https://github.com/airbytehq/airbyte/pull/78568) | Update dependencies |
| 1.0.23 | 2026-05-07 | [77776](https://github.com/airbytehq/airbyte/pull/77776) | Bump base image to `source-declarative-manifest:7.18.1` so streams without cursors no longer advertise incremental sync |
| 1.0.22 | 2026-05-07 | [77820](https://github.com/airbytehq/airbyte/pull/77820) | Switch v2 streams (`pages`, `blog_posts`, `space`) to cursor-based pagination |
| 1.0.21 | 2025-12-19 | [70941](https://github.com/airbytehq/airbyte/pull/70941) | Update dependencies |
| 1.0.20 | 2025-11-25 | [69919](https://github.com/airbytehq/airbyte/pull/69919) | Update dependencies |
| 1.0.19 | 2025-10-29 | [66333](https://github.com/airbytehq/airbyte/pull/66333) | Update dependencies |
| 1.0.18 | 2025-09-09 | [65889](https://github.com/airbytehq/airbyte/pull/65889) | Update dependencies |
| 1.0.17 | 2025-08-23 | [65281](https://github.com/airbytehq/airbyte/pull/65281) | Update dependencies |
| 1.0.16 | 2025-08-09 | [64777](https://github.com/airbytehq/airbyte/pull/64777) | Update dependencies |
| 1.0.15 | 2025-08-02 | [64318](https://github.com/airbytehq/airbyte/pull/64318) | Update dependencies |
| 1.0.14 | 2025-07-26 | [63958](https://github.com/airbytehq/airbyte/pull/63958) | Update dependencies |
| 1.0.13 | 2025-07-19 | [63597](https://github.com/airbytehq/airbyte/pull/63597) | Update dependencies |
| 1.0.12 | 2025-07-12 | [63027](https://github.com/airbytehq/airbyte/pull/63027) | Update dependencies |
| 1.0.11 | 2025-07-05 | [62797](https://github.com/airbytehq/airbyte/pull/62797) | Update dependencies |
| 1.0.10 | 2025-06-28 | [62380](https://github.com/airbytehq/airbyte/pull/62380) | Update dependencies |
| 1.0.9 | 2025-06-22 | [61996](https://github.com/airbytehq/airbyte/pull/61996) | Update dependencies |
| 1.0.8 | 2025-06-14 | [61176](https://github.com/airbytehq/airbyte/pull/61176) | Update dependencies |
| 1.0.7 | 2025-05-24 | [60406](https://github.com/airbytehq/airbyte/pull/60406) | Update dependencies |
| 1.0.6 | 2025-05-10 | [59921](https://github.com/airbytehq/airbyte/pull/59921) | Update dependencies |
| 1.0.5 | 2025-05-03 | [59442](https://github.com/airbytehq/airbyte/pull/59442) | Update dependencies |
| 1.0.4 | 2025-04-26 | [58851](https://github.com/airbytehq/airbyte/pull/58851) | Update dependencies |
| 1.0.3 | 2025-04-19 | [58320](https://github.com/airbytehq/airbyte/pull/58320) | Update dependencies |
| 1.0.2 | 2025-04-12 | [57774](https://github.com/airbytehq/airbyte/pull/57774) | Update dependencies |
| 1.0.1 | 2025-04-05 | [57269](https://github.com/airbytehq/airbyte/pull/57269) | Update dependencies |
| 1.0.0 | 2025-04-01 | [55876](https://github.com/airbytehq/airbyte/pull/55876) | Migrate API to V2 |
| 0.3.16 | 2025-03-29 | [56506](https://github.com/airbytehq/airbyte/pull/56506) | Update dependencies |
| 0.3.15 | 2025-03-22 | [55966](https://github.com/airbytehq/airbyte/pull/55966) | Update dependencies |
| 0.3.14 | 2025-03-08 | [55335](https://github.com/airbytehq/airbyte/pull/55335) | Update dependencies |
| 0.3.13 | 2025-03-01 | [54978](https://github.com/airbytehq/airbyte/pull/54978) | Update dependencies |
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
| 0.2.6 | 2024-06-15 | [39495](https://github.com/airbytehq/airbyte/pull/39495) | Fix parameters as comma separated single string |
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
