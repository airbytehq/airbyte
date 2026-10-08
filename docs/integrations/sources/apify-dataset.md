---
description: Web scraping and automation platform.
---

# Apify Dataset

[Apify](https://apify.com/) is a web scraping and web automation platform. It provides ready-made and custom scrapers (called Actors), open-source [JavaScript](https://docs.apify.com/sdk/js/) and [Python](https://docs.apify.com/sdk/python/) SDKs, proxies, and other tools for running web automation jobs at scale.

This connector reads [Apify datasets](https://docs.apify.com/platform/storage/dataset), where scraping jobs usually store their results, through the [Apify API v2](https://docs.apify.com/api/v2) and syncs them to your destination.

## Prerequisites

- An Apify account
- Your Apify personal API token
- The ID of the dataset you want to sync

## Set up the connector

<FieldAnchor field="token">

**API token**: In Apify Console, copy your personal API token from [**Settings** > **Integrations**](https://console.apify.com/account/integrations). For details, see [API token](https://docs.apify.com/platform/integrations/api#api-token) in the Apify documentation.

</FieldAnchor>

<FieldAnchor field="dataset_id">

**Dataset ID**: In Apify Console, find the dataset ID under [**Storage** > **Datasets**](https://console.apify.com/storage/datasets).

</FieldAnchor>

### Trigger an Airbyte sync from an Apify webhook

When an [Actor run](https://docs.apify.com/platform/actors/running) finishes, it can start an Airbyte sync. Create an Apify [webhook](https://docs.apify.com/platform/integrations/webhooks) that fires when the run succeeds and calls the Airbyte API endpoint that [triggers a sync job](https://reference.airbyte.com/reference/createjob) for your connection.

![Apify webhook configured to trigger an Airbyte connection sync](/.gitbook/assets/apify_trigger_airbyte_connection.png)

## Supported sync modes

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

None of the streams have a cursor, so every sync reads the full result set again.

## Streams

| Stream                                    | Endpoint                                                                                   | Primary key |
| :---------------------------------------- | :----------------------------------------------------------------------------------------- | :---------- |
| `dataset_collection`                      | [`GET /v2/datasets`](https://docs.apify.com/api/v2/datasets-get)                           | `id`        |
| `dataset`                                 | [`GET /v2/datasets/{datasetId}`](https://docs.apify.com/api/v2/dataset-get)                | `id`        |
| `item_collection`                         | [`GET /v2/datasets/{datasetId}/items`](https://docs.apify.com/api/v2/dataset-items-get)    | None        |
| `item_collection_website_content_crawler` | [`GET /v2/datasets/{datasetId}/items`](https://docs.apify.com/api/v2/dataset-items-get)    | None        |

### `dataset_collection`

Lists the datasets your API token can access. This stream doesn't use the dataset ID from your configuration.

The Apify API returns only named datasets by default, and the connector doesn't request unnamed ones. The default dataset that each Actor run creates is unnamed, so it doesn't appear in this stream unless you [name it](https://docs.apify.com/platform/storage/usage#named-and-unnamed-storages). The `dataset`, `item_collection`, and `item_collection_website_content_crawler` streams work with any dataset ID, named or unnamed.

### `dataset`

Returns the metadata of the dataset you configured, such as its name, item count, and creation time.

### `item_collection`

Returns every item in the configured dataset. Because item shapes depend on the Actor that produced them, the connector wraps each item in a single `data` object instead of declaring a fixed schema. This lets the stream work with datasets from any Actor, but your destination receives each item's fields nested inside `data` rather than as separate columns.

The connector doesn't request cleaned output, so items include [hidden fields](https://docs.apify.com/api/v2/dataset-items-get) (top-level fields whose names start with `#`).

Limitations:

- Empty items (`{}`) are skipped.
- Since version 2.2.62, each item must be a JSON object. If the dataset contains non-object items, such as numbers or strings, the sync fails with a `TypeError`.
- Since version 2.2.62, if an item is nested more than 200 levels deep, or contains a number outside the 64-bit float range (for example, `1e400`) or `NaN`/`Infinity`, the connector sets `data` to a string representation of the item instead of an object.
- Since version 2.2.62, if an item has a top-level `__airbyte_apify_wrapped_item` key, the contents of that key are merged into the top level of the record next to `data`.

### `item_collection_website_content_crawler`

Reads the same endpoint as `item_collection`, but uses a fixed schema that matches the output of the [Website Content Crawler](https://apify.com/apify/website-content-crawler) Actor. Use this stream only for datasets that Website Content Crawler produced. For datasets from other Actors, use `item_collection`.

## Rate limits

All streams page through results 50 records at a time. Apify applies a [global rate limit](https://docs.apify.com/api/v2#rate-limiting) of 250,000 requests per minute per user and a default limit of 60 requests per second per resource, such as a single dataset. When Apify returns HTTP 429, the connector retries the request with exponential backoff.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                 | Subject                                                                         |
| :------ | :--------- | :----------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 2.2.62 | 2026-10-08 | [88134](https://github.com/airbytehq/airbyte/pull/88134) | Replace the custom `item_collection` record extractor with built-in declarative transformations; record output is unchanged except for the edge cases listed under `item_collection` |
| 2.2.61 | 2026-10-06 | [87770](https://github.com/airbytehq/airbyte/pull/87770) | Update dependencies |
| 2.2.60 | 2026-09-29 | [87064](https://github.com/airbytehq/airbyte/pull/87064) | Update dependencies |
| 2.2.59 | 2026-09-22 | [86526](https://github.com/airbytehq/airbyte/pull/86526) | Update dependencies |
| 2.2.58 | 2026-09-15 | [85955](https://github.com/airbytehq/airbyte/pull/85955) | Update dependencies |
| 2.2.57 | 2026-09-08 | [84487](https://github.com/airbytehq/airbyte/pull/84487) | Update dependencies |
| 2.2.56 | 2026-08-11 | [83850](https://github.com/airbytehq/airbyte/pull/83850) | Update dependencies |
| 2.2.55 | 2026-07-28 | [83194](https://github.com/airbytehq/airbyte/pull/83194) | Update to CDK 7.23.8 (fixes AirbyteCustomCodeNotPermittedError for bundled custom components) and remove the temporary Cloud version override |
| 2.2.54 | 2026-07-28 | [1082](https://github.com/airbytehq/airbyte-python-cdk/issues/1082) | Roll Cloud back to 2.2.52 — 2.2.53 is built on SDM 7.23.7, which breaks bundled custom components |
| 2.2.53 | 2026-07-28 | [82834](https://github.com/airbytehq/airbyte/pull/82834) | Update dependencies |
| 2.2.52 | 2026-07-21 | [82336](https://github.com/airbytehq/airbyte/pull/82336) | Update dependencies |
| 2.2.51 | 2026-07-14 | [81739](https://github.com/airbytehq/airbyte/pull/81739) | Update dependencies |
| 2.2.50 | 2026-06-30 | [80961](https://github.com/airbytehq/airbyte/pull/80961) | Update dependencies |
| 2.2.49 | 2026-06-23 | [80380](https://github.com/airbytehq/airbyte/pull/80380) | Update dependencies |
| 2.2.48 | 2026-06-16 | [79760](https://github.com/airbytehq/airbyte/pull/79760) | Update dependencies |
| 2.2.47 | 2026-06-09 | [79203](https://github.com/airbytehq/airbyte/pull/79203) | Update dependencies |
| 2.2.46 | 2026-06-02 | [78578](https://github.com/airbytehq/airbyte/pull/78578) | Update dependencies |
| 2.2.45 | 2026-04-28 | [77189](https://github.com/airbytehq/airbyte/pull/77189) | Update dependencies |
| 2.2.44 | 2026-04-21 | [76502](https://github.com/airbytehq/airbyte/pull/76502) | Update dependencies |
| 2.2.43 | 2026-03-31 | [75895](https://github.com/airbytehq/airbyte/pull/75895) | Update dependencies |
| 2.2.42 | 2026-03-17 | [75003](https://github.com/airbytehq/airbyte/pull/75003) | Update dependencies |
| 2.2.41 | 2026-03-10 | [74482](https://github.com/airbytehq/airbyte/pull/74482) | Update dependencies |
| 2.2.40 | 2026-02-24 | [73807](https://github.com/airbytehq/airbyte/pull/73807) | Update dependencies |
| 2.2.39 | 2026-02-03 | [72687](https://github.com/airbytehq/airbyte/pull/72687) | Update dependencies |
| 2.2.38 | 2026-01-20 | [71876](https://github.com/airbytehq/airbyte/pull/71876) | Update dependencies |
| 2.2.37 | 2026-01-14 | [71443](https://github.com/airbytehq/airbyte/pull/71443) | Update dependencies |
| 2.2.36 | 2026-01-08 | [71099](https://github.com/airbytehq/airbyte/pull/71099) | Update logo |
| 2.2.35 | 2025-12-18 | [70793](https://github.com/airbytehq/airbyte/pull/70793) | Update dependencies |
| 2.2.34 | 2025-11-25 | [69867](https://github.com/airbytehq/airbyte/pull/69867) | Update dependencies |
| 2.2.33 | 2025-11-18 | [69519](https://github.com/airbytehq/airbyte/pull/69519) | Update dependencies |
| 2.2.32 | 2025-11-04 | [68843](https://github.com/airbytehq/airbyte/pull/68843) | Update dependencies |
| 2.2.31 | 2025-10-21 | [68364](https://github.com/airbytehq/airbyte/pull/68364) | Update dependencies |
| 2.2.30 | 2025-10-14 | [67997](https://github.com/airbytehq/airbyte/pull/67997) | Update dependencies |
| 2.2.29 | 2025-10-07 | [67163](https://github.com/airbytehq/airbyte/pull/67163) | Update dependencies |
| 2.2.28 | 2025-09-30 | [66273](https://github.com/airbytehq/airbyte/pull/66273) | Update dependencies |
| 2.2.27 | 2025-08-09 | [64655](https://github.com/airbytehq/airbyte/pull/64655) | Update dependencies |
| 2.2.26 | 2025-08-02 | [64432](https://github.com/airbytehq/airbyte/pull/64432) | Update dependencies |
| 2.2.25 | 2025-07-26 | [63802](https://github.com/airbytehq/airbyte/pull/63802) | Update dependencies |
| 2.2.24 | 2025-07-05 | [62540](https://github.com/airbytehq/airbyte/pull/62540) | Update dependencies |
| 2.2.23 | 2025-06-28 | [62139](https://github.com/airbytehq/airbyte/pull/62139) | Update dependencies |
| 2.2.22 | 2025-06-15 | [61108](https://github.com/airbytehq/airbyte/pull/61108) | Update dependencies |
| 2.2.21 | 2025-05-17 | [60677](https://github.com/airbytehq/airbyte/pull/60677) | Update dependencies |
| 2.2.20 | 2025-05-10 | [59857](https://github.com/airbytehq/airbyte/pull/59857) | Update dependencies |
| 2.2.19 | 2025-05-03 | [59312](https://github.com/airbytehq/airbyte/pull/59312) | Update dependencies |
| 2.2.18 | 2025-04-26 | [58251](https://github.com/airbytehq/airbyte/pull/58251) | Update dependencies |
| 2.2.17 | 2025-04-12 | [57599](https://github.com/airbytehq/airbyte/pull/57599) | Update dependencies |
| 2.2.16 | 2025-04-05 | [57134](https://github.com/airbytehq/airbyte/pull/57134) | Update dependencies |
| 2.2.15 | 2025-03-29 | [56579](https://github.com/airbytehq/airbyte/pull/56579) | Update dependencies |
| 2.2.14 | 2025-03-22 | [56107](https://github.com/airbytehq/airbyte/pull/56107) | Update dependencies |
| 2.2.13 | 2025-03-08 | [55423](https://github.com/airbytehq/airbyte/pull/55423) | Update dependencies |
| 2.2.12 | 2025-03-01 | [54885](https://github.com/airbytehq/airbyte/pull/54885) | Update dependencies |
| 2.2.11 | 2025-02-22 | [54235](https://github.com/airbytehq/airbyte/pull/54235) | Update dependencies |
| 2.2.10 | 2025-02-15 | [53872](https://github.com/airbytehq/airbyte/pull/53872) | Update dependencies |
| 2.2.9 | 2025-02-08 | [53440](https://github.com/airbytehq/airbyte/pull/53440) | Update dependencies |
| 2.2.8 | 2025-02-01 | [52904](https://github.com/airbytehq/airbyte/pull/52904) | Update dependencies |
| 2.2.7 | 2025-01-25 | [52208](https://github.com/airbytehq/airbyte/pull/52208) | Update dependencies |
| 2.2.6 | 2025-01-18 | [51740](https://github.com/airbytehq/airbyte/pull/51740) | Update dependencies |
| 2.2.5 | 2025-01-11 | [51257](https://github.com/airbytehq/airbyte/pull/51257) | Update dependencies |
| 2.2.4 | 2024-12-28 | [50468](https://github.com/airbytehq/airbyte/pull/50468) | Update dependencies |
| 2.2.3 | 2024-12-21 | [50217](https://github.com/airbytehq/airbyte/pull/50217) | Update dependencies |
| 2.2.2 | 2024-12-14 | [49553](https://github.com/airbytehq/airbyte/pull/49553) | Update dependencies |
| 2.2.1 | 2024-12-12 | [48216](https://github.com/airbytehq/airbyte/pull/48216) | Update dependencies |
| 2.2.0 | 2024-10-29 | [47286](https://github.com/airbytehq/airbyte/pull/47286) | Migrate to manifest only format |
| 2.1.27 | 2024-10-29 | [47068](https://github.com/airbytehq/airbyte/pull/47068) | Update dependencies |
| 2.1.26 | 2024-10-12 | [46837](https://github.com/airbytehq/airbyte/pull/46837) | Update dependencies |
| 2.1.25 | 2024-10-01 | [46373](https://github.com/airbytehq/airbyte/pull/46373) | add user-agent header to be able to track Airbyte integration on Apify |
| 2.1.24 | 2024-10-05 | [46430](https://github.com/airbytehq/airbyte/pull/46430) | Update dependencies |
| 2.1.23 | 2024-09-28 | [46146](https://github.com/airbytehq/airbyte/pull/46146) | Update dependencies |
| 2.1.22 | 2024-09-21 | [45820](https://github.com/airbytehq/airbyte/pull/45820) | Update dependencies |
| 2.1.21 | 2024-09-14 | [45479](https://github.com/airbytehq/airbyte/pull/45479) | Update dependencies |
| 2.1.20 | 2024-09-07 | [45252](https://github.com/airbytehq/airbyte/pull/45252) | Update dependencies |
| 2.1.19 | 2024-08-31 | [44962](https://github.com/airbytehq/airbyte/pull/44962) | Update dependencies |
| 2.1.18 | 2024-08-24 | [44734](https://github.com/airbytehq/airbyte/pull/44734) | Update dependencies |
| 2.1.17 | 2024-08-17 | [44204](https://github.com/airbytehq/airbyte/pull/44204) | Update dependencies |
| 2.1.16 | 2024-08-10 | [43607](https://github.com/airbytehq/airbyte/pull/43607) | Update dependencies |
| 2.1.15 | 2024-08-03 | [43071](https://github.com/airbytehq/airbyte/pull/43071) | Update dependencies |
| 2.1.14 | 2024-07-27 | [42627](https://github.com/airbytehq/airbyte/pull/42627) | Update dependencies |
| 2.1.13 | 2024-07-20 | [42364](https://github.com/airbytehq/airbyte/pull/42364) | Update dependencies |
| 2.1.12 | 2024-07-13 | [41893](https://github.com/airbytehq/airbyte/pull/41893) | Update dependencies |
| 2.1.11 | 2024-07-10 | [41344](https://github.com/airbytehq/airbyte/pull/41344) | Update dependencies |
| 2.1.10 | 2024-07-09 | [41189](https://github.com/airbytehq/airbyte/pull/41189) | Update dependencies |
| 2.1.9 | 2024-07-06 | [40813](https://github.com/airbytehq/airbyte/pull/40813) | Update dependencies |
| 2.1.8 | 2024-06-25 | [40411](https://github.com/airbytehq/airbyte/pull/40411) | Update dependencies |
| 2.1.7 | 2024-06-22 | [40187](https://github.com/airbytehq/airbyte/pull/40187) | Update dependencies |
| 2.1.6 | 2024-06-04 | [39010](https://github.com/airbytehq/airbyte/pull/39010) | [autopull] Upgrade base image to v1.2.1 |
| 2.1.5 | 2024-04-19 | [37115](https://github.com/airbytehq/airbyte/pull/37115) | Updating to 0.80.0 CDK |
| 2.1.4 | 2024-04-18 | [37115](https://github.com/airbytehq/airbyte/pull/37115) | Manage dependencies with Poetry. |
| 2.1.3 | 2024-04-15 | [37115](https://github.com/airbytehq/airbyte/pull/37115) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 2.1.2 | 2024-04-12 | [37115](https://github.com/airbytehq/airbyte/pull/37115) | schema descriptions |
| 2.1.1 | 2023-12-14 | [33414](https://github.com/airbytehq/airbyte/pull/33414) | Prepare for airbyte-lib |
| 2.1.0 | 2023-10-13 | [31333](https://github.com/airbytehq/airbyte/pull/31333) | Add stream for arbitrary datasets |
| 2.0.0 | 2023-09-18 | [30428](https://github.com/airbytehq/airbyte/pull/30428) | Fix broken stream, manifest refactor |
| 1.0.0 | 2023-08-25 | [29859](https://github.com/airbytehq/airbyte/pull/29859) | Migrate to lowcode |
| 0.2.0 | 2022-06-20 | [28290](https://github.com/airbytehq/airbyte/pull/28290) | Make connector work with platform changes not syncing empty stream schemas. |
| 0.1.11 | 2022-04-27 | [12397](https://github.com/airbytehq/airbyte/pull/12397) | No changes. Used connector to test publish workflow changes. |
| 0.1.9   | 2022-04-05 | [PR\#11712](https://github.com/airbytehq/airbyte/pull/11712) | No changes from 0.1.4. Used connector to test publish workflow changes.         |
| 0.1.4   | 2021-12-23 | [PR\#8434](https://github.com/airbytehq/airbyte/pull/8434)   | Update fields in source-connectors specifications                               |
| 0.1.2   | 2021-11-08 | [PR\#7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                 |
| 0.1.0   | 2021-07-29 | [PR\#5069](https://github.com/airbytehq/airbyte/pull/5069)   | Initial version of the connector                                                |

</details>
