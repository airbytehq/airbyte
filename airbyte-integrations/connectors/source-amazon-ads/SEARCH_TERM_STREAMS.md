# Adding Search Term Report Streams to the Amazon Ads Connector

This document explains the two new search term report streams added to the MarketLeap fork of the Airbyte Amazon Ads connector, why they were added, what they return, and how to deploy them.

---

## Why these streams were added

The official Airbyte Amazon Ads connector does **not** include search term reports. Search term data is critical for MarketLeap because it tells us:

- Which **actual search queries** shoppers typed before clicking an ad
- Which keywords are matching which real search terms (match type analysis)
- Which search terms are converting vs burning spend (ACOS/ROAS per search term)
- Negative keyword opportunities (search terms with high spend, zero conversions)

Without search term data, you only know a keyword spent money - not *why*.

---

## What was added

Two new streams in `manifest.yaml`:

| Stream name | Amazon report type | Ad product | Granularity |
|-------------|-------------------|------------|-------------|
| `sponsored_products_search_term_report_stream` | `spSearchTerm` | Sponsored Products | Daily |
| `sponsored_brands_search_term_report_stream` | `sbSearchTerm` | Sponsored Brands | Daily |

Both streams:
- Are **incremental** (cursor on `date` field, 3-day lookback for attribution updates)
- Run per **profile** (one Amazon marketplace account)
- Use the same async create → poll → download pattern as all other report streams
- Are registered in the `streams:` list and have schemas in the `schemas:` section

---

## What data each stream returns

### `sponsored_products_search_term_report_stream`

One row per `date + searchTerm + keyword + adGroup + campaign + profile`.

| Column | Type | Description |
|--------|------|-------------|
| `date` | string | Date of the data (YYYY-MM-DD) |
| `profileId` | integer | Amazon Ads profile (marketplace account) |
| `campaignId` / `campaignName` | integer / string | Campaign |
| `campaignStatus` | string | ENABLED, PAUSED, ARCHIVED |
| `campaignBudgetAmount` | number | Daily budget |
| `campaignBudgetCurrencyCode` | string | e.g. GBP, EUR |
| `campaignBudgetType` | string | DAILY |
| `portfolioId` | integer | Portfolio grouping |
| `adGroupId` / `adGroupName` | integer / string | Ad group |
| `keyword` | string | The keyword that triggered the ad |
| `keywordId` | integer | Keyword ID |
| `matchType` | string | BROAD, PHRASE, EXACT |
| `targeting` | string | Auto-targeting expression (if applicable) |
| `searchTerm` | string | The actual query the shopper typed |
| `impressions` | integer | Times the ad was shown |
| `clicks` | integer | Times the ad was clicked |
| `clickThroughRate` | number | clicks / impressions |
| `costPerClick` | number | Average CPC |
| `cost` | number | Total spend |
| `purchases7d` | integer | Orders within 7 days of click |
| `sales7d` | number | Revenue within 7 days of click |
| `unitsSoldClicks7d` | integer | Units sold within 7 days |
| `acosClicks7d` | number | ACOS (cost / sales7d) |
| `roasClicks7d` | number | ROAS (sales7d / cost) |
| `purchasesSameSku7d` | integer | Orders of the exact advertised SKU |
| `reportDate` | string | Added by transformer — sync interval end date |

---

### `sponsored_brands_search_term_report_stream`

One row per `date + searchTerm + keyword + adGroup + campaign + profile`.

