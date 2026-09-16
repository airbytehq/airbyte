# Klaviyo Migration Guide

## Upgrading to 3.0.0

This release changes the record shape of `flow_series_reports`, changes what `campaign_values_reports` writes in `date`, and changes the reporting periods both report streams request. Both streams need a schema refresh and a clear.

### What changed in `flow_series_reports`

The flow-series endpoint reports many days per response: it returns one `date_times` array plus, for each grouping, a statistics array whose values line up with that array by index. The connector used to emit one record per response, so each record carried whole arrays of daily values and a `date` copied from the end of the request window.

Now each response is split into one record per calendar day:

|                        | Before                                                                | After                                                       |
| ---------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------- |
| Records per grouping   | One per request window                                                | One per calendar day                                        |
| `statistics.opens`     | `[123, 156, 144]`                                                     | `144`                                                       |
| `date`                 | End of the request window, for example `2024-01-31T23:59:59+00:00`     | The day the row reports on, for example `2024-01-07T00:00:00+00:00` |

`groupings`, `flow_id`, `flow_message_id`, `send_channel` and `conversion_metric_id` are unchanged.

This is what makes the **Reporting Lookback Window (Days)** setting safe to use. The stream is keyed on `date` plus the grouping fields, so a day read again on a later sync arrives under the primary key it already had. On a destination that deduplicates on the primary key it replaces that row; in append mode each re-synced day adds an extra row per sync. Previously a re-read produced a new `date`, so the same days accumulated as extra rows and were counted twice however the destination was configured. Set the lookback to at least your Klaviyo attribution window - 5 days by default, up to 90 days if you have raised it - to pick up conversion revisions.

### What changed in `campaign_values_reports`

The fields are the same, but `date` now means something different. This endpoint has no per-day breakdown: one request answers with a single aggregate over the whole period, so `date` is what identifies the period a row covers. It used to be a timestamp inside the period - the moment the sync ran, for the period ending at that moment - and it is now the midnight that closes the period. A row dated `2024-06-15T00:00:00+00:00` covers everything up to the end of 2024-06-14.

That was not a cosmetic problem. The old value was a wall clock instant, and the next sync resumed from it, so it began requesting in the middle of a day the previous sync had already reported in full. The day on that boundary ended up inside two aggregates filed under two different `date` values, counted twice, with nothing for a destination to deduplicate. Periods now begin and end on day boundaries, so consecutive syncs tile the calendar: a sync that leaves the cursor at `2024-06-15T00:00:00+00:00` makes the next one ask for `2024-06-15` onwards and nothing earlier.

There is still deliberately no lookback window for this stream. Re-reading a period returns a fresh aggregate under a new `date`, which cannot replace an existing row and would only add a second one covering the same days.

### What changed in both streams

Report periods now cover whole calendar days and stop at the end of the last complete day.

- Klaviyo report timeframes are inclusive of both the first and the last day, and Klaviyo rounds the end up to `:59:59` of the hour it falls in. A period that stopped in the middle of a day therefore reported that whole day, and so did the following period. With a start date carrying a time of day - for example `2017-01-25T09:30:00Z` - every 30-day period boundary counted one day twice. Periods now start at midnight and end at `23:59:59`, so each day belongs to exactly one of them.
- These are whole days in your Klaviyo account's (company) timezone, not in UTC. Klaviyo documents that the timezone offset sent in a custom report timeframe is ignored and the company timezone configured for your account is used instead, even though the timestamps it returns carry a `+00:00` offset.
- The last period of a sync now ends at `23:59:59` on the previous day rather than at the moment the sync runs, so no period ever covers a partial day. The trade-off is freshness: the current day's numbers arrive with the next sync. For `campaign_values_reports` a second sync on the same day requests nothing at all, because no further day has completed.

Because period boundaries move, the periods `campaign_values_reports` has already written no longer line up with the periods it writes from now on.

### Migration steps

1. Back up the existing `flow_series_reports` and `campaign_values_reports` tables, or snapshot them into a copy. Step 4 deletes them, and refilling them means a full historical re-sync that can take days (see the warning below), so keep something to fall back on and to compare the new rows against.
2. Upgrade the connector to version 3.0.0.
3. In your connection, open the **Schema** tab and click **Refresh source schema**. Accept the changes for `flow_series_reports` and `campaign_values_reports`.
4. Clear both `flow_series_reports` and `campaign_values_reports` so they are re-read under the new record shape and the new period boundaries. Without this, old array-shaped rows and old reporting periods stay in your destination alongside the new ones.
5. Update any downstream models reading `flow_series_reports.statistics`. A field that was an array is now a single number, and there is one row per day instead of one row per sync window. Logic that used to unnest these arrays should now group by `date`.

:::warning
The re-sync after clearing reads your whole history again, one request per conversion metric per reporting period. Klaviyo's reporting endpoints are rate limited to 1 request per second in burst, 2 per minute sustained, and 225 per day ([see documentation](https://developers.klaviyo.com/en/reference/query_campaign_values)), so a full historical backfill can take several days and will spread across multiple syncs. Before clearing, restrict **Report Stream Conversion Metric IDs** to the metrics you actually need.
:::

Other streams are unaffected and do not need to be cleared.

## Upgrading to 2.0.0

Streams `campaigns`, `email_templates`, `events`, `flows`, `global_exclusions`, `lists`, and `metrics` are now pulling
data using latest API which has a different schema. Users will need to refresh the source schemas and reset these
streams after upgrading. See the chart below for the API version change.

| Stream            | Current API version | New API version |
|-------------------|---------------------|-----------------|
| campaigns         | v1                  | 2023-06-15      |
| email_templates   | v1                  | 2023-10-15      |
| events            | v1                  | 2023-10-15      |
| flows             | v1                  | 2023-10-15      |
| global_exclusions | v1                  | 2023-10-15      |
| lists             | v1                  | 2023-10-15      |
| metrics           | v1                  | 2023-10-15      |
| profiles          | 2023-02-22          | 2023-02-22      |

## Upgrading to 1.0.0

`event_properties/items/quantity` for `Events` stream is changed from `integer` to `number`.
For a smooth migration, data reset and schema refresh are needed.
