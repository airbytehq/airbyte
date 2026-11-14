# Datacircle

This page contains the setup guide and reference information for the Datacircle source connector.

[Datacircle](https://datacircle.dev) benchmarks the GTM APIs, such as LinkedIn profile, email finder, company data and web search APIs, and ranks every plan of each by its score out of 100.

The connector reads the open [Datacircle API](https://datacircle.dev/api) at `https://api.datacircle.dev/v1`: every API Datacircle benchmarks, who is best for each, every plan with its price and score, and one provider's ranks on each API it sells. For the calls and every field they return, see the [Datacircle API specification](https://api.datacircle.dev/v1/openapi.json).

## Prerequisites

None. The Datacircle API is open, with no API key and no account.

## Setup guide

### Set up the Datacircle connector in Airbyte

1. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
2. On the Set up the source page, select **Datacircle** from the Source type dropdown.
3. Enter a name for the Datacircle connector.
4. (Optional) Enter an **API** to sync one API only, by its name or its slug as the `apis` stream gives them, such as `linkedin-profile` or `email-finder`. The `plans` and `best_plans` streams then read that API's plans alone. Left empty, they read every API.
5. (Optional) Enter **Search words** to sync only the plans whose provider or plan name holds every one of these words, ignoring case and accents.
6. (Optional) Enter **Best plans per API**, from 1 to 50. The default is 10.
7. (Optional) Enter **Providers**, each by its slug: its name in lowercase letters and digits, the rest a hyphen, such as `bright-data` for Bright Data. Left empty, the `providers` stream reads none.
8. Click **Set up source**.

## Supported sync modes

The Datacircle source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

| Stream     | Endpoint                | Primary key     | Sync modes   | Notes                                                                                     |
| :--------- | :---------------------- | :-------------- | :----------- | :---------------------------------------------------------------------------------------- |
| apis       | `GET /apis`             | slug            | Full Refresh | Every API, with its number of plans and providers, its best plan and its pages             |
| best_plans | `GET /apis/{slug}/best` | api_slug, rank  | Full Refresh | Each API's plans best first by score, each with its rank. `api_slug` added to each record |
| plans      | `GET /plans`            | None            | Full Refresh | Every plan, best first, filtered by the API and the search words when set                 |
| providers  | `GET /providers/{slug}` | slug            | Full Refresh | Each configured provider's plans and rank on each API it sells                            |

A plan has no single key: one provider can sell the same plan name billed monthly and yearly, or for two calls of one API. Each plan record has its price per 1,000 calls (`perThousand`), its score out of 100 (`score`), its limits, the fields it returns and the pages it was read from.

## Performance considerations

The Datacircle API allows at most 60 calls a minute from one address. The connector keeps its requests under 55 a minute, and on a 429 waits for the time in the `Retry-After` header.

The `apis` stream takes one call. The `best_plans` stream takes one call per API, about 150 for every API, or one when **API** is set. The `plans` stream reads 50 plans a call: every plan of every API takes about 2,800 calls, close to an hour at the rate limit, so set **API** or **Search words** to sync a part of them faster. The `providers` stream takes one call per provider.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------- |
| 0.1.0   | 2026-11-13 | [92968](https://github.com/airbytehq/airbyte/pull/92968) | New source: Datacircle |

</details>