| Column | Type | Description |
|--------|------|-------------|
| `date` | string | Date (YYYY-MM-DD) |
| `startDate` | string | Campaign start date |
| `endDate` | string | Campaign end date |
| `profileId` | integer | Marketplace account |
| `campaignId` / `campaignName` | integer / string | Campaign |
| `campaignStatus` | string | ENABLED, PAUSED, ARCHIVED |
| `campaignBudgetAmount` | number | Daily budget |
| `campaignBudgetCurrencyCode` | string | e.g. GBP, EUR |
| `campaignBudgetType` | string | DAILY |
| `adGroupId` / `adGroupName` | integer / string | Ad group |
| `keywordId` | integer | Keyword ID |
| `keywordText` | string | The keyword that triggered the ad |
| `keywordBid` | number | Bid on the keyword |
| `matchType` | string | BROAD, PHRASE, EXACT |
| `costType` | string | CPC or VCPM |
| `searchTerm` | string | The actual query the shopper typed |
| `impressions` | integer | Times the ad was shown |
| `viewableImpressions` | integer | Viewable impressions |
| `viewabilityRate` | number | Viewable impressions / total impressions |
| `clicks` | integer | Times the ad was clicked |
| `viewClickThroughRate` | number | vCTR (clicks / viewable impressions) |
| `cost` | number | Total spend |
| `purchases` | integer | Total orders |
| `purchasesClicks` | integer | Click-attributed orders |
| `sales` | number | Total revenue |
| `salesClicks` | number | Click-attributed revenue |
| `unitsSold` | integer | Total units sold |
| `addToList` | integer | Add-to-wishlist events |
| `addToListFromClicks` | integer | Click-attributed add-to-wishlist |
| `qualifiedBorrows` | integer | Kindle Unlimited borrows |
| `qualifiedBorrowsFromClicks` | integer | Click-attributed KU borrows |
| `royaltyQualifiedBorrows` | integer | KU borrows generating royalties |
| `royaltyQualifiedBorrowsFromClicks` | integer | Click-attributed royalty KU borrows |
| `kindleEditionNormalizedPagesRead14d` | number | KENP read within 14 days |
| `kindleEditionNormalizedPagesRoyalties14d` | number | KENP royalties within 14 days |
| `video5SecondViewRate` | number | % viewers who watched 5+ seconds |
| `video5SecondViews` | integer | Views of 5+ seconds |
| `videoCompleteViews` | integer | Complete video views |
| `videoFirstQuartileViews` | integer | Views reaching 25% of video |
| `videoMidpointViews` | integer | Views reaching 50% of video |
| `videoThirdQuartileViews` | integer | Views reaching 75% of video |
| `videoUnmutes` | integer | Times viewer unmuted the video |
| `reportDate` | string | Added by transformer — sync interval end date |

**Key differences vs SP:** SB has no `portfolioId`, no `targeting`, no ACOS/ROAS columns (calculate client-side: `cost / NULLIF(salesClicks, 0)`), uses `viewableImpressions` + `viewClickThroughRate` instead of standard CTR, and includes video + Kindle Unlimited metrics not present in SP.

---

## Files changed

```
airbyte-integrations/connectors/source-amazon-ads/
  manifest.yaml     ← stream definitions, registrations, schemas added
  metadata.yaml     ← version bumped 8.0.4 → 8.1.0
  SEARCH_TERM_STREAMS.md  ← this file

docs/integrations/sources/amazon-ads.md  ← changelog entry added
```

---

## How to deploy to your local Airbyte instance

### Option A — Connector Builder UI (recommended for local dev)

1. Copy the manifest to clipboard:
   ```bash
   pbcopy < ~/w/mlc-airbyte/airbyte-integrations/connectors/source-amazon-ads/manifest.yaml
   ```

2. Open Airbyte UI → **Builder** → click **Amazon Ads** (the MarketLeap custom connector)

3. Top-left toggle → switch to **YAML view**

4. `Cmd+A` → `Cmd+V` to replace all content

5. Click **Publish** (top-right)

6. Go to your connection → **Schema** tab → confirm both search-term streams are enabled

### Option B — Airbyte API (for automation / CI)

```bash
# get your connector definition ID
curl -s http://localhost:8000/api/v1/source_definitions/list_for_workspace \
  -H "Content-Type: application/json" \
  -d '{"workspaceId": "<your-workspace-id>"}' \
  | jq '.sourceDefinitions[] | select(.name | contains("Amazon Ads"))'

# update the connector with the new manifest
# (use the Connector Builder API or re-publish via UI)
```

---

## How to configure the source

When creating an Amazon Ads source in Airbyte, set these fields to avoid throttling:

