# Workable

This page guides you through the process of setting up the Workable source connector. The connector syncs jobs, candidates, pipeline stages, and external recruiters from the [Workable API](https://workable.readme.io/reference/generate-an-access-token).

## Prerequisites

- A Workable account with permission to generate API access tokens.
- A Workable API access token with the `r_jobs` and `r_candidates` scopes. The `jobs`, `stages`, and `recruiters` streams require `r_jobs`, and the `candidates` stream requires `r_candidates`.
- Your Workable account subdomain. This is the `YOUR_SUBDOMAIN` part of `https://YOUR_SUBDOMAIN.workable.com`. You can also find it on the company profile settings page in Workable.

## Setup guide

### Step 1: Generate a Workable API access token

1. In Workable, open the drop-down menu in the top-right corner and select **Integrations**.
2. Click **Generate new token**.
3. Select the `r_jobs` and `r_candidates` scopes, then generate the token.
4. Copy the token and store it securely. Workable displays the token only once.

For more details, see Workable's guide to [generating an API access token](https://workable.readme.io/reference/generate-an-access-token#generate-an-api-access-token).

### Step 2: Set up the Workable connector in Airbyte

1. In Airbyte, go to **Sources** and click **New source**.
2. Search for and select **Workable**.
3. Enter a name for the source.
4. For **API Key**, enter the Workable API access token you generated in Step 1.
5. For **Account Subdomain**, enter your Workable account subdomain. Enter only the subdomain, for example `mycompany`, not the full URL.
6. For **Start Date**, enter the date from which to sync data, in the format `YYYYMMDDTHHMMSSZ`. For example, `20221115T225616Z`. The connector sends this value to Workable as the `created_after` parameter, so only jobs and candidates created after this date are synced.
7. Click **Set up source**.

## Supported sync modes

The Workable source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | Yes        |
| Namespaces        | No         |

## Supported streams

| Stream | Endpoint | Primary key | Required scope |
| :----- | :------- | :---------- | :------------- |
| [jobs](https://workable.readme.io/reference/jobs) | `/spi/v3/jobs` | `id` | `r_jobs` |
| [candidates](https://workable.readme.io/reference/job-candidates-index) | `/spi/v3/candidates` | `id` | `r_candidates` |
| [stages](https://workable.readme.io/reference/stages) | `/spi/v3/stages` | `slug` | `r_jobs` |
| [recruiters](https://workable.readme.io/reference/recruiters) | `/spi/v3/recruiters` | `id` | `r_jobs` |

## Limitations

- Workable limits account tokens to 10 requests every 10 seconds and returns HTTP 429 when you exceed this limit. See [Rate limiting](https://workable.readme.io/reference/rate-limits).
- The connector requests up to 100 records per page, which is the maximum the Workable API allows.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject              |
| :------ | :--------- | :------------------------------------------------------- | :------------------- |
| 0.2.18 | 2026-11-10 | [91459](https://github.com/airbytehq/airbyte/pull/91459) | Fix check and discover failing on page size option configuration; upgrade base image to `source-declarative-manifest:7.47.0` |
| 0.2.17 | 2026-06-02 | [79074](https://github.com/airbytehq/airbyte/pull/79074) | Update dependencies |
| 0.2.16 | 2025-05-24 | [60781](https://github.com/airbytehq/airbyte/pull/60781) | Update dependencies |
| 0.2.15 | 2025-05-10 | [59931](https://github.com/airbytehq/airbyte/pull/59931) | Update dependencies |
| 0.2.14 | 2025-05-04 | [58918](https://github.com/airbytehq/airbyte/pull/58918) | Update dependencies |
| 0.2.13 | 2025-04-19 | [58564](https://github.com/airbytehq/airbyte/pull/58564) | Update dependencies |
| 0.2.12 | 2025-04-12 | [58014](https://github.com/airbytehq/airbyte/pull/58014) | Update dependencies |
| 0.2.11 | 2025-04-05 | [57391](https://github.com/airbytehq/airbyte/pull/57391) | Update dependencies |
| 0.2.10 | 2025-03-29 | [56903](https://github.com/airbytehq/airbyte/pull/56903) | Update dependencies |
| 0.2.9 | 2025-03-22 | [56289](https://github.com/airbytehq/airbyte/pull/56289) | Update dependencies |
| 0.2.8 | 2025-03-08 | [55083](https://github.com/airbytehq/airbyte/pull/55083) | Update dependencies |
| 0.2.7 | 2025-02-22 | [54483](https://github.com/airbytehq/airbyte/pull/54483) | Update dependencies |
| 0.2.6 | 2025-02-15 | [54078](https://github.com/airbytehq/airbyte/pull/54078) | Update dependencies |
| 0.2.5 | 2025-02-08 | [53568](https://github.com/airbytehq/airbyte/pull/53568) | Update dependencies |
| 0.2.4 | 2025-02-01 | [53034](https://github.com/airbytehq/airbyte/pull/53034) | Update dependencies |
| 0.2.3 | 2025-01-25 | [52449](https://github.com/airbytehq/airbyte/pull/52449) | Update dependencies |
| 0.2.2 | 2025-01-18 | [47642](https://github.com/airbytehq/airbyte/pull/47642) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44044](https://github.com/airbytehq/airbyte/pull/44044) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43765](https://github.com/airbytehq/airbyte/pull/43765) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43520](https://github.com/airbytehq/airbyte/pull/43520) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43146](https://github.com/airbytehq/airbyte/pull/43146) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42772](https://github.com/airbytehq/airbyte/pull/42772) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42290](https://github.com/airbytehq/airbyte/pull/42290) | Update dependencies |
| 0.1.9 | 2024-07-16 | [38343](https://github.com/airbytehq/airbyte/pull/38343) | Make compatable with the builder |
| 0.1.8 | 2024-07-13 | [41916](https://github.com/airbytehq/airbyte/pull/41916) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41524](https://github.com/airbytehq/airbyte/pull/41524) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41091](https://github.com/airbytehq/airbyte/pull/41091) | Update dependencies |
| 0.1.5 | 2024-07-06 | [41012](https://github.com/airbytehq/airbyte/pull/41012) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40479](https://github.com/airbytehq/airbyte/pull/40479) | Update dependencies |
| 0.1.3 | 2024-06-22 | [39984](https://github.com/airbytehq/airbyte/pull/39984) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39268](https://github.com/airbytehq/airbyte/pull/39268) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38503](https://github.com/airbytehq/airbyte/pull/38503) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-15 | [18033](https://github.com/airbytehq/airbyte/pull/18033) | New Source: Workable |

</details>
