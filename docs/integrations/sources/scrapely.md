# Scrape.ly

This page contains the setup guide and reference information for the [Scrape.ly](https://scrape.ly) source connector.

Scrape.ly is a web scraping platform: ready-made scrapers (Actors) run in the cloud and store what they scrape in datasets. This connector syncs the results of your Actors' runs, or of datasets you choose, together with your runs, datasets and Actors.

## Prerequisites

- A Scrape.ly account. The free plan includes monthly credit.
- A Scrape.ly API key

## Setup guide

### Step 1: Create an API key

1. Sign up or log in at [scrape.ly](https://scrape.ly).
2. In the dashboard, open **Settings → API & Integrations** and create an API key. For a read-only key, give it the `runs:read`, `datasets:read` and `actors:read` permissions.

### Step 2: Set up the Scrape.ly connector in Airbyte

1. In Airbyte, go to **Sources** and click **New source**.
2. Search for and select **Scrape.ly**.
3. Enter your **API key**.
4. Optional: enter **Actors** (as `username/actor-name` or an Actor ID) to fill the `actor_results` stream with the results of their runs, and **Dataset IDs** to fill the `dataset_items` stream. Leave either list empty to skip that stream.
5. Optional: enter a **Start date** to skip runs started before it.
6. Click **Set up source**. Airbyte checks the key by listing your runs.

## Supported sync modes

| Stream          | Full Refresh | Incremental |
| :-------------- | :----------- | :---------- |
| `actor_runs`    | Yes          | Yes         |
| `actor_results` | Yes          | Yes         |
| `dataset_items` | Yes          | No          |
| `runs`          | Yes          | Yes         |
| `datasets`      | Yes          | No          |
| `actors`        | Yes          | No          |

## Supported streams

| Stream          | Endpoint                                                              | Primary key | Description                                                                                                     |
| :-------------- | :-------------------------------------------------------------------- | :---------- | :-------------------------------------------------------------------------------------------------------------- |
| `actor_runs`    | `GET /v2/actors/{id}/runs`                                            | `id`        | The succeeded runs of the configured Actors. Incremental on `finishedAt`.                                       |
| `actor_results` | `GET /v2/datasets/{id}/items` for each run in `actor_runs`            | none        | The results of every succeeded run of the configured Actors. Incremental on the run's finish time.              |
| `dataset_items` | `GET /v2/datasets/{id}/items`                                         | none        | The results stored in each configured dataset.                                                                  |
| `runs`          | `GET /v2/actor-runs`                                                  | `id`        | Your Actor runs: status, timings, cost and their default dataset. Incremental on `startedAt`.                   |
| `datasets`      | `GET /v2/datasets`                                                    | `id`        | Your datasets and their item counts.                                                                            |
| `actors`        | `GET /v2/acts`                                                        | `id`        | Your Actors.                                                                                                    |

### Notes on streams

- `actor_results` and `dataset_items` records are whatever the Actor scraped, so their fields differ per Actor. Each record also carries `_scrapely_dataset_id`; `actor_results` records carry `_scrapely_run_id` and `_scrapely_run_finished_at` as well.
- Incremental syncs of `runs`, `actor_runs` and `actor_results` re-read the most recent run. Use **Incremental | Append + Deduped** for `runs` and `actor_runs`. Scraped results have no primary key, so for `actor_results` deduplicate on `_scrapely_run_id` downstream if you need to.
- `runs` is incremental on `startedAt`, so a run's later status changes are not picked up; use **Full Refresh | Overwrite** for `runs` to keep statuses current.
- Only succeeded runs are synced into `actor_runs` and `actor_results`. They are tracked by finish time, so a run that is still going is picked up by a later sync once it succeeds.

## Performance considerations

The Scrape.ly API allows 1,000 requests per minute per account, and 5,000 per minute for dataset reads. The connector pages through results 1,000 at a time and retries on HTTP 429 and 5xx responses with exponential backoff.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 0.1.0   | 2026-10-29 | [PR_NUMBER](https://github.com/airbytehq/airbyte/pull/PR_NUMBER) | Initial release |

</details>