| Field | Recommended value | Why |
|-------|------------------|-----|
| `Number of concurrent threads` | `2` | Reduces 429 errors from Amazon |
| `Max concurrent report jobs` | `1` | Serializes report creation — Amazon throttles heavily on concurrent async reports |
| `Look Back Window` | `3` | Re-fetches last 3 days to capture late attribution updates |
| `Start Date` | `YYYY-MM-DD` (60 days max) | Amazon only allows reports up to 60 days in the past |

---

## Data flow for MarketLeap

```
Amazon Ads API (per brand/profile)
    ↓  Airbyte sync (one-time on brand onboarding, or daily)
S3: s3://airbyte-plain-s3/amazon/{brand_id}/
    raw JSONL — _airbyte_data column contains full JSON record
    ↓  Glue Crawler → Glue Catalog
    ↓  Redshift Spectrum (external schema)
    ↓  dbt (flatten _airbyte_data JSON + dedup + transform)
Redshift: sp_search_term, sb_search_term tables
    ↓
BI / Analytics
```

### Deduplication note

Both streams have a **3-day lookback** — each incremental sync re-fetches the last 3 days to capture late-attributed conversions. This means duplicate rows appear in S3 for the lookback window. Dedup happens in the dbt layer using the primary key:

- **SP:** `profileId + date + campaignId + adGroupId + keywordId + searchTerm`
- **SB:** `profileId + date + campaignId + adGroupId + searchTerm`

### Parsing `_airbyte_data` in Redshift

The S3 V2 destination writes a JSON blob per row in `_airbyte_data`. Use `json_extract_path_text()` in Redshift:

```sql
-- example: flatten SP search term raw data
SELECT
  json_extract_path_text(_airbyte_data, 'date')        AS date,
  json_extract_path_text(_airbyte_data, 'profileId')   AS profile_id,
  json_extract_path_text(_airbyte_data, 'searchTerm')  AS search_term,
  json_extract_path_text(_airbyte_data, 'cost')::float AS cost,
  json_extract_path_text(_airbyte_data, 'sales7d')::float AS sales_7d,
  json_extract_path_text(_airbyte_data, 'acosClicks7d')::float AS acos
FROM sponsored_products_search_term_report_stream
```

---

## Known issues / gotchas

### 1. Amazon Ads 429 throttling
Report creation gets throttled when too many reports run concurrently. Set `Max concurrent report jobs = 1` in the source config. The connector retries automatically but will fail after 6 attempts if sustained.

### 2. S3 V2 destination — instance role credentials
The S3 V2 destination connector uses the AWS Kotlin SDK, which fails to resolve instance-role credentials via IMDS when running inside Kubernetes (abctl/Kind). Use **explicit Access Key + Secret Key** in the S3 destination config instead of relying on the instance role. The S3 Data Lake destination (Java SDK) works with instance role — this is SDK-specific.

### 3. No `sdSearchTerm` stream
Sponsored Display does not have a search term report — SD targets audiences and product pages, not keywords. There is no `sdSearchTerm` report type in the Amazon Ads API.

### 4. SB primary key includes `keywordId`
Both SP and SB search term reports return `keywordId`. The primary key for both streams is `profileId + date + campaignId + adGroupId + keywordId + searchTerm`. Joins between SP and SB on `keywordId` are valid.

### 5. ACOS / ROAS not available in SB
The SB search term report does not return `acosClicks7d` or `roasClicks7d`. Calculate these client-side in dbt:
```sql
cost / NULLIF(salesClicks, 0)        AS acos,
salesClicks / NULLIF(cost, 0)        AS roas
```

---

## Running unit tests

```bash
cd ~/w/mlc-airbyte/airbyte-integrations/connectors/source-amazon-ads/unit_tests
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
poetry install --no-root
poetry run pytest -v
# Expected: 61 passed
```

---

## Branch

`feat/add-search-term-reports` on `MarketLeap-tech/mlc-airbyte`

Commit: `feat(amazon-ads): add SP and SB search term report streams`
